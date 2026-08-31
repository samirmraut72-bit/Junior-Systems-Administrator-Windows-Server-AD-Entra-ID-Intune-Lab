import os

from datetime import datetime, timezone, timedelta
from functools import wraps

from dotenv import load_dotenv

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from sqlalchemy.pool import NullPool

from identity.flask import Auth as EntraAuth

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY"
)

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "SECRET_KEY is missing from .env"
    )


# =========================================================
# MICROSOFT ENTRA ID CONFIGURATION
# =========================================================

ENTRA_CLIENT_ID = os.getenv(
    "ENTRA_CLIENT_ID",
    "",
).strip()

ENTRA_TENANT_ID = os.getenv(
    "ENTRA_TENANT_ID",
    "",
).strip()

ENTRA_CLIENT_SECRET = os.getenv(
    "ENTRA_CLIENT_SECRET",
    "",
).strip()

ENTRA_REDIRECT_URI = os.getenv(
    "ENTRA_REDIRECT_URI",
    "http://localhost:5000/auth/callback",
).strip()

ENTRA_AUTHORITY = (
    f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}"
    if ENTRA_TENANT_ID
    else ""
)

ENTRA_CONFIGURED = all(
    [
        ENTRA_CLIENT_ID,
        ENTRA_TENANT_ID,
        ENTRA_CLIENT_SECRET,
        ENTRA_REDIRECT_URI,
    ]
)

# =========================================================
# DATABASE + SERVER-SIDE SESSION CONFIGURATION
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
).strip()

APP_ENV = os.getenv(
    "APP_ENV",
    "development",
).strip().lower()

IS_PRODUCTION = APP_ENV == "production"


# ---------------------------------------------------------
# NORMALISE POSTGRES CONNECTION STRING
# ---------------------------------------------------------

if DATABASE_URL.startswith(
    "postgres://"
):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1,
    )


# ---------------------------------------------------------
# PRODUCTION / HOSTED DATABASE
# ---------------------------------------------------------

if DATABASE_URL:

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = DATABASE_URL

    # Supabase transaction pooling already handles connection
    # pooling. NullPool avoids keeping process-local persistent
    # connections inside short-lived serverless functions.
    app.config[
        "SQLALCHEMY_ENGINE_OPTIONS"
    ] = {
        "poolclass": NullPool,
    }

    # Microsoft Identity uses Flask-Session. Store those
    # server-side sessions in the central PostgreSQL database
    # rather than Vercel's ephemeral filesystem.
    app.config[
        "SESSION_TYPE"
    ] = "sqlalchemy"

    app.config[
        "SESSION_SQLALCHEMY_TABLE"
    ] = "medsecure_sessions"

    # Periodic cleanup of expired Flask-Session rows.
    app.config[
        "SESSION_CLEANUP_N_REQUESTS"
    ] = 100


# ---------------------------------------------------------
# LOCAL DEVELOPMENT
# ---------------------------------------------------------

else:

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "sqlite:///medsecure.db"

    app.config[
        "SESSION_TYPE"
    ] = "filesystem"

    app.config[
        "SESSION_FILE_DIR"
    ] = os.path.join(
        app.instance_path,
        "flask_session",
    )

    os.makedirs(
        app.config["SESSION_FILE_DIR"],
        exist_ok=True,
    )


app.config[
    "SESSION_PERMANENT"
] = False

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False


# =========================================================
# SESSION SECURITY
# =========================================================

app.config[
    "SESSION_COOKIE_HTTPONLY"
] = True

app.config[
    "SESSION_COOKIE_SAMESITE"
] = "Lax"

# Local development uses HTTP; Vercel production uses HTTPS.
app.config[
    "SESSION_COOKIE_SECURE"
] = IS_PRODUCTION

app.config[
    "PERMANENT_SESSION_LIFETIME"
] = timedelta(minutes=15)


# Maximum request size: 1 MB
app.config[
    "MAX_CONTENT_LENGTH"
] = 1024 * 1024


# =========================================================
# EXTENSIONS
# =========================================================

db = SQLAlchemy(app)


# Flask-Session needs the existing Flask-SQLAlchemy object when
# PostgreSQL is used as the server-side session backend.
if app.config[
    "SESSION_TYPE"
] == "sqlalchemy":

    app.config[
        "SESSION_SQLALCHEMY"
    ] = db


csrf = CSRFProtect(app)


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


login_manager = LoginManager(app)

login_manager.login_view = "login"

login_manager.login_message = (
    "Please log in to access MedSecure."
)


# =========================================================
# MICROSOFT ENTRA ID CLIENT
# =========================================================

entra_auth = None

if ENTRA_CONFIGURED:
    entra_auth = EntraAuth(
        app,
        authority=ENTRA_AUTHORITY,
        client_id=ENTRA_CLIENT_ID,
        client_credential=ENTRA_CLIENT_SECRET,
        redirect_uri=ENTRA_REDIRECT_URI,
    )


# =========================================================
# DATABASE MODELS
# =========================================================


class Patient(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    patient_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(100),
        nullable=False,
    )

    dob = db.Column(
        db.String(20),
        nullable=False,
    )

    allergies = db.Column(
        db.String(250),
        nullable=False,
    )

    medication = db.Column(
        db.String(250),
        nullable=False,
    )

    notes = db.Column(
        db.Text,
        nullable=False,
    )

    # -----------------------------------------------------
    # TEMPLATE COMPATIBILITY HELPERS
    #
    # These aliases keep older template names working while
    # the database continues to use the canonical fields:
    # patient_code, dob, medication and notes.
    # -----------------------------------------------------

    @property
    def patient_id(self):

        return self.patient_code


    @property
    def date_of_birth(self):

        return self.dob


    @property
    def medications(self):

        return self.medication


    @property
    def clinical_notes(self):

        return self.notes


class User(
    UserMixin,
    db.Model,
):

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    role = db.Column(
        db.String(20),
        nullable=False,
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=True,
    )

    # These columns are retained for compatibility
    # with the database created during the earlier
    # MFA development iteration.
    #
    # Enterprise authentication will later be
    # integrated through Microsoft identity services.

    mfa_secret = db.Column(
        db.String(32),
        nullable=True,
    )

    mfa_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    # Organisational workforce profile.
    #
    # This is separate from authentication so the current
    # local login can later be replaced with Microsoft Entra
    # ID / Active Directory without redesigning employee data.

    employee_profile = db.relationship(
        "EmployeeProfile",
        back_populates="user",
        uselist=False,
    )


    def set_password(
        self,
        password,
    ):

        self.password_hash = (
            generate_password_hash(
                password
            )
        )


    def check_password(
        self,
        password,
    ):

        return check_password_hash(
            self.password_hash,
            password,
        )


class Organisation(db.Model):

    __tablename__ = "organisation"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    organisation_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    legal_name = db.Column(
        db.String(200),
        nullable=True,
    )

    organisation_type = db.Column(
        db.String(100),
        nullable=False,
    )

    email_domain = db.Column(
        db.String(150),
        nullable=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="ACTIVE",
    )

    created_at = db.Column(
        db.String(50),
        nullable=False,
    )

    facilities = db.relationship(
        "OrganisationFacility",
        back_populates="organisation",
        lazy=True,
    )


class OrganisationFacility(db.Model):

    __tablename__ = "organisation_facility"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    organisation_id = db.Column(
        db.Integer,
        db.ForeignKey("organisation.id"),
        nullable=False,
    )

    facility_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    facility_type = db.Column(
        db.String(100),
        nullable=False,
    )

    address = db.Column(
        db.String(250),
        nullable=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="ACTIVE",
    )

    created_at = db.Column(
        db.String(50),
        nullable=False,
    )

    organisation = db.relationship(
        "Organisation",
        back_populates="facilities",
    )

    departments = db.relationship(
        "OrganisationDepartment",
        back_populates="facility",
        lazy=True,
    )


class OrganisationDepartment(db.Model):

    __tablename__ = "organisation_department"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    facility_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "organisation_facility.id"
        ),
        nullable=False,
    )

    department_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    department_type = db.Column(
        db.String(100),
        nullable=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="ACTIVE",
    )

    created_at = db.Column(
        db.String(50),
        nullable=False,
    )

    facility = db.relationship(
        "OrganisationFacility",
        back_populates="departments",
    )

    employees = db.relationship(
        "EmployeeProfile",
        back_populates="department",
        lazy=True,
    )


class EmployeeProfile(db.Model):

    __tablename__ = "employee_profile"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False,
    )

    employee_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
    )

    full_name = db.Column(
        db.String(150),
        nullable=False,
    )

    work_email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
    )

    job_title = db.Column(
        db.String(120),
        nullable=False,
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "organisation_department.id"
        ),
        nullable=False,
    )

    employment_type = db.Column(
        db.String(50),
        nullable=False,
    )

    identity_provider = db.Column(
        db.String(100),
        nullable=False,
    )

    account_status = db.Column(
        db.String(30),
        nullable=False,
        default="ACTIVE",
    )

    created_at = db.Column(
        db.String(50),
        nullable=False,
    )

    user = db.relationship(
        "User",
        back_populates="employee_profile",
    )

    department = db.relationship(
        "OrganisationDepartment",
        back_populates="employees",
    )

    @property
    def facility(self):

        if not self.department:
            return None

        return self.department.facility


    @property
    def organisation(self):

        if not self.facility:
            return None

        return self.facility.organisation


class SecurityEvent(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    username = db.Column(
        db.String(80),
        nullable=False,
    )

    action = db.Column(
        db.String(150),
        nullable=False,
    )

    result = db.Column(
        db.String(30),
        nullable=False,
    )


# =========================================================
# LOGIN MANAGER
# =========================================================


@login_manager.user_loader
def load_user(
    user_id,
):

    return db.session.get(
        User,
        int(user_id),
    )


@app.context_processor
def inject_current_employee_profile():

    employee_profile = None

    if (
        current_user.is_authenticated
        and current_user.role
        in [
            "nurse",
            "doctor",
            "admin",
        ]
    ):

        employee_profile = (
            EmployeeProfile.query
            .filter_by(
                user_id=current_user.id
            )
            .first()
        )

    return {
        "current_employee_profile":
            employee_profile
    }


# =========================================================
# SECURITY EVENT LOGGING
# =========================================================


def log_event(
    username,
    action,
    result,
):

    event = SecurityEvent(
        username=username,
        action=action,
        result=result,
    )

    db.session.add(
        event
    )

    db.session.commit()


# =========================================================
# ROLE-BASED ACCESS CONTROL
# =========================================================


def roles_required(
    *allowed_roles,
):

    def decorator(
        function,
    ):

        @wraps(function)
        def wrapper(
            *args,
            **kwargs,
        ):

            if (
                current_user.role
                not in allowed_roles
            ):

                log_event(
                    current_user.username,
                    (
                        "UNAUTHORIZED_ACCESS "
                        f"{request.path}"
                    ),
                    "BLOCKED",
                )

                abort(403)

            return function(
                *args,
                **kwargs,
            )

        return wrapper

    return decorator


# =========================================================
# SECURITY HEADERS
# =========================================================


@app.after_request
def apply_security_headers(
    response,
):

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"


    response.headers[
        "X-Frame-Options"
    ] = "DENY"


    response.headers[
        "Referrer-Policy"
    ] = "no-referrer"


    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"
    )


    response.headers[
        "Content-Security-Policy"
    ] = (
        "default-src 'self'; "
        "style-src 'self'; "
        "script-src 'self'; "
        "img-src 'self' data:; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'"
    )


    response.headers[
        "Cache-Control"
    ] = (
        "no-store, "
        "no-cache, "
        "must-revalidate"
    )


    return response


# =========================================================
# HOME
# =========================================================


@app.route("/")
def home():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard"
            )
        )

    return redirect(
        url_for(
            "login"
        )
    )


# =========================================================
# MICROSOFT ENTRA WORKFORCE AUTHENTICATION
# =========================================================

# The Entra app roles are the authoritative workforce roles.
# For this assessment prototype there is one seeded local profile
# for each workforce role. After Microsoft authenticates the user,
# the verified app-role claim is mapped to that local application
# profile so the existing Flask-Login RBAC continues to work.
#
# This keeps authentication and application authorization separate:
# Microsoft verifies the workforce identity; MedSecure applies its
# own least-privilege route controls to the established session.

ENTRA_ROLE_MAP = {
    "MedSecure.Nurse": "nurse",
    "MedSecure.Doctor": "doctor",
    "MedSecure.Admin": "admin",
}

ENTRA_LOCAL_PROFILE_MAP = {
    "nurse": "nurse1",
    "doctor": "doctor1",
    "admin": "admin1",
}


def _entra_principal(claims):

    return (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("name")
        or claims.get("oid")
        or claims.get("sub")
        or "UNKNOWN_ENTRA_USER"
    )


def _resolve_entra_role(claims):

    token_roles = claims.get(
        "roles",
        [],
    )

    if isinstance(
        token_roles,
        str,
    ):
        token_roles = [
            token_roles
        ]

    recognised = [
        role
        for role in token_roles
        if role in ENTRA_ROLE_MAP
    ]

    # The prototype intentionally requires exactly one MedSecure
    # app role. This avoids ambiguous privilege selection.
    if len(recognised) != 1:
        return None, recognised

    return (
        ENTRA_ROLE_MAP[
            recognised[0]
        ],
        recognised,
    )


def workforce_entra_login(
    *,
    context=None,
):

    if current_user.is_authenticated:
        return redirect(
            url_for(
                "dashboard"
            )
        )

    if not ENTRA_CONFIGURED:
        flash(
            "Microsoft Entra workforce sign-in is not configured."
        )
        return redirect(
            url_for(
                "login"
            )
        )

    claims = (
        context or {}
    ).get(
        "user",
        {},
    )

    principal = _entra_principal(
        claims
    )
    entra_display_name = (
    claims.get("name")
    or claims.get("preferred_username")
    or principal
    )

    # Defence in depth: the ID token must belong to the configured
    # tenant even though the MSAL/Identity library has already
    # validated the token against our single-tenant authority.
    if claims.get("tid") != ENTRA_TENANT_ID:
        log_event(
            principal,
            "ENTRA_LOGIN_TENANT",
            "BLOCKED",
        )
        flash(
            "This Microsoft account is not authorised for the "
            "MedSecure tenant."
        )
        return redirect(
            url_for(
                "login"
            )
        )
    local_role, recognised_roles = (
        _resolve_entra_role(
            claims
        )
    )

    if not local_role:
        log_event(
            principal,
            "ENTRA_APP_ROLE",
            "BLOCKED",
        )
        flash(
            "Your Microsoft identity does not have exactly one "
            "authorised MedSecure application role."
        )
        return redirect(
            url_for(
                "login"
            )
        )

    local_username = (
        ENTRA_LOCAL_PROFILE_MAP[
            local_role
        ]
    )

    user = (
        User.query
        .filter_by(
            username=local_username
        )
        .first()
    )

    if (
        not user
        or user.role != local_role
    ):
        log_event(
            principal,
            "ENTRA_PROFILE_MAPPING",
            "BLOCKED",
        )
        flash(
            "MedSecure could not map this workforce identity to "
            "an application profile."
        )
        return redirect(
            url_for(
                "login"
            )
        )

    workforce_profile = (
        EmployeeProfile.query
        .filter_by(
            user_id=user.id
        )
        .first()
    )

    if (
        not workforce_profile
        or workforce_profile.account_status.upper()
        != "ACTIVE"
    ):
        log_event(
            principal,
            "ENTRA_WORKFORCE_STATUS",
            "BLOCKED",
        )
        flash(
            "This MedSecure workforce profile is disabled. "
            "Contact MedSecure administration."
        )
        return redirect(
            url_for(
                "login"
            )
        )

    # Record that this application profile is now using Microsoft
    # Entra ID for workforce authentication.
    if (
        workforce_profile.identity_provider
        != "Microsoft Entra ID"
    ):
        workforce_profile.identity_provider = (
            "Microsoft Entra ID"
        )
        db.session.commit()

    login_user(
        user,
        fresh=True,
    )

    session.permanent = True

    session[
        "identity_provider"
    ] = "Microsoft Entra ID"

    session[
        "entra_principal"
    ] = principal
    session[
    "entra_display_name"
    ] = entra_display_name

    session[
        "entra_roles"
    ] = recognised_roles

    session[
        "entra_oid"
    ] = (
        claims.get("oid")
        or claims.get("sub")
    )

    log_event(
        principal,
        "ENTRA_LOGIN",
        "SUCCESS",
    )

    log_event(
        principal,
        (
            "ENTRA_ROLE "
            f"{recognised_roles[0]}"
        ),
        "ALLOWED",
    )

    return redirect(
        url_for(
            "dashboard"
        )
    )


# Register the workforce route dynamically so the application can
# still start in CI/testing environments where Entra secrets are
# intentionally unavailable.
if entra_auth:
    workforce_entra_login = (
        entra_auth.login_required(
            workforce_entra_login
        )
    )

app.add_url_rule(
    "/workforce/login",
    endpoint="workforce_entra_login",
    view_func=workforce_entra_login,
    methods=["GET"],
)


# =========================================================
# LOGIN
# =========================================================


@app.route(
    "/login",
    methods=[
        "GET",
        "POST",
    ],
)
@limiter.limit(
    "5 per minute",
    methods=["POST"],
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard"
            )
        )


    if request.method == "POST":

        username = (
            request.form.get(
                "username",
                "",
            )
            .strip()
        )


        password = (
            request.form.get(
                "password",
                "",
            )
        )


        user = (
            User.query
            .filter_by(
                username=username
            )
            .first()
        )


        # =================================================
        # SUCCESSFUL PASSWORD AUTHENTICATION
        # =================================================

        if (
            user
            and user.check_password(
                password
            )
        ):

            # -------------------------------------------------
            # WORKFORCE ACCOUNT STATUS
            # -------------------------------------------------
            # Patient accounts do not have an EmployeeProfile.
            # Workforce accounts must be ACTIVE before a session
            # can be established. This provides a simple, auditable
            # offboarding control for the development environment.

            workforce_profile = (
                EmployeeProfile.query
                .filter_by(
                    user_id=user.id
                )
                .first()
            )

            # Workforce passwords are retained only as development
            # compatibility data. In normal runtime, workforce staff
            # must authenticate through Microsoft Entra ID. Tests may
            # still exercise the historical local workflow so the
            # security regression suite remains useful.
            local_workforce_allowed = (
                app.config.get(
                    "TESTING",
                    False,
                )
                or os.getenv(
                    "ALLOW_LOCAL_WORKFORCE_LOGIN",
                    "0",
                ) == "1"
            )

            if (
                user.role
                in [
                    "nurse",
                    "doctor",
                    "admin",
                ]
                and not local_workforce_allowed
            ):
                log_event(
                    user.username,
                    "LOCAL_WORKFORCE_LOGIN",
                    "BLOCKED",
                )
                flash(
                    "Workforce accounts must sign in with "
                    "Microsoft Entra ID."
                )
                return render_template(
                    "login.html"
                )

            if (
                workforce_profile
                and workforce_profile.account_status.upper()
                != "ACTIVE"
            ):

                log_event(
                    user.username,
                    "WORKFORCE_LOGIN",
                    "BLOCKED",
                )

                flash(
                    "This workforce account is disabled. "
                    "Contact MedSecure administration."
                )

                return render_template(
                    "login.html"
                )

            log_event(
                user.username,
                "PASSWORD_AUTH",
                "SUCCESS",
            )


            # -------------------------------------------------
            # CURRENT LOCAL AUTHENTICATION
            #
            # This remains the working development login.
            #
            # Enterprise identity will later be replaced with
            # Microsoft Entra ID / Active Directory based SSO.
            # -------------------------------------------------

            login_user(
                user,
                fresh=True,
            )


            session.permanent = True


            # Remove any pending MFA state remaining
            # from the earlier TOTP development iteration.

            session.pop(
                "mfa_user_id",
                None,
            )


            log_event(
                user.username,
                "LOGIN",
                "SUCCESS",
            )


            return redirect(
                url_for(
                    "dashboard"
                )
            )


        # =================================================
        # FAILED PASSWORD AUTHENTICATION
        # =================================================

        log_event(
            (
                username
                or "UNKNOWN"
            ),
            "PASSWORD_AUTH",
            "FAILED",
        )


        flash(
            "Invalid username or password."
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================


@app.route(
    "/logout",
    methods=["POST"],
)
@csrf.exempt
@login_required
def logout():

    username = (
        current_user.username
    )

    was_entra_session = (
        session.get(
            "identity_provider"
        )
        == "Microsoft Entra ID"
    )

    audit_identity = (
        session.get(
            "entra_principal"
        )
        or username
    )

    logout_user()

    log_event(
        audit_identity,
        "LOGOUT",
        "SUCCESS",
    )

    if (
        was_entra_session
        and entra_auth
    ):
        # The Microsoft identity helper clears its own token/user
        # state and sends the browser to the Entra end-session
        # endpoint before returning to MedSecure.
        return entra_auth.logout()

    session.clear()

    return redirect(
        url_for(
            "login"
        )
    )


# =========================================================
# DASHBOARD
# =========================================================


@app.route(
    "/dashboard"
)
@login_required
def dashboard():

    patient = None

    patients = []

    users = []

    employee_profile = None

    organisation = None

    facilities = []

    departments = []

    employees = []


    # =====================================================
    # PATIENT DASHBOARD
    # =====================================================

    if (
        current_user.role
        == "patient"
    ):

        patient = db.session.get(
            Patient,
            current_user.patient_id,
        )


    # =====================================================
    # NURSE / DOCTOR DASHBOARD
    # =====================================================

    elif (
        current_user.role
        in [
            "nurse",
            "doctor",
        ]
    ):

        patients = (
            Patient.query
            .order_by(
                Patient.name.asc()
            )
            .all()
        )

        employee_profile = (
            EmployeeProfile.query
            .filter_by(
                user_id=current_user.id
            )
            .first()
        )


    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    elif (
        current_user.role
        == "admin"
    ):

        users = (
            User.query
            .order_by(
                User.username.asc()
            )
            .all()
        )

        organisation = (
            Organisation.query
            .order_by(
                Organisation.id.asc()
            )
            .first()
        )

        facilities = (
            OrganisationFacility.query
            .order_by(
                OrganisationFacility.name.asc()
            )
            .all()
        )

        departments = (
            OrganisationDepartment.query
            .order_by(
                OrganisationDepartment.name.asc()
            )
            .all()
        )

        employees = (
            EmployeeProfile.query
            .order_by(
                EmployeeProfile.full_name.asc()
            )
            .all()
        )

        employee_profile = (
            EmployeeProfile.query
            .filter_by(
                user_id=current_user.id
            )
            .first()
        )


    return render_template(
        "dashboard.html",
        patient=patient,
        patients=patients,
        users=users,
        employee_profile=employee_profile,
        organisation=organisation,
        facilities=facilities,
        departments=departments,
        employees=employees,
    )


# =========================================================
# ORGANISATION
# =========================================================


@app.route(
    "/organisation"
)
@login_required
@roles_required(
    "admin"
)
def organisation_overview():

    organisation = (
        Organisation.query
        .order_by(
            Organisation.id.asc()
        )
        .first()
    )


    if not organisation:

        abort(404)


    facilities = (
        OrganisationFacility.query
        .filter_by(
            organisation_id=organisation.id
        )
        .order_by(
            OrganisationFacility.name.asc()
        )
        .all()
    )


    departments = (
        OrganisationDepartment.query
        .join(
            OrganisationFacility
        )
        .filter(
            OrganisationFacility
            .organisation_id
            == organisation.id
        )
        .order_by(
            OrganisationDepartment
            .name
            .asc()
        )
        .all()
    )


    employees = (
        EmployeeProfile.query
        .join(
            OrganisationDepartment
        )
        .join(
            OrganisationFacility
        )
        .filter(
            OrganisationFacility
            .organisation_id
            == organisation.id
        )
        .order_by(
            EmployeeProfile
            .full_name
            .asc()
        )
        .all()
    )


    log_event(
        current_user.username,
        "VIEW_ORGANISATION",
        "ALLOWED",
    )


    return render_template(
        "organisation.html",
        organisation=organisation,
        facilities=facilities,
        departments=departments,
        employees=employees,
    )


# =========================================================
# WORKFORCE DIRECTORY
# =========================================================


@app.route(
    "/employees"
)
@login_required
@roles_required(
    "admin"
)
def employee_directory():

    employees = (
        EmployeeProfile.query
        .order_by(
            EmployeeProfile
            .full_name
            .asc()
        )
        .all()
    )


    log_event(
        current_user.username,
        "VIEW_EMPLOYEE_DIRECTORY",
        "ALLOWED",
    )


    return render_template(
        "employees.html",
        employees=employees,
    )


# =========================================================
# PROVISION WORKFORCE EMPLOYEE
# =========================================================


@app.route(
    "/employees/new",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
@roles_required(
    "admin"
)
def provision_employee():

    departments = (
        OrganisationDepartment.query
        .filter_by(
            status="ACTIVE"
        )
        .order_by(
            OrganisationDepartment
            .name
            .asc()
        )
        .all()
    )


    allowed_roles = {
        "nurse",
        "doctor",
        "admin",
    }

    allowed_employment_types = {
        "Permanent",
        "Part-time",
        "Casual",
        "Contract",
    }


    if request.method == "POST":

        employee_code = (
            request.form.get(
                "employee_code",
                "",
            )
            .strip()
            .upper()
        )

        full_name = (
            request.form.get(
                "full_name",
                "",
            )
            .strip()
        )

        work_email = (
            request.form.get(
                "work_email",
                "",
            )
            .strip()
            .lower()
        )

        job_title = (
            request.form.get(
                "job_title",
                "",
            )
            .strip()
        )

        username = (
            request.form.get(
                "username",
                "",
            )
            .strip()
            .lower()
        )

        role = (
            request.form.get(
                "role",
                "",
            )
            .strip()
            .lower()
        )

        employment_type = (
            request.form.get(
                "employment_type",
                "",
            )
            .strip()
        )

        temporary_password = (
            request.form.get(
                "temporary_password",
                "",
            )
        )

        department_value = (
            request.form.get(
                "department_id",
                "",
            )
            .strip()
        )


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not all(
            [
                employee_code,
                full_name,
                work_email,
                job_title,
                username,
                role,
                employment_type,
                temporary_password,
                department_value,
            ]
        ):

            flash(
                "All workforce provisioning fields are required."
            )

            return render_template(
                "provision_employee.html",
                departments=departments,
            )


        # -------------------------------------------------
        # INPUT VALIDATION
        # -------------------------------------------------

        if role not in allowed_roles:

            abort(400)


        if (
            employment_type
            not in allowed_employment_types
        ):

            abort(400)


        if len(temporary_password) < 12:

            flash(
                "Temporary password must contain at least "
                "12 characters."
            )

            return render_template(
                "provision_employee.html",
                departments=departments,
            )


        if (
            len(employee_code) > 30
            or len(full_name) > 150
            or len(work_email) > 150
            or len(job_title) > 120
            or len(username) > 80
        ):

            abort(400)


        if (
            "@" not in work_email
            or work_email.startswith("@")
            or work_email.endswith("@")
        ):

            flash(
                "Enter a valid work email address."
            )

            return render_template(
                "provision_employee.html",
                departments=departments,
            )


        try:
            department_id = int(
                department_value
            )
        except ValueError:
            abort(400)


        department = db.session.get(
            OrganisationDepartment,
            department_id,
        )

        if (
            not department
            or department.status.upper()
            != "ACTIVE"
        ):

            abort(400)


        # -------------------------------------------------
        # UNIQUENESS CHECKS
        # -------------------------------------------------

        if (
            User.query
            .filter_by(
                username=username
            )
            .first()
        ):

            flash(
                "That MedSecure username is already in use."
            )

            return render_template(
                "provision_employee.html",
                departments=departments,
            )


        if (
            EmployeeProfile.query
            .filter_by(
                employee_code=employee_code
            )
            .first()
        ):

            flash(
                "That employee ID is already in use."
            )

            return render_template(
                "provision_employee.html",
                departments=departments,
            )


        if (
            EmployeeProfile.query
            .filter_by(
                work_email=work_email
            )
            .first()
        ):

            flash(
                "That work email is already assigned."
            )

            return render_template(
                "provision_employee.html",
                departments=departments,
            )


        # -------------------------------------------------
        # CREATE AUTHENTICATION ACCOUNT
        # -------------------------------------------------

        user = User(
            username=username,
            role=role,
            patient_id=None,
            mfa_secret=None,
            mfa_enabled=False,
        )

        user.set_password(
            temporary_password
        )

        db.session.add(
            user
        )

        db.session.flush()


        # -------------------------------------------------
        # CREATE ORGANISATIONAL PROFILE
        # -------------------------------------------------

        employee = EmployeeProfile(
            user_id=user.id,
            employee_code=employee_code,
            full_name=full_name,
            work_email=work_email,
            job_title=job_title,
            department_id=department.id,
            employment_type=employment_type,
            identity_provider=(
                "Local Development Identity"
            ),
            account_status="ACTIVE",
            created_at=(
                datetime.now(
                    timezone.utc
                )
                .isoformat()
            ),
        )

        db.session.add(
            employee
        )

        db.session.commit()


        log_event(
            current_user.username,
            (
                "PROVISION_EMPLOYEE_"
                f"{employee.employee_code}"
            ),
            "SUCCESS",
        )


        flash(
            "Workforce employee provisioned successfully."
        )


        return redirect(
            url_for(
                "employee_record",
                employee_id=employee.id,
            )
        )


    return render_template(
        "provision_employee.html",
        departments=departments,
    )


# =========================================================
# WORKFORCE ACCOUNT STATUS / OFFBOARDING
# =========================================================


@app.route(
    "/employee/<int:employee_id>/status",
    methods=["POST"],
)
@login_required
@roles_required(
    "admin"
)
def update_employee_status(
    employee_id,
):

    employee = db.session.get(
        EmployeeProfile,
        employee_id,
    )


    if not employee:
        abort(404)


    requested_status = (
        request.form.get(
            "status",
            "",
        )
        .strip()
        .upper()
    )


    if requested_status not in {
        "ACTIVE",
        "DISABLED",
    }:

        abort(400)


    # Prevent an administrator from accidentally disabling
    # their own currently authenticated workforce account.

    if (
        employee.user_id
        == current_user.id
        and requested_status
        == "DISABLED"
    ):

        log_event(
            current_user.username,
            "SELF_DISABLE_ACCOUNT",
            "BLOCKED",
        )

        flash(
            "You cannot disable your own active "
            "administrator account."
        )

        return redirect(
            url_for(
                "employee_record",
                employee_id=employee.id,
            )
        )


    employee.account_status = (
        requested_status
    )

    db.session.commit()


    log_event(
        current_user.username,
        (
            "WORKFORCE_STATUS_"
            f"{employee.employee_code}"
        ),
        requested_status,
    )


    if requested_status == "ACTIVE":
        flash(
            "Workforce account activated."
        )
    else:
        flash(
            "Workforce account disabled. Future sign-in "
            "attempts will be blocked."
        )


    return redirect(
        url_for(
            "employee_record",
            employee_id=employee.id,
        )
    )


# =========================================================
# EMPLOYEE PROFILE
# =========================================================


@app.route(
    "/employee/<int:employee_id>"
)
@login_required
@roles_required(
    "admin"
)
def employee_record(
    employee_id,
):

    employee = db.session.get(
        EmployeeProfile,
        employee_id,
    )


    if not employee:

        abort(404)


    log_event(
        current_user.username,
        (
            "VIEW_EMPLOYEE_"
            f"{employee.employee_code}"
        ),
        "ALLOWED",
    )


    return render_template(
        "employee.html",
        employee=employee,
    )


# =========================================================
# MY WORKFORCE PROFILE
# =========================================================


@app.route(
    "/my-profile"
)
@login_required
@roles_required(
    "nurse",
    "doctor",
    "admin",
)
def my_employee_profile():

    employee = (
        EmployeeProfile.query
        .filter_by(
            user_id=current_user.id
        )
        .first()
    )


    if not employee:

        abort(404)


    log_event(
        current_user.username,
        "VIEW_OWN_EMPLOYEE_PROFILE",
        "ALLOWED",
    )


    return render_template(
        "employee.html",
        employee=employee,
        own_profile=True,
    )


# =========================================================
# PATIENT RECORD
# =========================================================


@app.route(
    "/patient/<int:patient_id>"
)
@login_required
def patient_record(
    patient_id,
):

    patient = db.session.get(
        Patient,
        patient_id,
    )


    if not patient:

        abort(404)


    # =====================================================
    # PATIENT RECORD ISOLATION
    # =====================================================

    if (
        current_user.role
        == "patient"
    ):

        if (
            current_user.patient_id
            != patient.id
        ):

            log_event(
                current_user.username,
                (
                    "PATIENT_RECORD_"
                    f"{patient_id}"
                ),
                "BLOCKED",
            )

            abort(403)


    # =====================================================
    # ADMIN LEAST PRIVILEGE
    # =====================================================

    elif (
        current_user.role
        == "admin"
    ):

        log_event(
            current_user.username,
            (
                "PATIENT_RECORD_"
                f"{patient_id}"
            ),
            "BLOCKED",
        )

        abort(403)


    # =====================================================
    # CLINICAL ACCESS
    # =====================================================

    elif (
        current_user.role
        not in [
            "nurse",
            "doctor",
        ]
    ):

        log_event(
            current_user.username,
            (
                "PATIENT_RECORD_"
                f"{patient_id}"
            ),
            "BLOCKED",
        )

        abort(403)


    # =====================================================
    # SUCCESSFUL ACCESS
    # =====================================================

    log_event(
        current_user.username,
        (
            "VIEW_"
            f"{patient.patient_code}"
        ),
        "ALLOWED",
    )


    return render_template(
        "patient.html",
        patient=patient,
    )


# =========================================================
# ADD CLINICAL NOTE
# =========================================================


@app.route(
    "/patient/<int:patient_id>/note",
    methods=["POST"],
)
@login_required
@roles_required(
    "nurse",
    "doctor",
)
def add_note(
    patient_id,
):

    patient = db.session.get(
        Patient,
        patient_id,
    )


    if not patient:

        abort(404)


    note = (
        request.form.get(
            "note",
            "",
        )
        .strip()
    )


    # =====================================================
    # EMPTY INPUT
    # =====================================================

    if not note:

        flash(
            "Clinical note cannot be empty."
        )


        return redirect(
            url_for(
                "patient_record",
                patient_id=patient_id,
            )
        )


    # =====================================================
    # INPUT LENGTH VALIDATION
    # =====================================================

    if len(note) > 1000:

        log_event(
            current_user.username,
            (
                "ADD_NOTE_"
                f"{patient.patient_code}"
            ),
            "BLOCKED_LENGTH",
        )


        flash(
            (
                "Clinical note must not "
                "exceed 1000 characters."
            )
        )


        return redirect(
            url_for(
                "patient_record",
                patient_id=patient_id,
            )
        )


    timestamp = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M"
        )
    )


    patient.notes += (
        "\n\n"
        f"[{timestamp}] "
        f"{current_user.role.upper()} "
        f"{current_user.username}: "
        f"{note}"
    )


    db.session.commit()


    log_event(
        current_user.username,
        (
            "ADD_NOTE_"
            f"{patient.patient_code}"
        ),
        "SUCCESS",
    )


    flash(
        "Clinical note saved."
    )


    return redirect(
        url_for(
            "patient_record",
            patient_id=patient_id,
        )
    )


# =========================================================
# SECURITY LOGS
# =========================================================


@app.route(
    "/security-logs"
)
@login_required
@roles_required(
    "admin"
)
def security_logs():

    events = (
        SecurityEvent.query
        .order_by(
            SecurityEvent
            .timestamp
            .desc()
        )
        .limit(100)
        .all()
    )


    return render_template(
        "security_logs.html",
        events=events,
    )


# =========================================================
# ERROR HANDLER — 400
# =========================================================


@app.errorhandler(400)
def bad_request(
    error,
):

    return (
        render_template(
            "error.html",
            message=(
                "400 - Invalid Request"
            ),
        ),
        400,
    )


# =========================================================
# ERROR HANDLER — 403
# =========================================================


@app.errorhandler(403)
def forbidden(
    error,
):

    return (
        render_template(
            "error.html",
            message=(
                "403 - Access Denied"
            ),
        ),
        403,
    )


# =========================================================
# ERROR HANDLER — 404
# =========================================================


@app.errorhandler(404)
def not_found(
    error,
):

    return (
        render_template(
            "error.html",
            message=(
                "404 - Resource Not Found"
            ),
        ),
        404,
    )


# =========================================================
# ERROR HANDLER — 413
# =========================================================


@app.errorhandler(413)
def request_too_large(
    error,
):

    return (
        render_template(
            "error.html",
            message=(
                "413 - Request Too Large"
            ),
        ),
        413,
    )


# =========================================================
# ERROR HANDLER — RATE LIMIT
# =========================================================


@app.errorhandler(429)
def rate_limit_exceeded(
    error,
):

    username = "UNKNOWN"


    if request.method == "POST":

        username = (
            request.form.get(
                "username",
                "",
            )
            or "UNKNOWN"
        )


    try:

        log_event(
            username,
            "LOGIN_RATE_LIMIT",
            "BLOCKED",
        )


    except Exception as log_error:

        app.logger.warning(
            (
                "Failed to record "
                "rate-limit security "
                "event: %s"
            ),
            log_error,
        )


    return (
        render_template(
            "error.html",
            message=(
                "429 - Too Many Login Attempts"
            ),
        ),
        429,
    )


# =========================================================
# SYNTHETIC PATIENT DATA
# =========================================================


def seed_database():

    # Don't duplicate existing users/data.

    if User.query.first():

        return


    # =====================================================
    # PATIENT 1
    # =====================================================

    patient1 = Patient(

        patient_code=(
            "PT-1001"
        ),

        name=(
            "John Carter"
        ),

        dob=(
            "12 April 1950"
        ),

        allergies=(
            "Penicillin"
        ),

        medication=(
            "Metformin 500 mg, "
            "Atorvastatin 20 mg"
        ),

        notes=(
            "Routine observations completed. "
            "Patient clinically stable."
        ),
    )


    # =====================================================
    # PATIENT 2
    # =====================================================

    patient2 = Patient(

        patient_code=(
            "PT-1002"
        ),

        name=(
            "Mary Thompson"
        ),

        dob=(
            "8 September 1947"
        ),

        allergies=(
            "No known allergies"
        ),

        medication=(
            "Amlodipine 5 mg"
        ),

        notes=(
            "Blood pressure monitoring "
            "continues."
        ),
    )


    # =====================================================
    # PATIENT 3
    # =====================================================

    patient3 = Patient(

        patient_code=(
            "PT-1003"
        ),

        name=(
            "David Wilson"
        ),

        dob=(
            "21 January 1955"
        ),

        allergies=(
            "Sulfonamides"
        ),

        medication=(
            "Paracetamol PRN"
        ),

        notes=(
            "Mobility assessment completed."
        ),
    )


    db.session.add_all(
        [
            patient1,
            patient2,
            patient3,
        ]
    )


    db.session.flush()


    # =====================================================
    # DEMO USERS
    # =====================================================

    users = [

        (
            "patient1",
            os.getenv(
                "DEMO_PATIENT_PASSWORD"
            ),
            "patient",
            patient1.id,
        ),

        (
            "patient2",
            os.getenv(
                "DEMO_PATIENT_PASSWORD"
            ),
            "patient",
            patient2.id,
        ),

        (
            "nurse1",
            os.getenv(
                "DEMO_NURSE_PASSWORD"
            ),
            "nurse",
            None,
        ),

        (
            "doctor1",
            os.getenv(
                "DEMO_DOCTOR_PASSWORD"
            ),
            "doctor",
            None,
        ),

        (
            "admin1",
            os.getenv(
                "DEMO_ADMIN_PASSWORD"
            ),
            "admin",
            None,
        ),
    ]


    # =====================================================
    # CREATE USERS
    # =====================================================

    for (
        username,
        password,
        role,
        patient_id,
    ) in users:

        if not password:

            raise RuntimeError(
                (
                    "Missing demo password "
                    f"for {role} in .env"
                )
            )


        user = User(

            username=username,

            role=role,

            patient_id=patient_id,

            mfa_secret=None,

            mfa_enabled=False,
        )


        user.set_password(
            password
        )


        db.session.add(
            user
        )


    db.session.commit()


# =========================================================
# DATABASE INITIALISATION
# =========================================================

with app.app_context():

    if not IS_PRODUCTION:

        db.create_all()

        seed_database()


# =========================================================
# RUN APPLICATION
# =========================================================


if __name__ == "__main__":

    app.run()