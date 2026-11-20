"""Asistente de IA flotante conectado a Ollama.

Muestra un boton flotante en todas las vistas de la app. Al pulsarlo se
abre una hoja inferior con un chat que conversa con el modelo configurado
en ``config.OLLAMA_MODELO`` (por defecto ``gemma4:31b-cloud``).
"""

from __future__ import annotations

import time

import flet as ft

import src.config as config
from src.services.ollama_service import OllamaError, OllamaService

# Ancho maximo de las burbujas de conversacion.
_ANCHO_BURBUJA = 300

# Cada cuanto se refresca la interfaz mientras llega el streaming (segundos).
_INTERVALO_PINTADO = 0.06


class ChatIA:
    """Boton flotante + hoja inferior con la conversacion del asistente."""

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._servicio = OllamaService()
        self._historial: list[dict[str, str]] = []
        self._generando = False
        self._ultimo_pintado = 0.0

        self._lista = ft.ListView(
            controls=[self._burbuja_bienvenida()],
            spacing=10,
            padding=ft.Padding(left=16, top=8, right=16, bottom=8),
            expand=True,
            auto_scroll=True,
        )
        self._subtitulo = ft.Text(
            "Asistente IA · Ollama",
            size=11,
            color=config.TEXTO_ATENUADO,
        )
        self._campo = self._crear_campo()
        self._boton_enviar = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=config.NEGRO,
            bgcolor=config.NARANJA,
            tooltip="Enviar mensaje",
            on_click=self._on_enviar,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )
        self._sheet = self._crear_sheet()

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def crear_boton(self) -> ft.FloatingActionButton:
        """Boton flotante que abre el chat (se instala en la pagina)."""
        return ft.FloatingActionButton(
            icon=ft.Icons.AUTO_AWESOME,
            bgcolor=config.NARANJA,
            foreground_color=config.NEGRO,
            tooltip=f"Preguntar a la IA ({config.OLLAMA_MODELO})",
            on_click=self.abrir,
            # Deja libre la barra de navegacion inferior de la app.
            margin=ft.Margin.only(bottom=92),
        )

    def _crear_campo(self) -> ft.TextField:
        """Campo de escritura del chat."""
        campo = ft.TextField(
            hint_text="Escribe tu mensaje...",
            hint_style=ft.TextStyle(color=config.TEXTO_ATENUADO),
            text_size=14,
            color=config.TEXTO_PRIMARIO,
            filled=True,
            fill_color=config.GRAFITO,
            border=ft.InputBorder.NONE,
            border_radius=12,
            content_padding=ft.Padding(left=14, top=12, right=14, bottom=12),
            multiline=True,
            min_lines=1,
            max_lines=4,
            shift_enter=False,
            on_submit=self._on_enviar,
        )
        campo.expand = True
        return campo

    def _crear_sheet(self) -> ft.BottomSheet:
        """Hoja inferior que contiene la conversacion completa."""
        encabezado = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.AUTO_AWESOME,
                        size=20,
                        color=config.NEGRO,
                    ),
                    width=40,
                    height=40,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=config.NARANJA,
                    border_radius=ft.BorderRadius.all(12),
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            config.OLLAMA_MODELO,
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=config.TEXTO_PRIMARIO,
                        ),
                        self._subtitulo,
                    ],
                    spacing=1,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=config.TEXTO_SECUNDARIO,
                    tooltip="Cerrar",
                    on_click=self.cerrar,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        entrada = ft.Row(
            controls=[self._campo, self._boton_enviar],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.END,
        )

        panel = ft.Container(
            expand=True,
            padding=ft.Padding(left=16, top=4, right=16, bottom=16),
            content=ft.Column(
                controls=[
                    encabezado,
                    ft.Divider(height=1, color=config.BORDE),
                    self._lista,
                    entrada,
                ],
                spacing=12,
                expand=True,
            ),
        )
        return ft.BottomSheet(
            content=panel,
            bgcolor=config.CARBON,
            show_drag_handle=True,
            dismissible=True,
            fullscreen=True,
            use_safe_area=True,
            on_dismiss=self._al_cerrar,
        )

    # ------------------------------------------------------------------
    # Burbujas de conversacion
    # ------------------------------------------------------------------
    def _burbuja_bienvenida(self) -> ft.Row:
        """Mensaje inicial del asistente (solo informativo)."""
        return self._burbuja(
            "Hola, soy tu asistente de IA. Puedo ayudarte con la tienda o "
            "con cualquier otra duda. ¿Que necesitas?",
            es_usuario=False,
        )

    def _burbuja(
        self,
        contenido: str | ft.Control,
        es_usuario: bool,
    ) -> ft.Row:
        """Fila con una burbuja alineada a la izquierda o a la derecha."""
        if isinstance(contenido, str):
            contenido = ft.Text(
                contenido,
                size=13,
                color=(
                    config.NEGRO if es_usuario else config.TEXTO_PRIMARIO
                ),
                selectable=True,
            )

        # En pantallas angostas la burbuja se adapta al ancho disponible.
        ancho_pagina = self._page.width or config.ANCHO_VENTANA
        ancho = max(180, min(_ANCHO_BURBUJA, int(ancho_pagina * 0.78)))

        return ft.Row(
            controls=[
                ft.Container(
                    content=contenido,
                    width=ancho,
                    padding=ft.Padding(left=14, top=10, right=14, bottom=10),
                    bgcolor=(
                        config.NARANJA if es_usuario else config.GRAFITO
                    ),
                    border_radius=ft.BorderRadius.only(
                        top_left=14,
                        top_right=14,
                        bottom_left=14 if es_usuario else 4,
                        bottom_right=4 if es_usuario else 14,
                    ),
                )
            ],
            alignment=(
                ft.MainAxisAlignment.END
                if es_usuario
                else ft.MainAxisAlignment.START
            ),
        )

    # ------------------------------------------------------------------
    # Apertura y cierre
    # ------------------------------------------------------------------
    async def abrir(self, e=None) -> None:
        """Muestra la hoja del chat y enfoca el campo de escritura."""
        self._mostrar_boton(False)
        self._page.show_dialog(self._sheet)
        await self._campo.focus()

    def cerrar(self, e=None) -> None:
        """Cierra la hoja del chat."""
        self._page.pop_dialog()
        self._mostrar_boton(True)
        self._page.update()

    def _al_cerrar(self, e=None) -> None:
        """Restaura el boton flotante cuando la hoja se cierra sola."""
        self._mostrar_boton(True)
        self._page.update()

    def _mostrar_boton(self, visible: bool) -> None:
        """Oculta el boton flotante mientras el chat esta abierto."""
        boton = self._page.floating_action_button
        if boton is not None:
            boton.visible = visible

    # ------------------------------------------------------------------
    # Envio de mensajes
    # ------------------------------------------------------------------
    def _on_enviar(self, e=None) -> None:
        """Toma el texto escrito y lanza la peticion al modelo."""
        if self._generando:
            return

        texto = (self._campo.value or "").strip()
        if not texto:
            return

        self._campo.value = ""
        self._generando = True
        self._boton_enviar.disabled = True
        self._subtitulo.value = "Pensando..."
        self._subtitulo.color = config.NARANJA_SUAVE

        # Burbuja del usuario + indicador de espera del asistente.
        self._lista.controls.append(self._burbuja(texto, es_usuario=True))
        indicador = ft.Row(
            controls=[
                ft.ProgressRing(
                    width=14,
                    height=14,
                    stroke_width=2,
                    color=config.NARANJA,
                ),
                ft.Text(
                    "Pensando...",
                    size=12,
                    color=config.TEXTO_SECUNDARIO,
                ),
            ],
            spacing=8,
        )
        self._lista.controls.append(indicador)
        self._page.update()

        self._page.run_task(self._responder, texto, indicador)

    async def _responder(self, pregunta: str, indicador: ft.Row) -> None:
        """Pide la respuesta a Ollama y la pinta en streaming."""
        mensajes = [*self._historial, {"role": "user", "content": pregunta}]
        respuesta = ft.Text(
            "",
            size=13,
            color=config.TEXTO_PRIMARIO,
            selectable=True,
        )
        # Sustituye el indicador de espera por la burbuja del asistente.
        indice = self._lista.controls.index(indicador)
        self._lista.controls[indice] = self._burbuja(
            respuesta,
            es_usuario=False,
        )
        self._page.update()

        fragmentos: list[str] = []

        def al_recibir(fragmento: str) -> None:
            fragmentos.append(fragmento)
            ahora = time.monotonic()
            if ahora - self._ultimo_pintado < _INTERVALO_PINTADO:
                return
            self._ultimo_pintado = ahora
            respuesta.value = "".join(fragmentos) + "▌"
            self._pintar()

        try:
            texto_final = await self._servicio.transmitir(mensajes, al_recibir)
        except OllamaError as error:
            respuesta.value = str(error)
            respuesta.color = config.ERROR
            self._subtitulo.value = "Sin conexion"
            self._subtitulo.color = config.ERROR
        except Exception as error:  # noqa: BLE001 - nunca dejar la UI colgada
            respuesta.value = f"Error inesperado: {error}"
            respuesta.color = config.ERROR
            self._subtitulo.value = "Error"
            self._subtitulo.color = config.ERROR
        else:
            respuesta.value = texto_final
            self._historial.append({"role": "user", "content": pregunta})
            self._historial.append(
                {"role": "assistant", "content": texto_final}
            )
            self._subtitulo.value = "Asistente IA · Ollama"
            self._subtitulo.color = config.TEXTO_ATENUADO
        finally:
            self._generando = False
            self._boton_enviar.disabled = False
            self._pintar()
            try:
                await self._campo.focus()
            except Exception:  # noqa: BLE001 - la hoja pudo cerrarse
                pass

    def _pintar(self) -> None:
        """Refresca la pagina sin romper si el chat ya se cerro."""
        try:
            self._page.update()
        except Exception:  # noqa: BLE001 - control fuera de la pagina
            pass
