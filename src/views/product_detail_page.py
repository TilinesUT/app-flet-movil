from __future__ import annotations

import asyncio

import flet as ft

from src.controllers.auth_controller import AuthController
from src.models import Role
from src.models.product import Product, Rating
from src.services.api_service import ApiService
from src.views.catalog_page import format_price


BG_DARK = "#0f172a"
BG_DARK_SECOND = "#1e293b"
GLASS_BG = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
GLASS_BORDER = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
TEXT_SLATE300 = "#cbd5e1"
TEXT_SLATE400 = "#94a3b8"
TEXT_SLATE500 = "#64748b"
GRADIENT_START = "#3b82f6"
GRADIENT_END = "#4f46e5"


class ProductDetailPage:
    def __init__(self, page: ft.Page, product_id: int, on_back: callable):
        self._page = page
        self._product_id = product_id
        self._on_back = on_back
        self._api = ApiService()
        self._auth = AuthController()
        self._product: Product | None = None
        self._content: ft.Container | None = None
        self._is_admin = self._auth.current_role is Role.ADMIN

    def build(self) -> ft.Control:
        header = ft.Container(
            content=ft.Row(
                [
                    ft.TextButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ARROW_BACK, size=18),
                                ft.Text("Volver", size=14),
                            ],
                            spacing=4,
                        ),
                        on_click=lambda _: self._on_back(),
                        style=ft.ButtonStyle(color=TEXT_SLATE300, padding=ft.Padding(left=4, top=4, right=8, bottom=4)),
                    ),
                    ft.Text("Detalle", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(width=16),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=8, top=12, right=16, bottom=12),
            bgcolor=GLASS_BG,
            border=ft.Border(bottom=ft.BorderSide(1, GLASS_BORDER)),
        )

        self._content = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=self._loading_view(),
        )

        root = ft.Container(
            content=ft.Column(
                [
                    header,
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
        self._load()

    def _loading_view(self) -> ft.Control:
        return ft.Column(
            [
                ft.ProgressRing(width=40, height=40, stroke_width=4, color=GRADIENT_START),
                ft.Container(height=16),
                ft.Text("Cargando producto...", size=13, color=TEXT_SLATE400),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _set_content(self, control: ft.Control) -> None:
        self._content.content = control
        self._page.update()

    def _load(self) -> None:
        try:
            self._product = self._api.get_product(self._product_id)
            self._set_content(self._detail_view())
        except Exception:
            self._show_unavailable()

    def _show_unavailable(self) -> None:
        self._set_content(ft.Container())

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Producto no disponible"),
            content=ft.Text("No se pudo cargar el detalle del producto."),
            actions=[
                ft.TextButton(
                    "Volver al catalogo",
                    on_click=lambda _: self._close_and_back(dialog),
                ),
            ],
        )
        self._page.open(dialog)

    def _close_and_back(self, dialog: ft.AlertDialog) -> None:
        self._page.close(dialog)
        self._on_back()

    def _detail_view(self) -> ft.Control:
        product = self._product
        if product is None:
            return self._loading_view()

        image = ft.Container(
            height=240,
            border_radius=20,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            alignment=ft.Alignment.CENTER,
            content=ft.Image(
                src=product.image,
                height=240,
                fit=ft.ImageFit.CONTAIN,
                error_content=ft.Icon(ft.Icons.BROKEN_IMAGE_OUTLINED, size=48, color=TEXT_SLATE500),
            ),
        )

        rating = product.rating
        rating_text = f"{rating.rate:.1f} ({rating.count} resenas)" if rating.count else "Sin resenas"

        children: list[ft.Control] = [
            image,
            ft.Container(height=16),
            ft.Text(product.title, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Text(format_price(product.price), size=22, weight=ft.FontWeight.BOLD, color=GRADIENT_START),
                    ft.Chip(
                        label=ft.Text(product.category.upper().replace("-", " "), size=12, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Icon(ft.Icons.STAR_ROUNDED, size=16, color=ft.Colors.AMBER),
                    ft.Text(rating_text, size=13, color=TEXT_SLATE400),
                ],
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=16),
            ft.Text("DESCRIPCION", size=11, weight=ft.FontWeight.W_700, color=TEXT_SLATE300),
            ft.Container(height=8),
            ft.Text(product.description, size=14, color=TEXT_SLATE300),
            ft.Container(height=16),
        ]

        if self._is_admin:
            children.append(
                ft.Row(
                    [
                        ft.FilledButton(
                            "Editar",
                            icon=ft.Icons.EDIT_OUTLINED,
                            on_click=lambda _: self._open_edit_dialog(),
                            style=ft.ButtonStyle(bgcolor=GRADIENT_END, color=ft.Colors.WHITE),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            "Eliminar",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=lambda _: self._confirm_delete(),
                            style=ft.ButtonStyle(
                                color="#f87171",
                                side=ft.BorderSide(1, "#f87171"),
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=12,
                )
            )

        return ft.ListView(
            spacing=0,
            padding=ft.Padding(left=16, top=16, right=16, bottom=24),
            controls=children,
        )

    def _confirm_delete(self) -> None:
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar producto"),
            content=ft.Text("Esta accion no se puede deshacer. Deseas continuar?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self._page.close(dialog)),
                ft.FilledButton(
                    content=ft.Text("Eliminar"),
                    on_click=lambda _: self._delete(dialog),
                    style=ft.ButtonStyle(bgcolor="#dc2626", color=ft.Colors.WHITE),
                ),
            ],
        )
        self._page.open(dialog)

    def _delete(self, dialog: ft.AlertDialog) -> None:
        self._page.close(dialog)
        try:
            self._api.delete_product(self._product_id)
            self._page.open(
                ft.SnackBar(
                    ft.Text("Producto eliminado"),
                    bgcolor=ft.Colors.GREEN_600,
                )
            )
            self._on_back()
        except Exception:
            self._page.open(
                ft.SnackBar(
                    ft.Text("No se pudo eliminar el producto"),
                    bgcolor=ft.Colors.RED_600,
                )
            )

    def _open_edit_dialog(self) -> None:
        product = self._product
        if product is None:
            return

        error_text = ft.Text("", size=12, color="#fca5a5", visible=False)

        title_field = ft.TextField(label="Titulo", value=product.title, text_size=14)
        price_field = ft.TextField(label="Precio", value=str(product.price), text_size=14, keyboard_type=ft.KeyboardType.NUMBER)
        category_field = ft.TextField(label="Categoria", value=product.category, text_size=14)
        description_field = ft.TextField(label="Descripcion", value=product.description, text_size=14, multiline=True, min_lines=3, max_lines=5)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar producto"),
            content=ft.Column(
                [
                    error_text,
                    title_field,
                    price_field,
                    category_field,
                    description_field,
                ],
                spacing=8,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self._page.close(dialog)),
                ft.FilledButton(
                    content=ft.Text("Guardar"),
                    on_click=lambda _: self._save_edit(
                        dialog,
                        error_text,
                        title_field.value or "",
                        price_field.value or "",
                        category_field.value or "",
                        description_field.value or "",
                    ),
                    style=ft.ButtonStyle(bgcolor=GRADIENT_END, color=ft.Colors.WHITE),
                ),
            ],
        )
        self._page.open(dialog)

    def _save_edit(
        self,
        dialog: ft.AlertDialog,
        error_text: ft.Text,
        title: str,
        price: str,
        category: str,
        description: str,
    ) -> None:
        if not title or not price or not category:
            error_text.value = "Titulo, precio y categoria son obligatorios."
            error_text.visible = True
            self._page.update()
            return

        try:
            new_price = float(price)
        except ValueError:
            error_text.value = "El precio debe ser un numero valido."
            error_text.visible = True
            self._page.update()
            return

        edited = Product(
            id=self._product_id,
            title=title,
            price=new_price,
            description=description,
            category=category,
            image=self._product.image if self._product is not None else "",
            rating=self._product.rating if self._product is not None else Rating(),
        )

        self._page.close(dialog)
        try:
            self._api.update_product(edited)
            self._page.open(
                ft.SnackBar(
                    ft.Text("Producto actualizado"),
                    bgcolor=ft.Colors.GREEN_600,
                )
            )
            self._load()
        except Exception:
            self._page.open(
                ft.SnackBar(
                    ft.Text("No se pudo actualizar el producto"),
                    bgcolor=ft.Colors.RED_600,
                )
            )