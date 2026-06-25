from src.database.models import CarritoDB


class TestEndpointAgregarProducto:

    def test_agregar_producto_retorna_201(self, api_client):
        response = api_client.post(
            "/carrito/sesion-api-001/productos",
            json={"nombre": "Laptop", "precio": 2_500_000.0, "cantidad": 1},
        )

        assert response.status_code == 201
        assert response.json()["mensaje"] == "Producto agregado"
        assert "item_id" in response.json()

    def test_agregar_producto_persiste_en_bd(self, api_client, db_session):
        sesion_id = "sesion-api-002"

        api_client.post(
            f"/carrito/{sesion_id}/productos",
            json={"nombre": "Monitor", "precio": 1_200_000.0, "cantidad": 2},
        )

        carrito = db_session.query(CarritoDB).filter(
            CarritoDB.sesion_id == sesion_id
        ).first()

        assert carrito is not None
        assert len(carrito.items) == 1
        assert carrito.items[0].nombre == "Monitor"
        assert carrito.items[0].precio == 1_200_000.0
        assert carrito.items[0].cantidad == 2

    def test_agregar_mismo_producto_suma_cantidad(self, api_client, db_session):
        sesion_id = "sesion-api-003"

        api_client.post(
            f"/carrito/{sesion_id}/productos",
            json={"nombre": "Teclado", "precio": 150_000.0, "cantidad": 1},
        )
        api_client.post(
            f"/carrito/{sesion_id}/productos",
            json={"nombre": "Teclado", "precio": 150_000.0, "cantidad": 4},
        )

        carrito = db_session.query(CarritoDB).filter(
            CarritoDB.sesion_id == sesion_id
        ).first()

        assert carrito.items[0].cantidad == 5


class TestEndpointObtenerCarrito:

    def test_obtener_carrito_vacio_retorna_cero(self, api_client):
        response = api_client.get("/carrito/sesion-vacia")

        assert response.status_code == 200
        assert response.json()["total"] == 0.0

    def test_total_correcto_despues_de_agregar(self, api_client):
        sesion_id = "sesion-api-004"

        api_client.post(
            f"/carrito/{sesion_id}/productos",
            json={"nombre": "Laptop", "precio": 2_500_000.0, "cantidad": 1},
        )
        api_client.post(
            f"/carrito/{sesion_id}/productos",
            json={"nombre": "Mouse", "precio": 85_000.0, "cantidad": 2},
        )

        response = api_client.get(f"/carrito/{sesion_id}")

        assert response.status_code == 200
        assert response.json()["total"] == 2_670_000.0