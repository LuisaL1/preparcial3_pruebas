import re
from playwright.sync_api import Page, expect

FRONTEND_URL = "http://localhost:4200"


def navegar_al_carrito(page: Page) -> None:
    page.goto(f"{FRONTEND_URL}/carrito")
    page.wait_for_load_state("networkidle")


def llenar_formulario(page: Page, nombre: str, precio: str, cantidad: str) -> None:
    page.get_by_test_id("input-nombre-producto").clear()
    page.get_by_test_id("input-nombre-producto").fill(nombre)

    page.get_by_test_id("input-precio-producto").clear()
    page.get_by_test_id("input-precio-producto").fill(precio)

    page.get_by_test_id("input-cantidad-producto").clear()
    page.get_by_test_id("input-cantidad-producto").fill(cantidad)


class TestCarritoFrontend:

    def test_flujo_agregar_monitor_y_verificar_total(self, page: Page):
        # Paso 1: navegar
        navegar_al_carrito(page)

        # Paso 2: llenar formulario
        llenar_formulario(page, "Monitor", "1500000", "1")

        # Paso 3: hacer clic en agregar
        page.get_by_test_id("btn-agregar-producto").click()

        # Paso 4: esperar y verificar total
        expect(page.get_by_test_id("total-carrito")).to_contain_text("1.500.000")

    def test_pagina_carga_elementos_del_formulario(self, page: Page):
        navegar_al_carrito(page)

        expect(page.get_by_test_id("input-nombre-producto")).to_be_visible()
        expect(page.get_by_test_id("input-precio-producto")).to_be_visible()
        expect(page.get_by_test_id("input-cantidad-producto")).to_be_visible()
        expect(page.get_by_test_id("btn-agregar-producto")).to_be_visible()

    def test_total_inicial_es_cero(self, page: Page):
        navegar_al_carrito(page)

        expect(page.get_by_test_id("total-carrito")).to_contain_text(re.compile(r"0"))

    def test_agregar_dos_productos_suma_total(self, page: Page):
        navegar_al_carrito(page)

        # Laptop: 2.500.000 × 1
        llenar_formulario(page, "Laptop", "2500000", "1")
        page.get_by_test_id("btn-agregar-producto").click()
        page.wait_for_timeout(500)

        # Mouse: 85.000 × 2
        llenar_formulario(page, "Mouse", "85000", "2")
        page.get_by_test_id("btn-agregar-producto").click()

        # Total esperado: 2.670.000
        expect(page.get_by_test_id("total-carrito")).to_contain_text("2.670.000")