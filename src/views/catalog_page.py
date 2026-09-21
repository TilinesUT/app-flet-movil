from __future__ import annotations

import asyncio

import flet as ft

from src.models.product import Product
from src.services.api_service import ApiService


BG_DARK = "#0f172a"
BG_DARK_SECOND = "#1e293b"
GLASS_BG = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
GLASS_BORDER = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
TEXT_SLATE300 = "#cbd5e1"
TEXT_SLATE400 = "#94a3b8"
TEXT_SLATE500 = "#64748b"
GRADIENT_START = "#3b82f6"
GRADIENT_END = "#4f46e5"

ALL_CATEGORIES = "ver_todos"


def format_price(price: float) -> str:
    return f"${price:,.2f}"


class CatalogPage:
    def __init__(
        self,
        page: ft.Page,
        on_open_product: callable,
        on_open_profile: callable,
        on_logout: callable,
    ):
        self._page = page
        self._on_open_product = on_open_product
        self._on_open_profile = on_open_profile
        self._on_logout = on_logout
        self._api = ApiService()
        self._products: list[Product] = []
        self._categories: list[str] = []
        self._selected_category: str | None = None
        self._content: ft.Container | None = None
        self._chip_row: ft.Row | None = None

    def build(self) -> ft.Control:
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Catalogo", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row(
                        [
                            ft.TextButton(
                                "Perfil",
                                on_click=lambda _: self._on_open_profile(),
                                style=ft.ButtonStyle(
                                    color=TEXT_SLATE400,
                                    padding=ft.Padding(left=4, top=4, right=4, bottom=4),
                                ),
                            ),
                            ft.TextButton(
                                "Salir",
                                on_click=lambda _: self._on_logout(),
                                style=ft.ButtonStyle(
                                    color=TEXT_SLATE400,
                                    padding=ft.Padding(left=4, top=4, right=8, bottom=4),
                                ),
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, top=12, right=8, bottom=12),
            bgcolor=GLASS_BG,
            border=ft.Border(bottom=ft.BorderSide(1, GLASS_BORDER)),
        )

        self._chip_row = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)

        self._content = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=self._loading_view(),
        )

        root = ft.Container(
            content=ft.Column(
                [
                    header,
                    self._chip_row,
                    self._content,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[BG_DARK, BG_DARK_SECOND],
            ),
        )

        self._page.run_task(self._load_initial_async)

        return root

    async def _load_initial_async(self) -> None:
        await asyncio.sleep(0)
        self._load_categories()

    def _loading_view(self) -> ft.Control:
        return ft.Column(
            [
                ft.ProgressRing(width=40, height=40, stroke_width=4, color=GRADIENT_START),
                ft.Container(height=16),
                ft.Text("Cargando catalogo...", size=13, color=TEXT_SLATE400),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _error_view(self, message: str, retry: callable) -> ft.Control:
        return ft.Column(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=TEXT_SLATE500),
                ft.Container(height=12),
                ft.Text(message, size=14, color=TEXT_SLATE300, text_align=ft.TextAlign.CENTER),
                ft.Container(height=16),
                ft.FilledButton(
                    "Reintentar",
                    on_click=lambda _: retry(),
                    style=ft.ButtonStyle(bgcolor=GRADIENT_END, color=ft.Colors.WHITE),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _empty_view(self) -> ft.Control:
        return ft.Column(
            [
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=48, color=TEXT_SLATE500),
                ft.Container(height=12),
                ft.Text("No hay productos para mostrar", size=14, color=TEXT_SLATE300),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _set_content(self, control: ft.Control) -> None:
        self._content.content = control
        self._page.update()

    def _load_categories(self) -> None:
        try:
            self._categories = self._api.get_categories()
        except Exception:
            self._categories = []
        self._render_chips()
        self._load_products()

    def _render_chips(self) -> None:
        chips = [self._chip(ALL_CATEGORIES, "Ver todos")]
        for category in self._categories:
            chips.append(self._chip(category, category.upper().replace("-", " ")))
        self._chip_row.controls = chips
        self._page.update()

    def _chip(self, category: str, label: str) -> ft.Control:
        is_selected = self._selected_category == category
        return ft.Chip(
            label=ft.Text(label, size=12, color=ft.Colors.WHITE),
            bgcolor=GRADIENT_END if is_selected else ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
            on_click=lambda _: self._select_category(category),
        )

    def _select_category(self, category: str) -> None:
        self._selected_category = None if category == ALL_CATEGORIES else category
        self._render_chips()
        self._load_products()

    def _load_products(self) -> None:
        self._products = []
        self._set_content(self._loading_view())

        try:
            if self._selected_category is None:
                self._products = self._api.get_products()
            else:
                self._products = self._api.get_products_by_category(self._selected_category)
        except Exception:
            self._set_content(self._error_view("No pudimos cargar los productos.", self._load_products))
            return

        if self._products:
            self._set_content(self._products_view())
        else:
            self._set_content(self._empty_view())

    def _products_view(self) -> ft.Control:
        return ft.ListView(
            spacing=12,
            padding=ft.Padding(left=16, top=16, right=16, bottom=16),
            controls=[self._product_card(product) for product in self._products],
        )

    def _product_card(self, product: Product) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=72,
                        height=72,
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                        content=ft.Image(
                            src=product.image,
                            width=72,
                            height=72,
                            fit=ft.ImageFit.COVER,
                            error_content=ft.Icon(ft.Icons.BROKEN_IMAGE_OUTLINED, size=28, color=TEXT_SLATE500),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                product.title,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Container(height=4),
                            ft.Text(format_price(product.price), size=15, weight=ft.FontWeight.BOLD, color=GRADIENT_START),
                            ft.Container(height=2),
                            ft.Text(
                                product.category.upper().replace("-", " "),
                                size=11,
                                color=TEXT_SLATE500,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=20, color=TEXT_SLATE500),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, top=12, right=12, bottom=12),
            border_radius=16,
            bgcolor=GLASS_BG,
            border=ft.Border(left=ft.BorderSide(1, GLASS_BORDER), top=ft.BorderSide(1, GLASS_BORDER), right=ft.BorderSide(1, GLASS_BORDER), bottom=ft.BorderSide(1, GLASS_BORDER)),
            on_click=lambda _: self._on_open_product(product.id),
        )