"""Servicio de acceso a la API local de Tienda Naranja (singleton).

Encapsula todas las llamadas HTTP contra el backend Express:
- autenticacion  -> POST /users/login
- catalogo       -> GET  /products, GET /products/categories, GET /products/:id
- administracion -> POST /products, PUT /products, DELETE /products/:id
- directorio     -> GET  /users

El backend no expone rutas de carritos, por lo que las compras se registran
en un archivo local para que el historial siga disponible al reiniciar.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import httpx

import src.config as config
from src.models.cart_history import CartDTO, CartItemDTO
from src.models.product import Producto
from src.models.user import UserDTO

CARRITOS_LOCALES = Path.home() / ".proyecto_movil_carts.json"


class ApiError(Exception):
    """Error informado por la API, con su mensaje y codigo HTTP."""

    def __init__(self, mensaje: str, status: int = 0, errores: dict | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status
        self.errores = errores or {}


class ApiService:
    """Singleton que centraliza el acceso a la API."""

    _instancia: "ApiService | None" = None

    def __new__(cls) -> "ApiService":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._carritos_creados = cls._instancia._leer_carritos_locales()
        return cls._instancia

    # ------------------------------------------------------------------
    # Metodo auxiliar de HTTP
    # ------------------------------------------------------------------
    def _peticion(self, metodo: str, ruta: str, datos: dict | None = None):
        """Ejecuta la peticion y devuelve el campo `res` de la respuesta."""
        url = f"{config.API_BASE}{ruta}"

        try:
            respuesta = httpx.request(
                metodo,
                url,
                json=datos,
                timeout=config.API_TIMEOUT,
            )
        except httpx.HTTPError as error:
            raise ApiError(
                f"No se pudo conectar con la API ({config.API_BASE})"
            ) from error

        try:
            cuerpo = respuesta.json()
        except ValueError:
            cuerpo = {}

        if not isinstance(cuerpo, dict):
            if respuesta.status_code >= 400:
                raise ApiError("La API devolvio un error", respuesta.status_code)
            return cuerpo

        if respuesta.status_code >= 400 or cuerpo.get("ok") is False:
            raise ApiError(
                self._mensaje_error(cuerpo),
                respuesta.status_code,
                cuerpo.get("err"),
            )

        if "res" in cuerpo:
            return cuerpo["res"]
        return cuerpo

    @staticmethod
    def _mensaje_error(cuerpo: dict) -> str:
        """Arma un mensaje legible a partir del sobre de error de la API."""
        mensaje = texto_error = str(cuerpo.get("msg") or "").strip()
        errores = cuerpo.get("err")

        if isinstance(errores, dict) and errores:
            detalle = "; ".join(
                f"{campo}: {detalle}" for campo, detalle in errores.items()
            )
            mensaje = f"{mensaje}: {detalle}" if texto_error and texto_error != "Error" else detalle

        return mensaje or "La API devolvio un error"

    # ------------------------------------------------------------------
    # Autenticacion y usuarios
    # ------------------------------------------------------------------
    def login(self, usuario: str, contrasena: str) -> UserDTO:
        """Valida las credenciales en /users/login y devuelve el perfil."""
        datos = self._peticion(
            "POST",
            "/users/login",
            {"user": usuario, "password": contrasena},
        )
        return UserDTO.from_dict(datos)

    def autenticar(self, usuario: str, contrasena: str) -> UserDTO:
        """Login contra la API, traduciendo el error de credenciales."""
        try:
            return self.login(usuario, contrasena)
        except ApiError as error:
            if error.status in (400, 401):
                raise ValueError("Credenciales incorrectas") from error
            raise

    def obtener_usuarios(self) -> list[UserDTO]:
        """Descarga el directorio completo de cuentas registradas."""
        respuesta = self._peticion("GET", "/users")
        if not isinstance(respuesta, list):
            return []
        return [
            UserDTO.from_dict(item)
            for item in respuesta
            if isinstance(item, dict)
        ]

    # ------------------------------------------------------------------
    # Catalogo de productos
    # ------------------------------------------------------------------
    def obtener_categorias(self) -> list[str]:
        """Devuelve la lista de categorias disponibles."""
        respuesta = self._peticion("GET", "/products/categories")
        if not isinstance(respuesta, list):
            return []
        return [categoria for categoria in respuesta if isinstance(categoria, str)]

    def obtener_productos(self, categoria: str | None = None) -> list[Producto]:
        """Descarga el catalogo y filtra por categoria si se indica."""
        respuesta = self._peticion("GET", "/products")
        if not isinstance(respuesta, list):
            return []

        productos = [
            Producto.from_json(item)
            for item in respuesta
            if isinstance(item, dict)
        ]

        if categoria:
            productos = [p for p in productos if p.categoria == categoria]
        return productos

    def obtener_producto(self, producto_id: int) -> Producto:
        """Descarga un articulo concreto por su id."""
        datos = self._peticion("GET", f"/products/{producto_id}")
        return Producto.from_json(datos)

    # ------------------------------------------------------------------
    # Administracion de articulos (CRUD)
    # ------------------------------------------------------------------
    @staticmethod
    def _producto_a_json(producto: Producto, incluir_id: bool = False) -> dict:
        """Convierte un Producto al JSON esperado por la API."""
        datos = {
            "title": producto.titulo,
            "price": producto.precio,
            "description": producto.descripcion,
            "image": producto.imagen,
            "category": producto.categoria,
            "rating_rate": producto.calificacion.tasa,
            "rating_count": producto.calificacion.conteo,
        }
        if incluir_id:
            datos["id"] = producto.id
        return datos

    def crear_producto(self, producto: Producto) -> Producto:
        """Crea un articulo en la API y devuelve el guardado."""
        datos = self._peticion(
            "POST",
            "/products",
            self._producto_a_json(producto),
        )
        return Producto.from_json(datos)

    def actualizar_producto(self, producto: Producto) -> Producto:
        """Actualiza un articulo existente (el id viaja en el cuerpo)."""
        datos = self._peticion(
            "PUT",
            "/products",
            self._producto_a_json(producto, incluir_id=True),
        )
        return Producto.from_json(datos)

    def eliminar_producto(self, producto_id: int) -> None:
        """Elimina un articulo del catalogo por su id."""
        self._peticion("DELETE", f"/products/{producto_id}")

    # ------------------------------------------------------------------
    # Historial de carritos (local, la API no expone /carts)
    # ------------------------------------------------------------------
    def _leer_carritos_locales(self) -> list[CartDTO]:
        """Recupera del disco las compras registradas por esta app."""
        if not CARRITOS_LOCALES.exists():
            return []
        try:
            datos = json.loads(CARRITOS_LOCALES.read_text(encoding="utf-8"))
            if not isinstance(datos, list):
                return []
            return [
                CartDTO.from_dict(item)
                for item in datos
                if isinstance(item, dict)
            ]
        except (OSError, ValueError):
            return []

    def _guardar_carritos_locales(self) -> None:
        """Persiste las compras locales para conservar el historial."""
        datos = [
            {
                "id": carrito.id,
                "userId": carrito.user_id,
                "date": carrito.date,
                "products": [
                    {
                        "productId": item.product_id,
                        "quantity": item.quantity,
                    }
                    for item in carrito.products
                ],
            }
            for carrito in self._carritos_creados
        ]
        try:
            CARRITOS_LOCALES.write_text(
                json.dumps(datos, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass

    def obtener_carritos(self) -> list[CartDTO]:
        """Devuelve el historial de compras registrado en este equipo."""
        return list(self._carritos_creados)

    def registrar_compra(self, user_id: int, items: list) -> CartDTO:
        """Registra una compra y la guarda para el historial global."""
        lineas = [
            CartItemDTO(
                product_id=int(item.producto_id),
                quantity=int(item.cantidad),
            )
            for item in items
            if int(item.cantidad) > 0
        ]
        if not lineas:
            raise ValueError("El carrito esta vacio")

        siguiente_id = max(
            (carrito.id for carrito in self._carritos_creados),
            default=0,
        ) + 1

        carrito = CartDTO(
            id=siguiente_id,
            user_id=int(user_id),
            date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            products=lineas,
        )

        self._carritos_creados.append(carrito)
        self._guardar_carritos_locales()
        return carrito
