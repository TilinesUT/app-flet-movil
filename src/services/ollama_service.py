"""Cliente del asistente de IA local servido por Ollama.

Se conecta al endpoint /api/chat de Ollama y transmite la respuesta por
fragmentos (streaming) para que la interfaz la pinte mientras se genera.

El modelo y la URL se configuran con las variables de entorno
``OLLAMA_MODELO`` y ``OLLAMA_URL`` (ver ``src/config.py``).
"""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx

import src.config as config


class OllamaError(Exception):
    """Error de Ollama con un mensaje listo para mostrar al usuario."""


class OllamaService:
    """Singleton que conversa con el modelo definido en la configuracion."""

    _instancia: "OllamaService | None" = None

    def __new__(cls) -> "OllamaService":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    async def transmitir(
        self,
        historial: list[dict[str, str]],
        al_recibir: Callable[[str], None] | None = None,
    ) -> str:
        """Envia la conversacion y devuelve la respuesta completa del modelo.

        ``historial`` es una lista de mensajes con el formato de Ollama
        (``{"role": "user" | "assistant", "content": "..."}``). Si se pasa
        ``al_recibir``, se invoca con cada fragmento recibido para poder
        mostrar la respuesta en vivo.
        """
        mensajes: list[dict[str, str]] = []
        if config.OLLAMA_PROMPT_SISTEMA.strip():
            mensajes.append(
                {
                    "role": "system",
                    "content": config.OLLAMA_PROMPT_SISTEMA.strip(),
                }
            )
        mensajes.extend(historial)

        peticion = {
            "model": config.OLLAMA_MODELO,
            "messages": mensajes,
            "stream": True,
        }
        fragmentos: list[str] = []

        try:
            timeout = httpx.Timeout(
                config.OLLAMA_TIMEOUT,
                connect=10.0,
            )
            async with httpx.AsyncClient(timeout=timeout) as cliente:
                async with cliente.stream(
                    "POST",
                    f"{config.OLLAMA_URL}/api/chat",
                    json=peticion,
                ) as respuesta:
                    if respuesta.status_code >= 400:
                        detalle = (await respuesta.aread()).decode(
                            "utf-8", "replace"
                        )
                        raise OllamaError(
                            self._mensaje_http(respuesta.status_code, detalle)
                        )

                    async for linea in respuesta.aiter_lines():
                        if not linea.strip():
                            continue
                        try:
                            datos = json.loads(linea)
                        except ValueError:
                            continue

                        if datos.get("error"):
                            raise OllamaError(str(datos["error"]))

                        fragmento = (datos.get("message") or {}).get(
                            "content"
                        ) or ""
                        if fragmento:
                            fragmentos.append(fragmento)
                            if al_recibir is not None:
                                al_recibir(fragmento)

                        if datos.get("done"):
                            break

        except OllamaError:
            raise
        except httpx.ConnectError as error:
            raise OllamaError(
                "No se pudo conectar con Ollama en "
                f"{config.OLLAMA_URL}. Inicia el servicio con "
                "'ollama serve'."
            ) from error
        except httpx.TimeoutException as error:
            raise OllamaError(
                "Ollama tardo demasiado en responder. Intenta de nuevo."
            ) from error
        except httpx.HTTPError as error:
            raise OllamaError(f"Error de conexion con Ollama: {error}") from error

        respuesta_final = "".join(fragmentos).strip()
        if not respuesta_final:
            raise OllamaError("El modelo no devolvio ninguna respuesta.")
        return respuesta_final

    @staticmethod
    def _mensaje_http(status: int, detalle: str) -> str:
        """Traduce la respuesta de error de Ollama a un mensaje util."""
        try:
            error = json.loads(detalle).get("error")
        except (ValueError, AttributeError):
            error = None

        texto = str(error or detalle or "").strip()

        if status in (401, 403):
            return (
                "Ollama Cloud rechazo la peticion. Inicia sesion con "
                "'ollama signin'."
            )

        if status == 404 or "not found" in texto.lower():
            return (
                f"El modelo '{config.OLLAMA_MODELO}' no esta disponible. "
                f"Ejecuta 'ollama pull {config.OLLAMA_MODELO}'."
            )

        return f"Ollama respondio con un error ({status}): {texto[:200]}"
