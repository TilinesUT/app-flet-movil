"""Barra de navegacion comun, filtrada segun el rol del usuario."""

from __future__ import annotations

import flet as ft

import src.config as config
from src.models import Role


def crear_barra_navegacion(
    rol: Role | None,
    seccion: str,
    on_home,
    on_catalog,
    on_admin=None,
    on_usuarios=None,
    on_carritos=None,
) -> ft.NavigationBar:
    """Construye la barra inferior y oculta secciones no autorizadas.

    Los clientes nunca reciben destinos de Usuarios ni Carritos, por lo que
    la opcion desaparece del menu. Las vistas ademas validan el rol antes
    de cargar datos para bloquear un acceso forzado.
    """
    opciones: list[tuple[str, ft.NavigationBarDestination, object]] = []

    def agregar(clave: str, icono, etiqueta: str, callback) -> None:
        if callback is not None:
            opciones.append(
                (
                    clave,
                    ft.NavigationBarDestination(icon=icono, label=etiqueta),
                    callback,
                )
            )

    agregar("perfil", ft.Icons.PERSON, "Mi perfil", on_home)
    agregar("catalogo", ft.Icons.STORE, "Catalogo", on_catalog)

    if rol is Role.ADMIN:
        agregar("admin", ft.Icons.ADMIN_PANEL_SETTINGS, "Admin", on_admin)

    if rol in (Role.ADMIN, Role.AUDITOR):
        agregar("usuarios", ft.Icons.GROUPS, "Usuarios", on_usuarios)
        agregar("carritos", ft.Icons.SHOPPING_CART, "Carritos", on_carritos)

    claves = [clave for clave, _, _ in opciones]
    acciones = [callback for _, _, callback in opciones]
    destinos = [destino for _, destino, _ in opciones]
    seleccionado = claves.index(seccion) if seccion in claves else 0

    def cambiar(e) -> None:
        indice = e.control.selected_index
        if 0 <= indice < len(acciones):
            acciones[indice]()

    return ft.NavigationBar(
        destinations=destinos,
        selected_index=seleccionado,
        on_change=cambiar,
        bgcolor=config.CARBON,
    )
