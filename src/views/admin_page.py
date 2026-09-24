"""Vista del panel de administracion (solo administradores).

Permite gestionar los articulos del catalogo (crear, editar, eliminar),
consultar estadisticas y revisar los permisos tipicos del rol, todo
visible unicamente para usuarios con cedigo de administrador.
"""

from __future__ import annotations

import asyncio

import flet as ft

import src.config as config
from src.controllers.admin_controller import AdminController
from src.controllers.auth_controller import AuthController
from src.models.product import Calificacion, Producto
from src.views.widgets import boton_primario, campo_texto

BORDE_SUAVE = ft.border.Border.all(width=1, color=config.BORDE)


class AdminPage:
    """Pantalla de administracion: articulos, estadisticas y permisos."""

    def __init__(self, page: ft.Page, on_home, on_catalog) -> None:
        self._page = page
        self._on_home = on_home          # callback de ir al perfil
        self._on_catalog = on_catalog    # callback de ir al catalogo
        self._admin = AdminController()
        self._auth = AuthController()
        self._productos: list[Producto] = []
        self._categorias: list[str] = []
        self._filtro = ""
        self._campo_busqueda = None
        self._contenido = None
        self._contador = None
        self._stat_total = None
        self._stat_categorias = None
        self._stat_precio = None

    # ------------------------------------------------------------------
    # Control de acceso
    # ------------------------------------------------------------------
    def _acceso_denegado(self) -> ft.Container:
        """Pantalla mostrada si un usuario sin rol admin intenta entrar."""
        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[config.NEGRO, config.CARBON, config.NEGRO],
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(24),
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SHIELD_OUTLINED, size=56, color=config.ERROR),
                    ft.Text(
                        "Acceso denegado",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=config.TEXTO_PRIMARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Esta opcion solo esta disponible para administradores "
                        "(codigos 1 y 2).",
                        size=13,
                        color=config.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    boton_primario("Volver al perfil", self._on_home, icono=ft.Icons.PERSON),
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # ------------------------------------------------------------------
    # Construccion de la vista
    # ------------------------------------------------------------------
    def build(self) -> ft.Container:
        """Construye el panel; si no hay sesion admin devuelve acceso denegado."""
        if not self._admin.es_administrador(self._auth.current_role):
            return self._acceso_denegado()

        self._campo_busqueda = ft.TextField(
            hint_text="Buscar articulo...",
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

        boton_nuevo = boton_primario(
            "Nuevo articulo",
            self._abrir_formulario,
            icono=ft.Icons.ADD,
            expand=False,
        )

        self._contador = ft.Text("Cargando...", size=12, color=config.TEXTO_ATENUADO)

        cabecera = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "PANEL DE ADMINISTRADOR",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_ATENUADO,
                        ),
                        ft.Text(
                            "Gestion del sistema",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_PRIMARIO,
                        ),
                    ],
                    spacing=0,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=24, color=config.NEGRO),
                    width=46,
                    height=46,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=config.NARANJA,
                    border_radius=ft.BorderRadius.all(14),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Mini estadisticas del catalogo.
        self._stat_total = ft.Text("...", size=16, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO)
        self._stat_categorias = ft.Text("...", size=16, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO)
        self._stat_precio = ft.Text("...", size=16, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO)
        fila_stats = ft.Row(
            controls=[
                self._mini_stat(ft.Icons.INVENTORY, "Articulos", self._stat_total),
                self._mini_stat(ft.Icons.CATEGORY, "Categorias", self._stat_categorias),
                self._mini_stat(ft.Icons.PRICE_CHANGE, "Precio prom.", self._stat_precio),
            ],
            spacing=8,
        )

        # Permisos tipicos del administrador.
        permisos_card = self._tarjeta("Permisos de administrador", [
            self._fila_permiso(p) for p in self._admin.permisos_administrador()
        ])

        # Zona central: lista de articulos a gestionar.
        self._contenido = ft.Container(
            expand=True,
            content=self._estado_cargando(),
        )

        navegacion = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Mi perfil"),
                ft.NavigationBarDestination(icon=ft.Icons.STORE, label="Catalogo"),
                ft.NavigationBarDestination(icon=ft.Icons.ADMIN_PANEL_SETTINGS, label="Admin"),
            ],
            selected_index=2,
            on_change=self._on_navegacion,
            bgcolor=config.CARBON,
        )

        encabezados = ft.Column(
            controls=[
                cabecera,
                fila_stats,
                permisos_card,
                ft.Row(controls=[self._campo_busqueda, boton_nuevo], spacing=8),
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
                    ft.Container(content=encabezados, padding=ft.Padding.all(16)),
                    self._contenido,
                    navegacion,
                ],
                spacing=0,
                expand=True,
            ),
        )

    # ------------------------------------------------------------------
    # Componentes auxiliares
    # ------------------------------------------------------------------
    def _tarjeta(self, titulo: str, hijos: list[ft.Control]) -> ft.Container:
        """Tarjeta con titulo y contenido."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(titulo.upper(), size=12, weight=ft.FontWeight.BOLD, color=config.TEXTO_SECUNDARIO),
                    *hijos,
                ],
                spacing=8,
            ),
            padding=ft.Padding.all(12),
            bgcolor=config.SUPERFICIE,
            border_radius=ft.BorderRadius.all(12),
            border=BORDE_SUAVE,
        )

    def _mini_stat(self, icono: str, etiqueta: str, valor: ft.Text) -> ft.Container:
        """Tarjeta pequeña con una estadistica numerica."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icono, size=16, color=config.NARANJA_SUAVE),
                    valor,
                    ft.Text(etiqueta, size=9, weight=ft.FontWeight.BOLD, color=config.TEXTO_ATENUADO),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            bgcolor=config.SUPERFICIE,
            border_radius=ft.BorderRadius.all(12),
            border=BORDE_SUAVE,
            padding=ft.Padding.all(10),
        )

    def _fila_permiso(self, permiso: dict) -> ft.Row:
        """Fila de un permiso: icono, titulo, detalle y estado."""
        color_estado = config.EXITO if permiso["funcional"] else config.NARANJA_SUAVE
        icono_estado = ft.Icons.CHECK_CIRCLE if permiso["funcional"] else ft.Icons.HOURGLASS_TOP
        estado = "ACTIVO" if permiso["funcional"] else "PLANTEADO"
        return ft.Row(
            controls=[
                ft.Icon(getattr(ft.Icons, permiso["icono"]), size=18, color=config.NARANJA),
                ft.Column(
                    controls=[
                        ft.Text(permiso["titulo"], size=13, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO),
                        ft.Text(permiso["detalle"], size=11, color=config.TEXTO_SECUNDARIO),
                    ],
                    spacing=1,
                    expand=True,
                ),
                ft.Icon(icono_estado, size=16, color=color_estado),
                ft.Text(estado, size=9, weight=ft.FontWeight.BOLD, color=color_estado),
            ],
            spacing=8,
        )

    # ------------------------------------------------------------------
    # Estados de la zona central
    # ------------------------------------------------------------------
    def _estado_cargando(self) -> ft.Container:
        """Contenido mientras se cargan los articulos."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(color=config.NARANJA, stroke_width=4),
                    ft.Text("Cargando articulos...", size=13, color=config.TEXTO_SECUNDARIO),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    def _estado_error(self, mensaje: str) -> ft.Container:
        """Contenido cuando falla la carga."""
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
        """Contenido cuando no hay articulos que coincidan."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SEARCH_OFF, size=42, color=config.TEXTO_ATENUADO),
                    ft.Text("Sin articulos", size=13, color=config.TEXTO_SECUNDARIO),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(top=48),
        )

    # ------------------------------------------------------------------
    # Carga y pintado
    # ------------------------------------------------------------------
    async def _cargar(self) -> None:
        """Descarga categorias, articulos y estadisticas, y pinta la lista."""
        # Seguridad: solo un administrador puede ver o cargar el panel.
        if not self._admin.es_administrador(self._auth.current_role):
            return
        self._contenido.content = self._estado_cargando()
        self._page.update()

        try:
            # Red fuera del hilo principal para no congelar la interfaz.
            categorias = await asyncio.to_thread(self._admin.categorias)
            productos = await asyncio.to_thread(self._admin.obtener_articulos)
            stats = await asyncio.to_thread(self._admin.estadisticas)
        except Exception:
            self._contenido.content = self._estado_error(
                "No se pudo cargar el panel de administracion."
            )
            self._page.update()
            return

        self._categorias = categorias
        self._productos = productos
        self._stat_total.value = str(stats["total"])
        self._stat_categorias.value = str(stats["categorias"])
        self._stat_precio.value = f"${stats['precio_promedio']:.2f}"
        self._pintar()

    def _on_cargar(self, e) -> None:
        """Recarga el panel (handler de los botones de reintentar)."""
        self._page.run_task(self._cargar)

    def _pintar(self) -> None:
        """Filtra por la busqueda y pinta la lista de articulos."""
        texto = self._filtro.lower()
        filtrados = [p for p in self._productos if texto in p.titulo.lower()]
        self._contador.value = f"{len(filtrados)} articulo(s)"

        if not filtrados:
            estado = self._estado_vacio()
        else:
            estado = ft.ListView(
                controls=[self._fila_articulo(p) for p in filtrados],
                spacing=8,
                padding=ft.Padding.all(2),
                expand=True,
            )

        if self._contenido is not None:
            self._contenido.content = estado
            self._page.update()

    def _on_buscar(self, e) -> None:
        """Actualiza el filtro de busqueda y repinta."""
        self._filtro = e.control.value or ""
        self._pintar()

    def _on_navegacion(self, e) -> None:
        """Navega al perfil o al catalogo segun la pestana elegida."""
        indice = e.control.selected_index
        if indice == 0:
            self._on_home()
        elif indice == 1:
            self._on_catalog()

    def _fila_articulo(self, producto: Producto) -> ft.Container:
        """Fila del listado: imagen, datos y botones editar/eliminar."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Image(
                            src=producto.imagen,
                            fit=ft.BoxFit.CONTAIN,
                            error_content=ft.Icon(ft.Icons.IMAGE_OUTLINED, size=20, color=config.TEXTO_ATENUADO),
                        ),
                        width=56,
                        height=56,
                        bgcolor=config.GRAFITO,
                        border_radius=ft.BorderRadius.all(10),
                        alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.all(4),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(producto.titulo, size=13, weight=ft.FontWeight.BOLD, color=config.TEXTO_PRIMARIO, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(
                                f"{self._admin.nombre_categoria(producto.categoria)}  ·  {producto.precio_formateado()}",
                                size=11,
                                color=config.TEXTO_ATENUADO,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=config.NARANJA_SUAVE,
                        tooltip="Editar articulo",
                        on_click=lambda e, prod=producto: self._abrir_formulario(prod),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=config.ERROR,
                        tooltip="Eliminar articulo",
                        on_click=lambda e, prod=producto: self._pedir_eliminacion(prod),
                    ),
                ],
                spacing=8,
            ),
            bgcolor=config.SUPERFICIE,
            border_radius=ft.BorderRadius.all(12),
            border=BORDE_SUAVE,
            padding=ft.Padding.all(10),
        )

    # ------------------------------------------------------------------
    # Formulario: crear / editar articulo
    # ------------------------------------------------------------------
    def _opciones_categorias(self) -> list[ft.DropdownOption]:
        """Opciones del selector de categorias (traducidas)."""
        from src.models.product import CATEGORIAS_LEGIBLES

        return [
            ft.DropdownOption(key=c, text=CATEGORIAS_LEGIBLES.get(c, c))
            for c in self._categorias
        ]

    def _abrir_formulario(self, producto: Producto | None = None) -> None:
        """Abre el dialogo para crear (None) o editar (Producto) un articulo."""
        editando = producto is not None

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

        if editando:
            campo_titulo.value = producto.titulo
            campo_precio.value = f"{producto.precio:.2f}"
            campo_imagen.value = producto.imagen
            campo_descripcion.value = producto.descripcion
            selector_categoria.value = producto.categoria

        error_texto = ft.Text("", size=12, color=config.ERROR)

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar articulo" if editando else "Nuevo articulo",
                color=config.TEXTO_PRIMARIO,
            ),
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
                    on_click=lambda e: self._guardar_clic(dialogo, campo_titulo, campo_precio, selector_categoria, campo_imagen, campo_descripcion, error_texto, producto),
                    icono=ft.Icons.CHECK,
                    expand=False,
                ),
            ],
        )
        self._page.show_dialog(dialogo)

    def _guardar_clic(self, dialogo, campo_titulo, campo_precio, selector, campo_imagen, campo_descripcion, error_texto, producto) -> None:
        """Arranca la tarea de guardado del formulario."""
        self._page.run_task(
            self._guardar_articulo,
            dialogo,
            campo_titulo,
            campo_precio,
            selector,
            campo_imagen,
            campo_descripcion,
            error_texto,
            producto,
        )

    async def _guardar_articulo(self, dialogo, campo_titulo, campo_precio, selector, campo_imagen, campo_descripcion, error_texto, producto) -> None:
        """Valida, crea o actualiza el articulo y refresca la lista."""
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
        if producto is not None:
            await asyncio.to_thread(self._admin.actualizar_articulo, nuevo, producto.id)
            mensaje = "Articulo modificado correctamente"
        else:
            await asyncio.to_thread(self._admin.crear_articulo, nuevo)
            mensaje = "Articulo creado correctamente"

        self._cerrar(dialogo)
        self._mostrar_snack(mensaje)
        await self._cargar()

    # ------------------------------------------------------------------
    # Confirmacion de eliminacion
    # ------------------------------------------------------------------
    def _pedir_eliminacion(self, producto: Producto) -> None:
        """Muestra un dialogo pidiendo confirmacion para eliminar."""
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar articulo", color=config.TEXTO_PRIMARIO),
            bgcolor=config.GRAFITO,
            content=ft.Column(
                controls=[
                    ft.Text(f"Vas a eliminar: '{producto.titulo}'.", size=13, color=config.TEXTO_SECUNDARIO),
                    ft.Text("Esta accion no se puede deshacer.", size=11, color=config.TEXTO_ATENUADO),
                ],
                spacing=6,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._cerrar(dialogo)),
                ft.FilledButton(
                    content="Eliminar",
                    bgcolor=config.ERROR,
                    color="#FFFFFF",
                    on_click=lambda e: self._page.run_task(self._confirmar_eliminacion, producto, dialogo),
                ),
            ],
        )
        self._page.show_dialog(dialogo)

    async def _confirmar_eliminacion(self, producto: Producto, dialogo) -> None:
        """Ejecuta la eliminacion y refresca el panel."""
        await asyncio.to_thread(self._admin.eliminar_articulo, producto.id)
        self._cerrar(dialogo)
        self._mostrar_snack("Articulo eliminado")
        await self._cargar()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _cerrar(self, dialogo: ft.AlertDialog) -> None:
        """Cierra un dialogo y refresca la pagina."""
        dialogo.open = False
        self._page.update()

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