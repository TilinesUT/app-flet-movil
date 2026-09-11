from __future__ import annotations

from src.models import Role
from src.models.user import UserDTO
from src.services.api_service import ApiService
from src.models.session import Session


class AuthController:
    _instance: AuthController | None = None
    _api: ApiService
    _session: Session

    def __new__(cls) -> AuthController:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api = ApiService()
            cls._instance._session = Session()
        return cls._instance

    @property
    def current_user(self) -> UserDTO | None:
        return self._session.user

    @property
    def current_role(self) -> Role | None:
        return self._session.role

    @property
    def is_authenticated(self) -> bool:
        return self._session.is_authenticated

    def login(self, username: str, password: str) -> UserDTO:
        user = self._api.login(username, password)
        self._session.save(user)
        return user

    def logout(self) -> None:
        self._session.destroy()

    def restore_session(self) -> UserDTO | None:
        return self._session.load()
