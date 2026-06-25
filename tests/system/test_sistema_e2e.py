import os
import uuid
import httpx
import pytest

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="module")
def http_client():
    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
        yield client


def nueva_sesion() -> str:
    return f"e2e-{uuid.uuid4().hex[:12]}"


class TestFlujoCompletoCarrito:

    def test_agregar_dos_productos_y_verificar_total(self, http_client):
        sesion_id = nueva_sesion()

        # Paso 1: agregar primer producto
        respuesta_laptop = http_client.post(
            f"/carrito/{sesion_id}/productos",
            json={"nombre": "Laptop", "precio": 4_500_000.0, "cantidad": 1},
        )
        assert respuesta_laptop.status_code == 201

        # Paso 2: agregar segundo producto
        respuesta_monitor = http_client.post(
            f"/carrito/{sesion_id}/productos",
            json={"nombre": "Monitor", "precio": 1_800_000.0, "cantidad": 2},
        )
        assert respuesta_monitor.status_code == 201

        # Paso 3: consultar el carrito
        respuesta_carrito = http_client.get(f"/carrito/{sesion_id}")
        assert respuesta_carrito.status_code == 200

        # Paso 4: validar total matemáticamente
        # Laptop: 4_500_000 × 1 = 4_500_000
        # Monitor: 1_800_000 × 2 = 3_600_000
        # Total esperado: 8_100_000
        total_esperado = (4_500_000.0 * 1) + (1_800_000.0 * 2)
        assert respuesta_carrito.json()["total"] == total_esperado

    def test_carrito_inexistente_retorna_total_cero(self, http_client):
        sesion_id = nueva_sesion()

        respuesta = http_client.get(f"/carrito/{sesion_id}")

        assert respuesta.status_code == 200
        assert respuesta.json()["total"] == 0.0

    def test_sesiones_distintas_son_independientes(self, http_client):
        sesion_a = nueva_sesion()
        sesion_b = nueva_sesion()

        http_client.post(
            f"/carrito/{sesion_a}/productos",
            json={"nombre": "Laptop", "precio": 2_500_000.0, "cantidad": 1},
        )
        http_client.post(
            f"/carrito/{sesion_b}/productos",
            json={"nombre": "Mouse", "precio": 85_000.0, "cantidad": 3},
        )

        total_a = http_client.get(f"/carrito/{sesion_a}").json()["total"]
        total_b = http_client.get(f"/carrito/{sesion_b}").json()["total"]

        assert total_a == 2_500_000.0
        assert total_b == 255_000.0