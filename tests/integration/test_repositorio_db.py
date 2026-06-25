import pytest
from src.database.repositorio import CarritoRepositorio
from src.database.models import CarritoDB


class TestAgregarItem:

    def test_agregar_item_persiste_en_bd(self, db_session):
        repo = CarritoRepositorio(db_session)
        
        item = repo.agregar_item(
            sesion_id="sesion-001",
            nombre="Laptop",
            precio=2_500_000.0,
            cantidad=1,
        )

        assert item.id is not None
        assert item.nombre == "Laptop"
        assert item.precio == 2_500_000.0
        assert item.cantidad == 1

    def test_agregar_item_crea_carrito_automaticamente(self, db_session):
        repo = CarritoRepositorio(db_session)

        repo.agregar_item("sesion-002", "Mouse", 85_000.0, 2)

        carrito = db_session.query(CarritoDB).filter(
            CarritoDB.sesion_id == "sesion-002"
        ).first()

        assert carrito is not None
        assert len(carrito.items) == 1

    def test_agregar_mismo_producto_suma_cantidad(self, db_session):
        repo = CarritoRepositorio(db_session)

        repo.agregar_item("sesion-003", "Teclado", 150_000.0, 1)
        repo.agregar_item("sesion-003", "Teclado", 150_000.0, 3)

        carrito = db_session.query(CarritoDB).filter(
            CarritoDB.sesion_id == "sesion-003"
        ).first()

        assert len(carrito.items) == 1
        assert carrito.items[0].cantidad == 4


class TestCalcularTotal:

    def test_total_carrito_vacio(self, db_session):
        repo = CarritoRepositorio(db_session)

        total = repo.calcular_total("sesion-inexistente")

        assert total == 0.0

    def test_total_un_producto(self, db_session):
        repo = CarritoRepositorio(db_session)

        repo.agregar_item("sesion-004", "Laptop", 2_500_000.0, 2)
        total = repo.calcular_total("sesion-004")

        assert total == 5_000_000.0

    def test_total_multiples_productos(self, db_session):
        repo = CarritoRepositorio(db_session)

        repo.agregar_item("sesion-005", "Laptop", 2_500_000.0, 1)
        repo.agregar_item("sesion-005", "Mouse", 85_000.0, 2)
        total = repo.calcular_total("sesion-005")

        assert total == 2_670_000.0