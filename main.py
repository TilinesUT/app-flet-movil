"""Punto de entrada de la app Tienda Naranja.

Orquesta la navegacion entre el login, el perfil del usuario y el
catalogo de productos, y aplica el tema naranja/negro global.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import flet as ft

import src.config as config
from src.controllers.auth_controller import AuthController
from src.views.admin_page import AdminPage
from src.views.catalog_page import CatalogPage
from src.views.dashboard_page import DashboardPage
from src.views.login_page import LoginPage


class App:
    """Controlador raiz: configura la pagina y cambia entre vistas."""
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.auth = AuthController()
        self._configurar_entorno()

        # Si hay una sesion guardada en disco, se entra directo al perfil.
        if self.auth.restore_session() is not None:
            self.mostrar_home()
        else:
            self.mostrar_login()

    # ------------------------------------------------------------------
    # Configuracion global de la ventana y del tema
    # ------------------------------------------------------------------
    def _configurar_entorno(self) -> None:
        """Aplica titulo, fondo, tema oscuro y tamano de ventana movil."""
        self.page.title = "Tienda Naranja"
        self.page.padding = 0
        self.page.bgcolor = config.NEGRO
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=config.NARANJA,
                secondary=config.NARANJA_SUAVE,
                surface=config.SUPERFICIE,
                error=config.ERROR,
            ),
        )
        self.page.window.width = config.ANCHO_VENTANA
        self.page.window.height = config.ALTO_VENTANA

    # ------------------------------------------------------------------
    # Navegacion entre vistas
    # ------------------------------------------------------------------
    def _cambiar_vista(self, vista: ft.Control) -> None:
        """Limpia la pagina y muestra una nueva vista."""
        self.page.clean()
        self.page.add(vista)
        self.page.update()

    def mostrar_login(self) -> None:
        """Muestra la pantalla de inicio de sesion."""
        self._cambiar_vista(
            LoginPage(self.page, on_success=self.mostrar_home).build()
        )

    def mostrar_home(self) -> None:
        """Muestra el perfil del usuario autenticado."""
        self._cambiar_vista(
            DashboardPage(
                self.page,
                on_logout=self._cerrar_sesion,
                on_catalog=self.mostrar_catalogo,
                on_admin=self.mostrar_admin,
            ).build()
        )

    def mostrar_catalogo(self) -> None:
        """Muestra el catalogo de productos y dispara su carga asincrona."""
        vista = CatalogPage(self.page, on_home=self.mostrar_home)
        self._cambiar_vista(vista.build())
        self.page.run_task(vista._cargar)

    def mostrar_admin(self) -> None:
        """Muestra el panel de administracion (solo para administradores)."""
        vista = AdminPage(
            self.page,
            on_home=self.mostrar_home,
            on_catalog=self.mostrar_catalogo,
        )
        self._cambiar_vista(vista.build())
        self.page.run_task(vista._cargar)

    def _cerrar_sesion(self) -> None:
        """Destruye la sesion guardada y regresa al login."""
        self.auth.logout()
        self.mostrar_login()


def main(page: ft.Page) -> None:
    """Funcion principal que arranca la aplicacion."""
    App(page)


if __name__ == "__main__":
    # Soporte para ejecutar en una ventana nativa o como app web.
    view = os.environ.get("FLET_VIEW", "native")
    flet_view = (
        ft.AppView.WEB_BROWSER if view == "web" else ft.AppView.FLET_APP
    )
    ft.run(main, view=flet_view, port=8550)