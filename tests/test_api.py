import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Base, engine, get_db, Empleado, SolicitudVacaciones


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ac01_solicitud_valida_y_calculo_saldo(client):
    # Crear ADMIN_RRHH (id=1)
    client.post("/api/v1/empleados", json={
        "nombre": "Admin",
        "email": "admin@test.com",
        "rol": "ADMIN_RRHH",
        "anios_antiguedad": 5
    })

    # Crear MANAGER (id=2)
    client.post("/api/v1/empleados", json={
        "nombre": "Manager",
        "email": "manager@test.com",
        "rol": "MANAGER",
        "anios_antiguedad": 3
    }, headers={"X-User-Id": "1"})

    # Crear EMPLEADO (id=3, anios_antiguedad=3, manager_id=2)
    client.post("/api/v1/empleados", json={
        "nombre": "Empleado",
        "email": "empleado@test.com",
        "rol": "EMPLEADO",
        "anios_antiguedad": 3,
        "manager_id": 2
    }, headers={"X-User-Id": "1"})

    # Verificar saldo inicial: dias_totales = min(12 + 2*(3-1), 20) = 16
    response = client.get("/api/v1/vacaciones/saldo/3")
    assert response.status_code == 200
    data = response.json()
    assert data["dias_totales"] == 16
