"""Componentes visuales reutilizables (tema naranja/negro).

Botones, campos de texto, insignias, tarjetas y utilidades graficas
compartidas por todas las vistas de la aplicacion.
"""

from __future__ import annotations

import flet as ft

import src.config as config
from src.models.product import Producto

# Borde suave que usan muchas tarjetas de la interfaz.
BORDE_SUAVE = ft.border.Border.all(width=1, color=config.BORDE)


def boton_primario(
    texto: str,
    on_click,
    icono: str | None = None,
    expand: bool = True,
) -> ft.FilledButton:
    """Boton principal de accion (fondo naranja, texto negro)."""
    return ft.FilledButton(
        content=texto,
        icon=icono,
        on_click=on_click,
        expand=expand,
        bgcolor=config.NARANJA,
        color=config.NEGRO,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
        ),
    )


def boton_secundario(
    texto: str,
    on_click,
    icono: str | None = None,
    expand: bool = True,
) -> ft.OutlinedButton:
    """Boton secundario (borde naranja suave, texto naranja)."""
    return ft.OutlinedButton(
        content=texto,
        icon=icono,
        on_click=on_click,
        expand=expand,
        style=ft.ButtonStyle(
            color=config.NARANJA_SUAVE,
            side=ft.BorderSide(width=1, color=config.NARANJA),
            shape=ft.RoundedRectangleBorder(radius=12),
            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
        ),
    )


def campo_texto(
    etiqueta: str,
    hint: str = "",
    icono: str | None = None,
    contrasena: bool = False,
    contrasena_revelable: bool = False,
) -> ft.TextField:
    """Campo de texto con el estilo oscuro/naranja de la app."""
    return ft.TextField(
        label=etiqueta,
        hint_text=hint,
        prefix_icon=icono,
        filled=True,
        fill_color=config.GRAFITO,
        border_color=config.BORDE,
        focused_border_color=config.NARANJA,
        border_radius=12,
        content_padding=ft.Padding(left=14, top=6, right=14, bottom=6),
        color=config.TEXTO_PRIMARIO,
        text_style=ft.TextStyle(size=14),
        label_style=ft.TextStyle(color=config.TEXTO_SECUNDARIO),
        hint_style=ft.TextStyle(color=config.TEXTO_ATENUADO),
        password=contrasena,
        can_reveal_password=contrasena_revelable,
    )


def insignia_rol(texto: str, color: str) -> ft.Container:
    """Etiqueta redondeada con el nombre y color del rol."""
    return ft.Container(
        content=ft.Text(
            texto.upper(),
            size=11,
            weight=ft.FontWeight.BOLD,
            color=config.NEGRO,
        ),
        padding=ft.Padding(left=12, top=5, right=12, bottom=5),
        bgcolor=color,
        border_radius=ft.BorderRadius.all(99),
    )


def avatar_codigo(codigo: int, tamano: float = 72) -> ft.Container:
    """Avatar circular con el codigo (id) del usuario."""
    return ft.Container(
        content=ft.Text(
            str(codigo),
            size=tamano * 0.45,
            weight=ft.FontWeight.BOLD,
            color=config.NARANJA,
        ),
        width=tamano,
        height=tamano,
        alignment=ft.Alignment.CENTER,
        bgcolor=config.GRAFITO,
        border=BORDE_SUAVE,
        border_radius=ft.BorderRadius.all(tamano / 2),
    )


def fila_dato(icono: str, etiqueta: str, valor: str) -> ft.Row:
    """Fila 'icono + etiqueta + valor' para mostrar datos del usuario."""
    return ft.Row(
        controls=[
            ft.Icon(icono, size=16, color=config.NARANJA_SUAVE),
            ft.Text(
                etiqueta.upper(),
                size=11,
                weight=ft.FontWeight.BOLD,
                color=config.TEXTO_ATENUADO,
            ),
            ft.Text(
                valor,
                size=13,
                color=config.TEXTO_PRIMARIO,
                expand=True,
                text_align=ft.TextAlign.RIGHT,
            ),
        ],
        spacing=10,
    )


def calificacion_estrellas(tasa: float, tamano: float = 14) -> ft.Row:
    """Representacion con estrellas de la valoracion de un producto."""
    pinta = max(0.0, min(5.0, round(float(tasa), 1)))
    enteras = int(pinta)
    media = 1 <= (pinta - enteras) * 10 >= 5
    vacias = 5 - enteras - (1 if media else 0)

    estrellas: list[ft.Control] = []
    estrellas += [
        ft.Icon(ft.Icons.STAR, size=tamano, color=config.AMARILLO)
        for _ in range(enteras)
    ]
    if media:
        estrellas.append(ft.Icon(ft.Icons.STAR_HALF, size=tamano, color=config.AMARILLO))
    estrellas += [
        ft.Icon(ft.Icons.STAR_OUTLINE, size=tamano, color=config.TEXTO_ATENUADO)
        for _ in range(vacias)
    ]
    return ft.Row(controls=estrellas, spacing=1)


def tarjeta_producto(producto: Producto, on_click, on_editar=None) -> ft.Container:
    """Tarjeta compacta de un producto.

    Si se pasa ``on_editar`` se agrega un recuadro de edicion debajo del
    precio (solo lo muestran quienes pueden editar el catalogo). El recuadro
    es un control hermano de la zona clicable, asi su clic no abre el detalle.
    """
    imagen = ft.Container(
        content=ft.Image(
            src=producto.imagen,
            fit=ft.BoxFit.CONTAIN,
            error_content=ft.Icon(
                ft.Icons.BROKEN_IMAGE_OUTLINED,
                size=40,
                color=config.TEXTO_ATENUADO,
            ),
        ),
        height=120,
        bgcolor=config.SUPERFICIE,
        border_radius=ft.BorderRadius.all(10),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding(left=8, top=8, right=8, bottom=8),
    )
    informacion = [
        ft.Text(
            producto.titulo,
            size=12,
            color=config.TEXTO_PRIMARIO,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
        calificacion_estrellas(producto.calificacion.tasa),
        ft.Text(
            producto.precio_formateado(),
            size=14,
            weight=ft.FontWeight.BOLD,
            color=config.NARANJA,
        ),
    ]

    if on_editar is None:
        # Sin recuadro de edicion: toda la tarjeta abre el detalle.
        cuerpo = ft.Column(
            controls=[imagen, *informacion],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )
        return ft.Container(
            content=cuerpo,
            padding=ft.Padding.all(10),
            bgcolor=config.SUPERFICIE,
            border_radius=ft.BorderRadius.all(14),
            border=BORDE_SUAVE,
            on_click=on_click,
            ink=True,
        )

    # Con recuadro de edicion: la zona superior abre el detalle y el
    # recuadro inferior edita el articulo (solo editores administradores).
    zona_clicable = ft.Container(
        content=ft.Column(
            controls=[imagen, *informacion],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        on_click=on_click,
        ink=False,
    )

    recuadro_editar = ft.OutlinedButton(
        content="EDITAR",
        icon=ft.Icons.EDIT_OUTLINED,
        expand=True,
        on_click=lambda e: on_editar(),
        style=ft.ButtonStyle(
            color=config.NARANJA_SUAVE,
            side=ft.BorderSide(width=1, color=config.NARANJA),
            shape=ft.RoundedRectangleBorder(radius=10),
            text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD),
        ),
    )

    return ft.Container(
        content=ft.Column(
            controls=[zona_clicable, recuadro_editar],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        padding=ft.Padding.all(10),
        bgcolor=config.SUPERFICIE,
        border_radius=ft.BorderRadius.all(14),
        border=BORDE_SUAVE,
    )