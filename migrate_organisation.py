

Pasted code.py
Python
give me the whole code

efc4d7b6-deb5-4c3f-9a7b-570accffcbfd.png
yup much more better 

a33002c8-5483-46ca-851f-e492e6982ba3.png

53f39852-08e1-4744-bc3f-721104655205.png
its quite not right they want real software with real multifactor code sent to the phone 

0a98826d-557e-44c8-b10a-393100f99471.png

de0680b5-e45e-40eb-97a6-4cf087bae24e.png
Yes that should be the system of our website, and lets make it all realistic too. suppose in the photo the dashbaord is too blank, may be add a picture or make it look like health website, but in pro level, and i can't login as a nurse now because after scanning the QR the code doesn't appear lets do like that. also change some of the button colors like green make it like a real website not just demo. i have had enough with the demo, lets do it

9dfbc5dc-4ef5-4cf4-9821-5d4701f7e28c.png
also here change some things like the font or something else make it look really realistic

bf90691f-9aac-44f6-b643-92a45a474397.png
looks good but i would replace that john carter dashbaord image into a photos of health care professionals and such

a79eac13-14a8-4d95-8bd9-ea8231a76764.png
just make them fit here

eaef7f86-cd5c-4658-9ed4-702af1ccbce0.png
picture were ok like before but it wasn't doing slide show and still its not, like in the interval of 3 secs real time can't we make something like that?

78186977-fdfa-4cbb-9b2f-527bdf491efd.png
its like this doesn't really doing much

7c40ba11-4187-42a2-9933-ac60761eda64.png
looks like this now, alright later we will make a register page for patient and employee so that they can view their own profiles and such for now this is good

715f71c3-c071-45af-9bf3-d41060d000f5.png

94d0a2af-1d19-4705-915d-0127c6adf236.png
also the readability is not quite good here


Pasted code(1).py
Python

I reviewed your current app.py and built the full replacement file around the exact version you uploaded. Your existing app already has the working Flask setup, local authentication, RBAC, patient isolation, audit logging, rate limiting, CSRF protection, and security headers, so I preserved all of that rather than rebuilding from an older version. 


I also kept your current Patient, User, and SecurityEvent structure intact and added the organisational layer around it. 


What the new app.py adds
The replacement now includes:

Organisation
    ↓
Facilities
    ↓
Departments
    ↓
Employee Profiles
    ↓
Existing MedSecure User accounts
Plus these new routes:

/organisation
/employees
/employee/<id>
/my-profile
They are protected by RBAC:

Organisation        Admin only
Employee Directory  Admin only
Employee profile    Admin only
My profile           Nurse / Doctor / Admin
Viewing organisational information also generates security-audit events such as:

VIEW_ORGANISATION              ALLOWED
VIEW_EMPLOYEE_DIRECTORY        ALLOWED
VIEW_EMPLOYEE_EMP-1001         ALLOWED
VIEW_OWN_EMPLOYEE_PROFILE      ALLOWED
I also added compatibility properties so the earlier field-name mismatch between things like patient_code vs patient_id won't keep causing blank values in templates.

Step 1 — download the complete replacement
Download the full replacement app.py

Save it over:

D:\medsecure\app.py
You can first make a backup:

Copy-Item app.py app-backup-before-organisation.py
Then replace app.py with the downloaded file.

Step 2 — start MedSecure
Your migration has already created the required tables, so do not run the migration again.

Start Flask:

python app.py
You should see the normal Flask startup with no SQL/database errors.

Then test the existing site first:

http://127.0.0.1:5000/login
Log in as:

admin1
Admin123!
For now, do not visit /organisation yet, because we haven't created the new organisation templates. The important test at this stage is that:

login still works

Admin Dashboard still opens

Security Logs still opens

Nurse login still works

patient records still open

Once you confirm “app.py working”, our next step is to build the actual MedSecure Health Network Organisation Portal, starting with templates/organisation.html. That is where the three facilities, eight departments, and workforce directory will become visible inside the application. 


MedSecure_app_full_replacement.py
Code


it shows red in color the code file is the code not right?

Yes — it is the actual Python code file.

The .py file I gave you is meant to replace:

D:\medsecure\app.py
I also checked the generated file for Python syntax errors, and it compiles successfully.

If you mean the filename is showing red in VS Code, that does not automatically mean the code is wrong. Red can mean several things in VS Code, such as Git showing the file as changed/untracked, or the editor detecting an issue somewhere.

Do this first:

python app.py
If the Flask server starts normally, the file is fine.

If VS Code is showing red underlines inside the code, or python app.py gives an error, send me a screenshot or paste the error and I’ll fix it.


(.venv) PS D:\medsecure> python app.py
  File "D:\medsecure\app.py", line 7
    efc4d7b6-deb5-4c3f-9a7b-570accffcbfd.png
                  ^
SyntaxError: invalid decimal literal
(.venv) PS D:\medsecure>

That error means the local D:\medsecure\app.py is corrupted — the line

efc4d7b6-deb5-4c3f-9a7b-570accffcbfd.png
is obviously not Python code. So yes, something went wrong when that file was copied/replaced.

I’ve now created a clean app.py and syntax-checked it successfully.

Download the clean app.py

Do this:

Copy-Item app.py app-corrupted-backup.py
Then replace:

D:\medsecure\app.py
with the clean downloaded app.py.

After that, run:

python -m py_compile app.py
If that gives no output, the syntax is valid.

Then run:

python app.py
The clean file’s SHA-256 is:

56a215d7fc7d37c1bb628f2a8967170963fd39f1a95577375cc60839a63133b5
So this time we know the file itself is valid before you start Flask. 


app.py
Code


app.py


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


app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///medsecure.db"

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

# Local development currently uses HTTP.
# Production HTTPS should set this to True.
app.config[
    "SESSION_COOKIE_SECURE"
] = False

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
@login_required
def logout():

    username = (
        current_user.username
    )


    logout_user()


    session.clear()


    log_event(
        username,
        "LOGOUT",
        "SUCCESS",
    )


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

    db.create_all()

    seed_database()


# =========================================================
# RUN APPLICATION
# =========================================================


if __name__ == "__main__":

    app.run()
