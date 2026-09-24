"""Servicio de acceso a la API de FakeStore (singleton).

Encapsula todas las llamadas HTTP:
- autenticacion  -> POST /auth/login (devuelve un token JWT) y GET /users
- catalogo       -> GET  /products y sus categorias
- administracion -> POST /products, PUT /products/{id}, DELETE /products/{id}

La API de FakeStore es de solo lectura (no persiste cambios), por lo que
los cambios del administrador (crear/editar/eliminar) se mantienen en un
registro local de la sesion. Asi el catalogo refleja las modificaciones
mientras la aplicacion esta abierta.
"""

from __future__ import annotations

import httpx

import src.config as config
from src.models.product import Producto
from src.models.user import UserDTO

TIMEOUT = 15  # segundos para cada peticion HTTP


class ApiService:
    """Singleton que centraliza el acceso a la API."""

    _instancia: "ApiService | None" = None

    def __new__(cls) -> "ApiService":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._creados: dict[int, Producto] = {}   # articulos nuevos
            cls._instancia._editados: dict[int, Producto] = {}  # articulos modificados
            cls._instancia._eliminados: set[int] = set()        # articulos borrados
            cls._instancia._ultimo_id = 20                      # contador local de ids
        return cls._instancia

    # ------------------------------------------------------------------
    # Metodos auxiliares de HTTP
    # ------------------------------------------------------------------
    def _get(self, url: str):
        """Ejecuta GET y devuelve el JSON (lanza error si falla)."""
        respuesta = httpx.get(url, timeout=TIMEOUT)
        respuesta.raise_for_status()
        return respuesta.json()

    def _post(self, url: str, datos: dict):
        """Ejecuta POST y devuelve el JSON (lanza error si falla)."""
        respuesta = httpx.post(url, json=datos, timeout=TIMEOUT)
        respuesta.raise_for_status()
        return respuesta.json()

    def _put(self, url: str, datos: dict):
        """Ejecuta PUT y devuelve el JSON (lanza error si falla)."""
        respuesta = httpx.put(url, json=datos, timeout=TIMEOUT)
        respuesta.raise_for_status()
        return respuesta.json()

    def _delete(self, url: str):
        """Ejecuta DELETE y devuelve el JSON (o vacio) si tiene exito."""
        respuesta = httpx.delete(url, timeout=TIMEOUT)
        respuesta.raise_for_status()
        return respuesta.json() if respuesta.content else {}

    # ------------------------------------------------------------------
    # Autenticacion y usuarios
    # ------------------------------------------------------------------
    def login(self, usuario: str, contrasena: str) -> str:
        """Valida credenciales contra /auth/login y devuelve el token."""
        datos = self._post(
            f"{config.API_BASE}/auth/login",
            {"username": usuario, "password": contrasena},
        )
        return datos["token"]

    def obtener_usuario(self, usuario: str) -> UserDTO:
        """Busca en /users el perfil completo del usuario autenticado."""
        for u in self._get(f"{config.API_BASE}/users"):
            if u.get("username") == usuario:
                return UserDTO.from_dict(u)
        raise ValueError("Usuario autenticado no encontrado en la API")

    def autenticar(self, usuario: str, contrasena: str) -> UserDTO:
        """Login real contra la API + carga del perfil del usuario."""
        try:
            self.login(usuario, contrasena)
        except httpx.HTTPStatusError as error:
            # HTTP 400/401 = credenciales invalidas (no un fallo de red)
            if error.response is not None and error.response.status_code in (400, 401):
                raise ValueError("Credenciales incorrectas") from error
            raise
        return self.obtener_usuario(usuario)

    # ------------------------------------------------------------------
    # Catalogo de productos
    # ------------------------------------------------------------------
    def obtener_categorias(self) -> list[str]:
        """Devuelve la lista de categorias disponibles."""
        return self._get(f"{config.API_BASE}/products/categories")

    def obtener_productos(self, categoria: str | None = None) -> list[Producto]:
        """Devuelve el catalogo combinando la API con los cambios locales.

        Aplica sobre la lista base: eliminaciones, ediciones y creaciones
        hechas por el administrador durante la sesion.
        """
        base = [Producto.from_json(p) for p in self._get(f"{config.API_BASE}/products")]
        ids_base = {p.id for p in base}

        mezcla: list[Producto] = []
        for producto in base:
            if producto.id in self._eliminados:
                continue                       # omitido por el administrador
            if producto.id in self._editados:
                mezcla.append(self._editados[producto.id])
            else:
                mezcla.append(producto)

        # Articulos creados localmente (su id no existe en la API).
        for producto_id in sorted(self._creados):
            if producto_id not in ids_base:
                mezcla.append(self._creados[producto_id])

        if categoria:
            mezcla = [p for p in mezcla if p.categoria == categoria]
        return mezcla

    # ------------------------------------------------------------------
    # Administracion de articulos (CRUD)
    # ------------------------------------------------------------------
    @staticmethod
    def _producto_a_json(producto: Producto) -> dict:
        """Convierte un Producto al JSON esperado por la API."""
        return {
            "title": producto.titulo,
            "price": producto.precio,
            "description": producto.descripcion,
            "image": producto.imagen,
            "category": producto.categoria,
        }

    def crear_producto(self, producto: Producto) -> Producto:
        """Crea un articulo (remoto + registro local) y devuelve el guardado."""
        try:
            self._post(f"{config.API_BASE}/products", self._producto_a_json(producto))
        except Exception:
            # La API de demo no persiste; igualmente se guarda en la sesion.
            pass
        self._ultimo_id += 1
        producto.id = self._ultimo_id
        self._creados[producto.id] = producto
        return producto

    def actualizar_producto(self, producto: Producto) -> Producto:
        """Modifica un articulo (remoto + registro local)."""
        try:
            self._put(
                f"{config.API_BASE}/products/{producto.id}",
                self._producto_a_json(producto),
            )
        except Exception:
            pass
        if producto.id in self._creados:
            self._creados[producto.id] = producto
        else:
            self._editados[producto.id] = producto
        return producto

    def eliminar_producto(self, producto_id: int) -> None:
        """Elimina un articulo (remoto + registro local)."""
        try:
            self._delete(f"{config.API_BASE}/products/{producto_id}")
        except Exception:
            pass
        self._eliminados.add(producto_id)
        self._creados.pop(producto_id, None)
        self._editados.pop(producto_id, None)