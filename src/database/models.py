from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class CarritoDB(Base):
    __tablename__ = "carritos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sesion_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descuento_tipo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    descuento_valor: Mapped[float] = mapped_column(Float, default=0.0)
    items: Mapped[list["ItemCarritoDB"]] = relationship(
        "ItemCarritoDB", back_populates="carrito", cascade="all, delete-orphan"
    )

class ItemCarritoDB(Base):
    __tablename__ = "items_carrito"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carrito_id: Mapped[int] = mapped_column(Integer, ForeignKey("carritos.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    carrito: Mapped["CarritoDB"] = relationship("CarritoDB", back_populates="items")