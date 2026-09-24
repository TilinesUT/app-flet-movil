"""Vista del catalogo de productos (FakeStore API).

Carga las categorias y productos de forma asincrona, permite buscar y
filtrar, y muestra el detalle de cada producto en un dialogo.
"""

from __future__ import annotations

import asyncio

import flet as ft

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
                ],
                spacing=0,
                expand=True,
            ),
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