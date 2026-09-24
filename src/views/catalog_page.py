<<<<<<< HEAD
=======
"""Vista del catalogo de productos (FakeStore API).

Carga las categorias y productos de forma asincrona, permite buscar y
filtrar, y muestra el detalle de cada producto en un dialogo.
"""

>>>>>>> julio
from __future__ import annotations

import asyncio

import flet as ft

<<<<<<< HEAD
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
=======
import src.config as config
from src.controllers.admin_controller import AdminController
from src.controllers.auth_controller import AuthController
from src.models import Role
from src.models.product import CATEGORIAS_LEGIBLES, Calificacion, Producto
from src.services.api_service import ApiService
from src.views.widgets import (
    boton_primario,
    calificacion_estrellas,
    campo_texto,
    tarjeta_producto,
)

BORDE_SUAVE = ft.border.Border.all(width=1, color=config.BORDE)


class CatalogPage:
    """Pantalla del catalogo: busqueda, filtros y cuadricula de productos."""

    def __init__(self, page: ft.Page, on_home) -> None:
        self._page = page
        self._on_home = on_home              # callback de volver al perfil
        self._api = ApiService()
        self._admin = AdminController()       # edicion de articulos
        self._auth = AuthController()
        # Solo quienes tienen rol de editor (administradores 1 y 2) editan.
        self._es_editor = self._auth.current_role is Role.ADMIN
        self._productos: list[Producto] = []
        self._categorias: list[str] = []
        self._filtro = ""                     # texto de busqueda
        self._categoria: str | None = None    # categoria seleccionada
        self._campo_busqueda = None
        self._selector_categoria = None
        self._contenido = None
        self._contador = None

    # ------------------------------------------------------------------
    # Construccion de la vista
    # ------------------------------------------------------------------
    def build(self) -> ft.Container:
        """Construye el esqueleto del catalogo (se llena de forma asincrona)."""
        self._campo_busqueda = ft.TextField(
            hint_text="Buscar producto...",
            prefix_icon=ft.Icons.SEARCH,
            filled=True,
            fill_color=config.GRAFITO,
            border_color=config.BORDE,
            focused_border_color=config.NARANJA,
            border_radius=12,
            content_padding=ft.Padding(left=14, top=6, right=14, bottom=6),
            hint_style=ft.TextStyle(color=config.TEXTO_ATENUADO),
            text_style=ft.TextStyle(color=config.TEXTO_PRIMARIO, size=14),
            on_change=self._on_buscar,
            expand=True,
        )

        # Selector de categoria; se rellena con las categorias de la API.
        self._selector_categoria = ft.Dropdown(
            hint_text="Todas las categorias",
            value="",
            filled=True,
            fill_color=config.GRAFITO,
            border_color=config.BORDE,
            focused_border_color=config.NARANJA,
            border_radius=12,
            text_size=13,
            on_select=self._on_categoria,
            expand=True,
        )

        boton_recargar = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=config.NARANJA_SUAVE,
            tooltip="Recargar catalogo",
            on_click=self._on_cargar,
        )

        self._contador = ft.Text(
            "Cargando...",
            size=12,
            color=config.TEXTO_ATENUADO,
        )

        cabecera = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "CATALOGO",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_ATENUADO,
                        ),
                        ft.Text(
                            "Nuestros productos",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_PRIMARIO,
                        ),
                    ],
                    spacing=0,
                ),
                ft.Icon(ft.Icons.STORE, size=26, color=config.NARANJA),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Zona central: se pinta con la cuadricula, estados de carga, etc.
        self._contenido = ft.Container(
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
            content=self._estado_cargando(),
        )

        navegacion = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Mi perfil"),
                ft.NavigationBarDestination(icon=ft.Icons.STORE, label="Catalogo"),
            ],
            selected_index=1,
            on_change=self._on_navegacion,
            bgcolor=config.CARBON,
        )

        encabezados = ft.Column(
            controls=[
                cabecera,
                ft.Row(controls=[self._campo_busqueda, boton_recargar], spacing=8),
                self._selector_categoria,
                self._contador,
            ],
            spacing=12,
        )

        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[config.NEGRO, config.CARBON, config.NEGRO],
            ),
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=encabezados,
                        padding=ft.Padding.all(16),
                    ),
                    self._contenido,
                    navegacion,
>>>>>>> julio
                ],
                spacing=0,
                expand=True,
            ),
<<<<<<< HEAD
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
=======
        )

    # ------------------------------------------------------------------
    # Estados de la zona central
    # ------------------------------------------------------------------
    def _estado_cargando(self) -> ft.Container:
        """Contenido mostrado mientras se descargan los productos."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(color=config.NARANJA, stroke_width=4),
                    ft.Text("Cargando catalogo...", size=13, color=config.TEXTO_SECUNDARIO),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    def _estado_error(self, mensaje: str) -> ft.Container:
        """Contenido mostrado cuando falla la descarga."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.CLOUD_OFF, size=42, color=config.TEXTO_ATENUADO),
                    ft.Text(mensaje, size=13, color=config.TEXTO_SECUNDARIO, text_align=ft.TextAlign.CENTER),
                    ft.TextButton("Reintentar", on_click=self._on_cargar),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    def _estado_vacio(self) -> ft.Container:
        """Contenido mostrado cuando no hay coincidencias con la busqueda."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SEARCH_OFF, size=42, color=config.TEXTO_ATENUADO),
                    ft.Text("Sin resultados", size=13, color=config.TEXTO_SECUNDARIO),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    # ------------------------------------------------------------------
    # Carga asincrona de datos desde la API
    # ------------------------------------------------------------------
    async def _cargar(self) -> None:
        """Descarga categorias y productos, luego pinta la cuadricula."""
        self._contenido.content = self._estado_cargando()
        self._page.update()

        try:
            # La red se ejecuta fuera del hilo principal para no congelar la UI.
            categorias = await asyncio.to_thread(self._api.obtener_categorias)
            productos = await asyncio.to_thread(self._api.obtener_productos)
        except Exception:
            self._productos = []
            self._contenido.content = self._estado_error(
                "No se pudo cargar el catalogo. Revisa tu conexion."
            )
            self._page.update()
            return

        self._productos = productos
        self._categorias = categorias
        # Poblar el selector de categorias (traducidas al espanol).
        self._selector_categoria.options = [
            ft.DropdownOption(key="", text="Todas las categorias")
        ] + [
            ft.DropdownOption(key=c, text=CATEGORIAS_LEGIBLES.get(c, c))
            for c in categorias
        ]
        self._pintar()

    def _on_cargar(self, e) -> None:
        """Recarga el catalogo desde la API (handler de boton)."""
        self._page.run_task(self._cargar)

    # ------------------------------------------------------------------
    # Pintado y filtrado de la cuadricula
    # ------------------------------------------------------------------
    def _pintar(self) -> None:
        """Aplica busqueda + categoria y redibuja la cuadricula de productos."""
        texto = self._filtro.lower()
        filtrados = [
            p
            for p in self._productos
            if texto in p.titulo.lower()
            and (self._categoria is None or p.categoria == self._categoria)
        ]

        self._contador.value = f"{len(filtrados)} producto(s)"

        if not filtrados:
            estado = self._estado_vacio()
        else:
            estado = ft.GridView(
                controls=[
                    tarjeta_producto(
                        p,
                        on_click=lambda e, prod=p: self._abrir_detalle(prod),
                        # El recuadro de editar solo existe para los editores.
                        on_editar=(
                            (lambda prod=p: self._abrir_edicion(prod))
                            if self._es_editor
                            else None
                        ),
                    )
                    for p in filtrados
                ],
                runs_count=2,
                spacing=2,
                run_spacing=2,
                child_aspect_ratio=0.9,
                padding=ft.Padding.all(2),
            )

        if self._contenido is not None:
            self._contenido.content = estado
            self._page.update()

    def _on_buscar(self, e) -> None:
        """Actualiza el filtro de busqueda y repinta."""
        self._filtro = e.control.value or ""
        self._pintar()

    def _on_categoria(self, e) -> None:
        """Cambia la categoria y recarga el catalogo desde la API."""
        self._categoria = e.control.value or None
        self._page.run_task(self._cargar)

    def _on_navegacion(self, e) -> None:
        """Vuelve al perfil al pulsar la pestana 'Mi perfil'."""
        if e.control.selected_index == 0:
            self._on_home()

    # ------------------------------------------------------------------
    # Dialogo de detalle de un producto
    # ------------------------------------------------------------------
    def _abrir_detalle(self, producto: Producto) -> None:
        """Muestra todos los detalles de un producto en un dialogo."""
        estrellas = calificacion_estrellas(producto.calificacion.tasa, tamano=16)

        detalle = ft.AlertDialog(
            modal=True,
            bgcolor=config.GRAFITO,
            content=ft.Container(
                width=350,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Image(
                                src=producto.imagen,
                                fit=ft.BoxFit.CONTAIN,
                                error_content=ft.Icon(
                                    ft.Icons.BROKEN_IMAGE_OUTLINED,
                                    size=48,
                                    color=config.TEXTO_ATENUADO,
                                ),
                            ),
                            height=200,
                            bgcolor=config.SUPERFICIE,
                            border_radius=ft.BorderRadius.all(12),
                            alignment=ft.Alignment.CENTER,
                            padding=ft.Padding.all(12),
                        ),
                        ft.Text(
                            producto.titulo,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_PRIMARIO,
                        ),
                        ft.Text(
                            producto.nombre_categoria(),
                            size=12,
                            color=config.TEXTO_ATENUADO,
                        ),
                        ft.Row(
                            controls=[
                                estrellas,
                                ft.Text(
                                    f"{producto.calificacion.tasa:.1f} "
                                    f"({producto.calificacion.conteo} votos)",
                                    size=12,
                                    color=config.TEXTO_SECUNDARIO,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Text(
                            producto.precio_formateado(),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=config.NARANJA,
                        ),
                        ft.Divider(color=config.BORDE),
                        ft.Text(
                            producto.descripcion,
                            size=12,
                            color=config.TEXTO_SECUNDARIO,
                        ),
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._cerrar(detalle)),
            ],
        )
        self._page.show_dialog(detalle)

    def _cerrar(self, dialogo: ft.AlertDialog) -> None:
        """Cierra el dialogo de detalle."""
        dialogo.open = False
        self._page.update()

    # ------------------------------------------------------------------
    # Edicion desde el catalogo (solo para editores/administradores)
    # ------------------------------------------------------------------
    def _opciones_categorias(self) -> list[ft.DropdownOption]:
        """Opciones del selector de categorias (traducidas al espanol)."""
        return [
            ft.DropdownOption(key=c, text=CATEGORIAS_LEGIBLES.get(c, c))
            for c in self._categorias
        ]

    def _abrir_edicion(self, producto: Producto) -> None:
        """Abre el dialogo para editar un articulo sin salir del catalogo."""
        campo_titulo = campo_texto("Titulo", hint="Nombre del articulo")
        campo_precio = campo_texto("Precio", hint="Ej: 19.99")
        campo_imagen = campo_texto("Url de imagen", hint="https://...")
        campo_descripcion = campo_texto("Descripcion", hint="Detalles del articulo")

        selector_categoria = ft.Dropdown(
            hint_text="Categoria",
            filled=True,
            fill_color=config.GRAFITO,
            border_color=config.BORDE,
            focused_border_color=config.NARANJA,
            border_radius=12,
            text_size=13,
            options=self._opciones_categorias(),
            expand=True,
        )

        campo_titulo.value = producto.titulo
        campo_precio.value = f"{producto.precio:.2f}"
        campo_imagen.value = producto.imagen
        campo_descripcion.value = producto.descripcion
        selector_categoria.value = producto.categoria

        error_texto = ft.Text("", size=12, color=config.ERROR)

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar articulo", color=config.TEXTO_PRIMARIO),
            bgcolor=config.GRAFITO,
            content=ft.Container(
                width=350,
                content=ft.Column(
                    controls=[
                        campo_titulo,
                        campo_precio,
                        selector_categoria,
                        campo_imagen,
                        campo_descripcion,
                        error_texto,
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._cerrar(dialogo)),
                boton_primario(
                    "Guardar",
                    on_click=lambda e: self._guardar_clic(
                        dialogo, campo_titulo, campo_precio, selector_categoria,
                        campo_imagen, campo_descripcion, error_texto, producto,
                    ),
                    icono=ft.Icons.CHECK,
                    expand=False,
                ),
            ],
        )
        self._page.show_dialog(dialogo)

    def _guardar_clic(self, dialogo, campo_titulo, campo_precio, selector, campo_imagen, campo_descripcion, error_texto, producto) -> None:
        """Arranca la tarea de guardado de la edicion."""
        self._page.run_task(
            self._guardar_edicion,
            dialogo,
            campo_titulo,
            campo_precio,
            selector,
            campo_imagen,
            campo_descripcion,
            error_texto,
            producto,
        )

    async def _guardar_edicion(self, dialogo, campo_titulo, campo_precio, selector, campo_imagen, campo_descripcion, error_texto, producto) -> None:
        """Valida la edicion, la guarda y refresca el catalogo."""
        titulo = (campo_titulo.value or "").strip()
        precio_texto = (campo_precio.value or "").strip().replace(",", ".")
        categoria = selector.value or ""

        if not titulo or not precio_texto or not categoria:
            error_texto.value = "Completa al menos titulo, precio y categoria."
            self._page.update()
            return

        try:
            precio = float(precio_texto)
            if precio <= 0:
                raise ValueError
        except ValueError:
            error_texto.value = "Precio invalido. Escribe un numero mayor a 0."
            self._page.update()
            return

        nuevo = Producto(
            titulo=titulo,
            precio=precio,
            descripcion=(campo_descripcion.value or "").strip(),
            categoria=categoria,
            imagen=(campo_imagen.value or "").strip(),
            calificacion=Calificacion(),
        )

        # Guardar en un hilo aparte para no bloquear la interfaz.
        await asyncio.to_thread(self._admin.actualizar_articulo, nuevo, producto.id)
        self._cerrar(dialogo)
        self._mostrar_snack("Articulo modificado correctamente")
        await self._cargar()

    def _mostrar_snack(self, mensaje: str) -> None:
        """Muestra una notificacion breve al usuario."""
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=config.TEXTO_PRIMARIO),
            bgcolor=config.SUPERFICIE,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self._page.overlay.append(snack)
        snack.open = True
        self._page.update()
>>>>>>> julio
