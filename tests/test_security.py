import os
import pytest

from app import app, SecurityEvent


TEST_PATIENT_PASSWORD = os.environ["DEMO_PATIENT_PASSWORD"]
TEST_NURSE_PASSWORD = os.environ["DEMO_NURSE_PASSWORD"]
TEST_ADMIN_PASSWORD = os.environ["DEMO_ADMIN_PASSWORD"]


@pytest.fixture
def client():
    app.config["TESTING"] = True

    # Disable CSRF only inside automated tests.
    # CSRF remains enabled in the real MedSecure application.
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        yield client


def login(client, username, password, ip="10.10.10.1"):

    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
        environ_base={
            "REMOTE_ADDR": ip,
        },
        follow_redirects=False,
    )


# =========================================================
# TEST 1 — SUCCESSFUL AUTHENTICATION
# =========================================================

def test_valid_patient_login(client):

    response = login(
        client,
        "patient1",
        TEST_PATIENT_PASSWORD,
        "10.10.10.11",
    )

    assert response.status_code == 302

    assert "/dashboard" in response.headers["Location"]


# =========================================================
# TEST 2 — PATIENT CAN VIEW OWN RECORD
# =========================================================

def test_patient_can_view_own_record(client):

    login(
        client,
        "patient1",
        TEST_PATIENT_PASSWORD,
        "10.10.10.12",
    )

    response = client.get("/patient/1")

    assert response.status_code == 200

    assert b"John Carter" in response.data

    assert b"PT-1001" in response.data


# =========================================================
# TEST 3 — BROKEN ACCESS CONTROL PREVENTION
# =========================================================

def test_patient_cannot_view_another_patient(client):

    login(
        client,
        "patient1",
        TEST_PATIENT_PASSWORD,
        "10.10.10.13",
    )

    response = client.get("/patient/2")

    assert response.status_code == 403

    assert b"Access Denied" in response.data


# =========================================================
# TEST 4 — ADMIN LEAST PRIVILEGE
# =========================================================

def test_admin_cannot_access_clinical_record(client):

    login(
        client,
        "admin1",
        TEST_ADMIN_PASSWORD,
        "10.10.10.14",
    )

    response = client.get("/patient/1")

    assert response.status_code == 403


# =========================================================
# TEST 5 — NURSE CLINICAL ACCESS
# =========================================================

def test_nurse_can_access_patient_record(client):

    login(
        client,
        "nurse1",
        TEST_NURSE_PASSWORD,
        "10.10.10.15",
    )

    response = client.get("/patient/2")

    assert response.status_code == 200

    assert b"Mary Thompson" in response.data


# =========================================================
# TEST 6 — SECURITY LOG ACCESS CONTROL
# =========================================================

def test_nurse_cannot_access_security_logs(client):

    login(
        client,
        "nurse1",
        TEST_NURSE_PASSWORD,
        "10.10.10.16",
    )

    response = client.get("/security-logs")

    assert response.status_code == 403


# =========================================================
# TEST 7 — SECURITY HEADERS
# =========================================================

def test_security_headers(client):

    response = client.get("/login")

    assert (
        response.headers["X-Content-Type-Options"]
        == "nosniff"
    )

    assert (
        response.headers["X-Frame-Options"]
        == "DENY"
    )

    assert (
        response.headers["Referrer-Policy"]
        == "no-referrer"
    )

    assert "Content-Security-Policy" in response.headers

    assert (
        response.headers["Cache-Control"]
        == "no-store, no-cache, must-revalidate"
    )


# =========================================================
# TEST 8 — BRUTE-FORCE RATE LIMIT
# =========================================================

def test_login_rate_limiting(client):

    test_ip = "10.99.99.99"

    for attempt in range(5):

        response = login(
            client,
            "patient1",
            "wrongpassword",
            test_ip,
        )

        assert response.status_code == 200

    response = login(
        client,
        "patient1",
        "wrongpassword",
        test_ip,
    )

    assert response.status_code == 429

    assert b"Too Many Login Attempts" in response.data


# =========================================================
# TEST 9 — ZERO TRUST PATIENT WRITE DENIAL
# =========================================================

def test_zero_trust_patient_cannot_write_clinical_note(client):

    login(
        client,
        "patient1",
        TEST_PATIENT_PASSWORD,
        "10.10.10.17",
    )

    response = client.post(
        "/patient/1/note",
        data={
            "note": "Patient attempted to write a clinical note.",
        },
        environ_base={
            "REMOTE_ADDR": "10.10.10.17",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403


# =========================================================
# TEST 10 — ZERO TRUST NURSE WRITE ALLOW
# =========================================================

def test_zero_trust_nurse_can_write_clinical_note(client):

    login(
        client,
        "nurse1",
        TEST_NURSE_PASSWORD,
        "10.10.10.18",
    )

    response = client.post(
        "/patient/2/note",
        data={
            "note": "Zero Trust policy validation note.",
        },
        environ_base={
            "REMOTE_ADDR": "10.10.10.18",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302


# =========================================================
# TEST 11 — ZERO TRUST DECISION AUDIT
# =========================================================

def test_zero_trust_denial_is_audited(client):

    login(
        client,
        "patient1",
        TEST_PATIENT_PASSWORD,
        "10.10.10.19",
    )

    response = client.get(
        "/patient/2",
        environ_base={
            "REMOTE_ADDR": "10.10.10.19",
        },
    )

    assert response.status_code == 403

    with app.app_context():

        event = (
            SecurityEvent.query
            .filter(
                SecurityEvent.action.like(
                    "ZT_POLICY resource=clinical_record action=read%"
                )
            )
            .order_by(
                SecurityEvent.id.desc()
            )
            .first()
        )

        assert event is not None
        assert event.result == "BLOCKED"
        assert "PATIENT_OWNERSHIP_MISMATCH" in event.action
