from sqlalchemy.orm import Session
from src.database.models import CarritoDB, ItemCarritoDB

class CarritoRepositorio:

    def __init__(self, db: Session):
        self.db = db

    def _obtener_o_crear_carrito(self, sesion_id: str) -> CarritoDB:
        carrito = self.db.query(CarritoDB).filter(CarritoDB.sesion_id == sesion_id).first()
        if not carrito:
            carrito = CarritoDB(sesion_id=sesion_id)
            self.db.add(carrito)
            self.db.flush()
        return carrito

    def agregar_item(self, sesion_id: str, nombre: str, precio: float, cantidad: int) -> ItemCarritoDB:
        carrito = self._obtener_o_crear_carrito(sesion_id)
        item_existente = self.db.query(ItemCarritoDB).filter(
            ItemCarritoDB.carrito_id == carrito.id,
            ItemCarritoDB.nombre == nombre
        ).first()
        if item_existente:
            item_existente.cantidad += cantidad
            self.db.flush()
            return item_existente
        nuevo_item = ItemCarritoDB(carrito_id=carrito.id, nombre=nombre, precio=precio, cantidad=cantidad)
        self.db.add(nuevo_item)
        self.db.flush()
        return nuevo_item

    def calcular_total(self, sesion_id: str) -> float:
        carrito = self.db.query(CarritoDB).filter(CarritoDB.sesion_id == sesion_id).first()
        if not carrito:
            return 0.0
        subtotal = sum(item.precio * item.cantidad for item in carrito.items)
        if carrito.descuento_tipo == "porcentaje":
            subtotal = subtotal * (1 - carrito.descuento_valor / 100)
        elif carrito.descuento_tipo == "fijo":
            subtotal = subtotal - carrito.descuento_valor
        return max(subtotal, 0.0)