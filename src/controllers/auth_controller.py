"""Controlador de autenticacion (singleton).

Gestiona el login contra la API, el usuario en sesion y la persistencia
de la sesion en disco para que el usuario no tenga que volver a entrar.
"""

from __future__ import annotations

from src.models import Role
from src.models.session import Session
from src.models.user import UserDTO
from src.services.api_service import ApiService


class AuthController:
    """Singleton que centraliza la autenticacion del usuario."""

    _instance: "AuthController | None" = None
    _api: ApiService
    _session: Session

    def __new__(cls) -> "AuthController":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api = ApiService()   # acceso a la FakeStore API
            cls._instance._session = Session()  # sesion persistida en disco
        return cls._instance

    @property
    def current_user(self) -> UserDTO | None:
        """Usuario autenticado actualmente (o None)."""
        return self._session.user

    @property
    def current_role(self) -> Role | None:
        """Rol del usuario actual segun su codigo (id)."""
        return self._session.role

    @property
    def is_authenticated(self) -> bool:
        """True si hay una sesion iniciada."""
        return self._session.is_authenticated

    def login(self, username: str, password: str) -> UserDTO:
        """Valida credenciales en la API, guarda sesion y devuelve el perfil."""
        usuario = self._api.autenticar(username, password)
        self._session.save(usuario)
        return usuario

    def logout(self) -> None:
        """Cierra la sesion actual."""
        self._session.destroy()

    def restore_session(self) -> UserDTO | None:
        """Recupera la sesion guardada en disco (si existe)."""
        return self._session.load()