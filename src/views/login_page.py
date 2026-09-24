"""Vista de inicio de sesion (tema naranja/negro).

Permite autenticarse contra la FakeStore API de forma asincrona y
distingue entre credenciales invalidas y errores de conexion.
"""

from __future__ import annotations

import asyncio

import flet as ft

import src.config as config
from src.controllers.auth_controller import AuthController
from src.views.widgets import boton_primario, campo_texto

# Cuentas de prueba de la FakeStore API (codigo = id del usuario).
_CUENTAS_DEMO = [
    ("johnd", "1"),
    ("mor_2314", "2"),
    ("kevinryan", "3"),
    ("donero", "4"),
]


class LoginPage:
    """Pantalla de login con los campos, el boton y los mensajes de error."""

    def __init__(self, page: ft.Page, on_success) -> None:
        self._page = page
        self._on_success = on_success          # callback al autenticarse
        self._auth = AuthController()
        self._campo_usuario = None
        self._campo_contrasena = None
        self._btn_ingresar = None
        self._error_texto = None

    def build(self) -> ft.Container:
        """Construye y devuelve la vista completa del login."""
        self._campo_usuario = campo_texto(
            "Usuario",
            hint="Tu codigo de acceso",
            icono=ft.Icons.PERSON,
        )
        self._campo_contrasena = campo_texto(
            "Contrasena",
            hint="Tu clave secreta",
            icono=ft.Icons.LOCK,
            contrasena=True,
            contrasena_revelable=True,
        )
        self._campo_contrasena.on_submit = self._on_login

        self._error_texto = ft.Text(
            "",
            size=13,
            color=config.ERROR,
            text_align=ft.TextAlign.CENTER,
        )

        self._btn_ingresar = boton_primario(
            "Ingresar",
            self._on_login,
            icono=ft.Icons.LOGIN,
        )

        # Logo: circulo naranja con el icono de la tienda.
        logo = ft.Container(
            content=ft.Icon(ft.Icons.STORE, size=44, color=config.NEGRO),
            width=84,
            height=84,
            alignment=ft.Alignment.CENTER,
            bgcolor=config.NARANJA,
            border_radius=ft.BorderRadius.all(26),
        )

        titulo = ft.Text(
            "TIENDA NARANJA",
            size=26,
            weight=ft.FontWeight.W_900,
            color=config.TEXTO_PRIMARIO,
        )
        subtitulo = ft.Text(
            "Inicia sesion para continuar",
            size=14,
            color=config.TEXTO_SECUNDARIO,
        )

        # Lista de cuentas de prueba para facilitar el ingreso.
        demo_superior = ft.Text(
            "Cuentas de prueba",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=config.TEXTO_SECUNDARIO,
        )
        pie_demostrativo = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.HELP_OUTLINE, size=14, color=config.NARANJA_SUAVE),
                        demo_superior,
                    ],
                    spacing=6,
                ),
                *[
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"  {usuario}",
                                size=12,
                                color=config.TEXTO_PRIMARIO,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                f"(rol codigo {codigo})",
                                size=12,
                                color=config.TEXTO_ATENUADO,
                            ),
                        ],
                        spacing=4,
                    )
                    for usuario, codigo in _CUENTAS_DEMO
                ],
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        formulario = ft.Column(
            controls=[
                logo,
                titulo,
                subtitulo,
                ft.Container(height=14),
                self._campo_usuario,
                self._campo_contrasena,
                self._error_texto,
                self._btn_ingresar,
                ft.Container(height=14),
                pie_demostrativo,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        )

        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[config.NEGRO, config.CARBON, config.NEGRO],
            ),
            padding=ft.Padding(left=28, top=40, right=28, bottom=28),
            alignment=ft.Alignment.CENTER,
            content=formulario,
        )

    # ------------------------------------------------------------------
    # Manejo del login (asincrono para no bloquear la interfaz)
    # ------------------------------------------------------------------
    async def _on_login(self, e) -> None:
        """Valida los campos y autentica al usuario en la API."""
        usuario = (self._campo_usuario.value or "").strip()
        contrasena = self._campo_contrasena.value or ""

        # Datos vacios: mensaje amigable sin llamar a la API.
        if not usuario or not contrasena:
            self._error_texto.value = "Ingresa el usuario y la contrasena."
            self._page.update()
            return

        # Deshabilita el boton mientras se procesa el login.
        self._btn_ingresar.disabled = True
        self._error_texto.value = ""
        self._page.update()

        try:
            # La llamada de red se ejecuta en otro hilo (asyncio.to_thread)
            # para no congelar la interfaz mientras se espera la respuesta.
            await asyncio.to_thread(self._auth.login, usuario, contrasena)
        except ValueError:
            # La API respondio 400/401 (credenciales invalidas).
            self._error_texto.value = (
                "Credenciales incorrectas. Verifica tu usuario y contrasena."
            )
        except Exception:
            # Fallo de red, DNS, timeout, servidor caido, etc.
            self._error_texto.value = (
                "Error de conexion. Revisa tu internet e intenta de nuevo."
            )
        else:
            # Exito: se pasa al siguiente modulo (Home del usuario).
            self._on_success()
            return
        finally:
            self._btn_ingresar.disabled = False
            self._page.update()