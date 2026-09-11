from __future__ import annotations

import flet as ft

from src.controllers.auth_controller import AuthController


BG_DARK = "#0f172a"
BG_DARK_SECOND = "#1e293b"
GLASS_BG = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
GLASS_BORDER = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
TEXT_SLATE300 = "#cbd5e1"
TEXT_SLATE400 = "#94a3b8"
TEXT_SLATE500 = "#64748b"
GRADIENT_START = "#3b82f6"
GRADIENT_END = "#4f46e5"


class LoginPage:
    def __init__(self, page: ft.Page, on_success: callable):
        self._page = page
        self._on_success = on_success
        self._auth = AuthController()
        self._error_text: ft.Text | None = None
        self._progress: ft.ProgressRing | None = None
        self._btn: ft.ElevatedButton | None = None

    def build(self) -> ft.Control:
        self._error_text = ft.Text(
            "",
            color="#fca5a5",
            size=13,
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )

        self._progress = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2,
            color=ft.Colors.WHITE,
            visible=False,
        )

        username_field = ft.TextField(
            hint_text="Ingresa tu usuario",
            hint_style=ft.TextStyle(color=TEXT_SLATE500),
            label="Usuario",
            label_style=ft.TextStyle(color=TEXT_SLATE300, size=13),
            border_color=GLASS_BORDER,
            focused_border_color="#3b82f6",
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            color=ft.Colors.WHITE,
            text_size=15,
            content_padding=ft.Padding(left=16, top=14, right=16, bottom=14),
            cursor_color="#3b82f6",
        )

        password_field = ft.TextField(
            hint_text="Ingresa tu contrasena",
            hint_style=ft.TextStyle(color=TEXT_SLATE500),
            label="Contrasena",
            label_style=ft.TextStyle(color=TEXT_SLATE300, size=13),
            password=True,
            can_reveal_password=True,
            border_color=GLASS_BORDER,
            focused_border_color="#3b82f6",
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            color=ft.Colors.WHITE,
            text_size=15,
            content_padding=ft.Padding(left=16, top=14, right=16, bottom=14),
            cursor_color="#3b82f6",
        )

        self._btn = ft.ElevatedButton(
            content=ft.Row(
                [
                    self._progress,
                    ft.Text("Iniciar sesion", size=15, weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor=GRADIENT_END,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(left=0, top=16, right=0, bottom=16),
            ),
            on_click=lambda _: self._handle_login(username_field.value or "", password_field.value or ""),
        )

        login_card = ft.Container(
            content=ft.Column(
                [
                    self._error_text,
                    ft.Container(
                        content=ft.Column(
                            [
                                username_field,
                                ft.Container(height=8),
                                password_field,
                                ft.Container(height=12),
                                self._btn,
                            ],
                            spacing=0,
                        ),
                        padding=ft.Padding(left=24, top=24, right=24, bottom=24),
                        border_radius=16,
                        bgcolor=GLASS_BG,
                        border=ft.Border(left=ft.BorderSide(1, GLASS_BORDER), top=ft.BorderSide(1, GLASS_BORDER), right=ft.BorderSide(1, GLASS_BORDER), bottom=ft.BorderSide(1, GLASS_BORDER)),
                    ),
                ],
                spacing=16,
            ),
        )

        header = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.LOCK_ROUNDED,
                            size=40,
                            color=ft.Colors.WHITE,
                        ),
                        width=80,
                        height=80,
                        border_radius=16,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.TOP_LEFT,
                            end=ft.Alignment.BOTTOM_RIGHT,
                            colors=[GRADIENT_START, GRADIENT_END],
                        ),
                        alignment=ft.Alignment.CENTER,
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=16,
                            color=ft.Colors.with_opacity(0.3, GRADIENT_END),
                        ),
                    ),
                    ft.Container(height=16),
                    ft.Text(
                        "Bienvenido",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Inicia sesion para continuar",
                        size=13,
                        color=TEXT_SLATE400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            margin=ft.Margin(left=0, top=0, right=0, bottom=32),
        )

        credentials_hint = ft.Container(
            content=ft.Text(
                "Credenciales: mor_2314 / 83r5^_",
                size=11,
                color=TEXT_SLATE500,
                text_align=ft.TextAlign.CENTER,
            ),
            margin=ft.Margin(left=0, top=24, right=0, bottom=0),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(expand=True),
                    header,
                    login_card,
                    credentials_hint,
                    ft.Container(expand=True),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[BG_DARK, BG_DARK_SECOND],
            ),
            padding=ft.Padding(left=24, top=0, right=24, bottom=0),
        )

    def _handle_login(self, username: str, password: str) -> None:
        self._error_text.visible = False
        self._progress.visible = True
        self._btn.content.controls[1].value = "Iniciando sesion..."
        self._btn.disabled = True
        self._page.update()

        try:
            self._auth.login(username, password)
            self._on_success()
        except Exception as e:
            self._error_text.value = str(e)
            self._error_text.visible = True
        finally:
            self._progress.visible = False
            self._btn.content.controls[1].value = "Iniciar sesion"
            self._btn.disabled = False
            self._page.update()
