import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Base, engine


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ac01_solicitud_valida_y_calculo_saldo():
    # Crear ADMIN_RRHH (id=1)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Admin",
            "email": "admin@test.com",
            "rol": "ADMIN_RRHH",
            "anios_antiguedad": 5,
        },
    )

    # Crear MANAGER (id=2)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Manager",
            "email": "manager@test.com",
            "rol": "MANAGER",
            "anios_antiguedad": 3,
        },
        headers={"X-User-Id": "1"},
    )

    # Crear EMPLEADO (id=3, anios_antiguedad=3, manager_id=2)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Empleado",
            "email": "empleado@test.com",
            "rol": "EMPLEADO",
            "anios_antiguedad": 3,
            "manager_id": 2,
        },
        headers={"X-User-Id": "1"},
    )

    # Verificar saldo inicial: dias_totales = min(12 + 2*(3-1), 20) = 16
    saldo_resp = client.get("/api/v1/vacaciones/saldo/3")
    assert saldo_resp.status_code == 200
    saldo_data = saldo_resp.json()
    assert saldo_data["dias_totales"] == 16
    assert saldo_data["saldo_disponible"] == 16

    # Solicitar 5 días
    sol_resp = client.post(
        "/api/v1/vacaciones/solicitar",
        json={"empleado_id": 3, "dias_solicitados": 5, "motivo": "Vacaciones"},
    )
    assert sol_resp.status_code == 201
    sol_data = sol_resp.json()
    assert sol_data["estado"] == "PENDING"
    solicitud_id = sol_data["id"]

    # Manager aprueba
    rev_resp = client.post(
        f"/api/v1/vacaciones/{solicitud_id}/revisar",
        json={"accion": "APPROVE"},
        headers={"X-User-Id": "2"},
    )
    assert rev_resp.status_code == 200
    rev_data = rev_resp.json()
    assert rev_data["estado"] == "APPROVED"

    # Verificar nuevo saldo: 16 - 5 = 11
    saldo_resp2 = client.get("/api/v1/vacaciones/saldo/3")
    assert saldo_resp2.status_code == 200
    assert saldo_resp2.json()["saldo_disponible"] == 11


def test_ac02_saldo_insuficiente():
    # Crear ADMIN_RRHH (id=1)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Admin",
            "email": "admin@test.com",
            "rol": "ADMIN_RRHH",
            "anios_antiguedad": 5,
        },
    )

    # Crear EMPLEADO (id=2, anios_antiguedad=1 -> 12 días)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Empleado",
            "email": "empleado@test.com",
            "rol": "EMPLEADO",
            "anios_antiguedad": 1,
        },
        headers={"X-User-Id": "1"},
    )

    # Intentar solicitar 15 días (excede saldo de 12)
    resp = client.post(
        "/api/v1/vacaciones/solicitar",
        json={"empleado_id": 2, "dias_solicitados": 15},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Insufficient vacation balance"


def test_ac03_manager_no_autorizado():
    # Crear ADMIN_RRHH (id=1)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Admin",
            "email": "admin@test.com",
            "rol": "ADMIN_RRHH",
            "anios_antiguedad": 5,
        },
    )

    # Crear MANAGER A (id=2)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Manager A",
            "email": "managera@test.com",
            "rol": "MANAGER",
            "anios_antiguedad": 3,
        },
        headers={"X-User-Id": "1"},
    )

    # Crear MANAGER B (id=3)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Manager B",
            "email": "managerb@test.com",
            "rol": "MANAGER",
            "anios_antiguedad": 3,
        },
        headers={"X-User-Id": "1"},
    )

    # Crear EMPLEADO (id=4, manager_id=2)
    client.post(
        "/api/v1/empleados",
        json={
            "nombre": "Empleado",
            "email": "empleado@test.com",
            "rol": "EMPLEADO",
            "anios_antiguedad": 2,
            "manager_id": 2,
        },
        headers={"X-User-Id": "1"},
    )

    # Empleado 4 solicita 3 días
    sol_resp = client.post(
        "/api/v1/vacaciones/solicitar",
        json={"empleado_id": 4, "dias_solicitados": 3},
    )
    assert sol_resp.status_code == 201
    solicitud_id = sol_resp.json()["id"]

    # MANAGER B (id=3) intenta aprobar -> no es su jefe directo
    rev_resp = client.post(
        f"/api/v1/vacaciones/{solicitud_id}/revisar",
        json={"accion": "APPROVE"},
        headers={"X-User-Id": "3"},
    )
    assert rev_resp.status_code == 403
    assert rev_resp.json()["detail"] == "Unauthorized: Not the direct manager"
