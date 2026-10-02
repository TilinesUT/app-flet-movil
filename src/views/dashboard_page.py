"""Vista de inicio del usuario autenticado (Mi Perfil).

Muestra la identidad, el rol segun el codigo del usuario y sus permisos,
con enlaces para ir al catalogo o cerrar sesion.
"""

from __future__ import annotations

import flet as ft

import src.config as config
from src.controllers.auth_controller import AuthController
from src.controllers.user_controller import UserController
from src.models import Role
from src.views.widgets import (
    avatar_codigo,
    boton_primario,
    boton_secundario,
    fila_dato,
    insignia_rol,
)

BORDE_SUAVE = ft.border.Border.all(width=1, color=config.BORDE)


class DashboardPage:
    """Pantalla del perfil: identidad, datos y permisos del usuario."""

    def __init__(self, page: ft.Page, on_logout, on_catalog, on_admin=None) -> None:
        self._page = page
        self._on_logout = on_logout       # callback de cerrar sesion
        self._on_catalog = on_catalog     # callback de ir al catalogo
        self._on_admin = on_admin         # callback del panel admin (solo admin)
        self._auth = AuthController()
        self._usuario = UserController()

    # ------------------------------------------------------------------
    # Utilidades de maquetacion
    # ------------------------------------------------------------------
    def _tarjeta(self, titulo: str, icono: str, hijos: list[ft.Control]) -> ft.Container:
        """Tarjeta con titulo (icono + texto) y contenido."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icono, size=18, color=config.NARANJA),
                            ft.Text(
                                titulo.upper(),
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=config.TEXTO_SECUNDARIO,
                            ),
                        ],
                        spacing=8,
                    ),
                    *hijos,
                ],
                spacing=12,
            ),
            padding=ft.Padding(left=16, top=16, right=16, bottom=16),
            bgcolor=config.SUPERFICIE,
            border_radius=ft.BorderRadius.all(14),
            border=BORDE_SUAVE,
        )

    def build(self) -> ft.Container:
        """Construye el perfil del usuario actualmente en sesion."""
        usuario = self._auth.current_user
        rol = self._auth.current_role

        if usuario is None or rol is None:
            # Sin sesion activa: pantalla vacia de fondo negro.
            return ft.Container(expand=True, bgcolor=config.NEGRO)

        nombre = self._usuario.get_full_name(usuario)
        etiqueta_rol = self._usuario.get_role_label(rol)
        color_rol = self._usuario.get_role_color(rol)
        permisos = self._usuario.get_permissions(rol)

        # Cabecera de la pagina.
        cabecera = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "MI PERFIL",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_ATENUADO,
                        ),
                        ft.Text("Bienvenido", size=22, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO),
                    ],
                    spacing=0,
                ),
                ft.Icon(ft.Icons.FAVORITE_BORDER, size=22, color=config.NARANJA_SUAVE),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Tarjeta de identidad: avatar con codigo + nombre + insignia de rol.
        identidad = ft.Container(
            content=ft.Column(
                controls=[
                    avatar_codigo(usuario.id),
                    ft.Text(nombre, size=20, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO),
                    ft.Text(usuario.email, size=13, color=config.TEXTO_SECUNDARIO),
                    insignia_rol(etiqueta_rol, color_rol),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.all(20),
            bgcolor=config.SUPERFICIE,
            border_radius=ft.BorderRadius.all(14),
            border=BORDE_SUAVE,
        )

        # Datos principales del usuario.
        datos = self._tarjeta(
            "Datos del usuario",
            ft.Icons.PERSON,
            [
                fila_dato(ft.Icons.MAIL, "Correo", usuario.email),
                fila_dato(ft.Icons.PERSON, "Usuario", usuario.username),
                fila_dato(ft.Icons.PHONE, "Telefono", usuario.phone),
                fila_dato(ft.Icons.PLACE, "Direccion", self._usuario.get_full_address(usuario)),
                fila_dato(ft.Icons.LOCATION_CITY, "Ciudad", usuario.address.city),
            ],
        )

        # Permisos asociados al rol del usuario.
        permiso_icono = ft.Icon(getattr(ft.Icons, permisos["icono"]), size=20, color=config.NEGRO)
        permisos_card = self._tarjeta(
            "Permisos",
            ft.Icons.SHIELD,
            [
                ft.Row(
                    controls=[
                        ft.Container(
                            content=permiso_icono,
                            width=40,
                            height=40,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=color_rol,
                            border_radius=ft.BorderRadius.all(12),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(permisos["titulo"], size=14, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO),
                                ft.Text(permisos["detalle"], size=12, color=config.TEXTO_SECUNDARIO),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                )
            ],
        )

        # Acciones: si es administrador, acceso destacado al panel de admin.
        es_admin = rol is Role.ADMIN
        boton_admin = None
        if es_admin and self._on_admin is not None:
            boton_admin = boton_primario(
                "Gestionar articulos",
                self._on_admin,
                ft.Icons.ADMIN_PANEL_SETTINGS,
            )
        acciones = ft.Row(
            controls=[
                boton_secundario("Cerrar sesion", self._on_logout, ft.Icons.LOGOUT),
                boton_primario("Ver catalogo", self._on_catalog, ft.Icons.STORE),
            ],
            spacing=10,
        )
        bloque_acciones = [boton_admin, acciones] if boton_admin is not None else [acciones]

        contenido = ft.ListView(
            controls=[cabecera, identidad, datos, permisos_card, *bloque_acciones],
            spacing=16,
            padding=ft.Padding.all(16),
            expand=True,
        )

        # Barra inferior: la pestana "Admin" solo aparece para administradores.
        destinos = [
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Mi perfil"),
            ft.NavigationBarDestination(icon=ft.Icons.STORE, label="Catalogo"),
        ]
        if es_admin:
            destinos.append(
                ft.NavigationBarDestination(icon=ft.Icons.ADMIN_PANEL_SETTINGS, label="Admin")
            )
        navegacion = ft.NavigationBar(
            destinations=destinos,
            selected_index=0,
            on_change=self._on_navegacion,
            bgcolor=config.CARBON,
        )

        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[config.NEGRO, config.CARBON, config.NEGRO],
            ),
            content=ft.Column(
                controls=[contenido, navegacion],
                spacing=0,
                expand=True,
            ),
        )

    def _on_navegacion(self, e) -> None:
        """Navega segun la pestana elegida en la barra inferior."""
        if e.control.selected_index == 1:
            self._on_catalog()
        elif e.control.selected_index == 2 and self._on_admin is not None:
            self._on_admin()