from __future__ import annotations

import flet as ft

from src.controllers.auth_controller import AuthController
from src.controllers.user_controller import UserController
from src.models import Role


BG_DARK = "#0f172a"
BG_DARK_SECOND = "#1e293b"
GLASS_BG = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
GLASS_BORDER = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
TEXT_SLATE300 = "#cbd5e1"
TEXT_SLATE400 = "#94a3b8"
TEXT_SLATE500 = "#64748b"
GRADIENT_START = "#3b82f6"
GRADIENT_END = "#4f46e5"

ROLE_STYLES = {
    Role.ADMIN: ("Administrador", "#ef4444", "#fef2f2"),
    Role.AUDITOR: ("Auditor", "#d97706", "#fffbeb"),
    Role.CLIENT: ("Cliente", "#16a34a", "#f0fdf4"),
}


class DashboardPage:
    def __init__(self, page: ft.Page, on_logout: callable):
        self._page = page
        self._on_logout = on_logout
        self._auth = AuthController()
        self._uc = UserController()

    def build(self) -> ft.Control:
        user = self._auth.current_user
        role = self._auth.current_role
        if user is None or role is None:
            return ft.Container()

        full_name = self._uc.get_full_name(user)
        role_label, role_fg, role_bg = ROLE_STYLES.get(role, ("?", TEXT_SLATE400, GLASS_BG))
        initial = user.name.firstname[:1].upper()

        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Mi Perfil", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.TextButton(
                        "Salir",
                        on_click=lambda _: self._handle_logout(),
                        style=ft.ButtonStyle(
                            color=TEXT_SLATE400,
                            padding=ft.Padding(left=4, top=4, right=4, bottom=4),
                        ),
                    ),
                ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, top=12, right=16, bottom=12),
            bgcolor=GLASS_BG,
            border=ft.Border(bottom=ft.BorderSide(1, GLASS_BORDER)),
        )

        profile_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text(initial, size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        width=80,
                        height=80,
                        border_radius=40,
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
                    ft.Text(full_name, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"@{user.username}", size=13, color=TEXT_SLATE400, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Text(role_label, size=11, weight=ft.FontWeight.W_700, color=role_fg),
                        padding=ft.Padding(left=12, top=4, right=12, bottom=4),
                        border_radius=20,
                        bgcolor=role_bg,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, top=24, right=24, bottom=24),
            border_radius=16,
            bgcolor=GLASS_BG,
            border=ft.Border(left=ft.BorderSide(1, GLASS_BORDER), top=ft.BorderSide(1, GLASS_BORDER), right=ft.BorderSide(1, GLASS_BORDER), bottom=ft.BorderSide(1, GLASS_BORDER)),
            margin=ft.Margin(left=0, top=0, right=0, bottom=16),
        )

        personal_card = self._build_section(
            "INFORMACION PERSONAL",
            [
                self._info_row(ft.Icons.EMAIL_OUTLINED, "Email", user.email),
                self._info_row(ft.Icons.PHONE_OUTLINED, "Telefono", user.phone),
            ],
        )

        address_card = self._build_section(
            "DIRECCION",
            [
                self._info_row(ft.Icons.MAP_OUTLINED, "Calle", f"{user.address.street} {user.address.number}"),
                self._info_row(ft.Icons.LOCATION_CITY_OUTLINED, "Ciudad", user.address.city),
                self._info_row(ft.Icons.BOOKMARK_OUTLINED, "Codigo Postal", user.address.zipcode),
            ],
        )

        geo_card = self._build_section(
            "GEOLOCALIZACION",
            [
                self._info_row(ft.Icons.LOCATION_ON_OUTLINED, "Latitud", user.address.geolocation.lat),
                self._info_row(ft.Icons.LOCATION_ON_OUTLINED, "Longitud", user.address.geolocation.long),
            ],
        )

        content = ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Column(
                        [
                            profile_card,
                            personal_card,
                            address_card,
                            geo_card,
                        ],
                        spacing=0,
                    ),
                    padding=ft.Padding(left=16, top=16, right=16, bottom=16),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

        return ft.Container(
            content=content,
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[BG_DARK, BG_DARK_SECOND],
            ),
        )

    def _build_section(self, title: str, children: list[ft.Control]) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        title,
                        size=11,
                        weight=ft.FontWeight.W_700,
                        color=TEXT_SLATE300,
                    ),
                    ft.Container(height=12),
                    *children,
                ],
                spacing=10,
            ),
            padding=ft.Padding(left=20, top=20, right=20, bottom=20),
            border_radius=16,
            bgcolor=GLASS_BG,
            border=ft.Border(left=ft.BorderSide(1, GLASS_BORDER), top=ft.BorderSide(1, GLASS_BORDER), right=ft.BorderSide(1, GLASS_BORDER), bottom=ft.BorderSide(1, GLASS_BORDER)),
            margin=ft.Margin(left=0, top=0, right=0, bottom=12),
        )

    def _info_row(self, icon: ft.IconName, label: str, value: str) -> ft.Control:
        return ft.Row(
            [
                ft.Icon(icon, size=18, color=TEXT_SLATE500),
                ft.Column(
                    [
                        ft.Text(label, size=11, color=TEXT_SLATE500),
                        ft.Text(value, size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=1,
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def _handle_logout(self) -> None:
        self._auth.logout()
        self._on_logout()
