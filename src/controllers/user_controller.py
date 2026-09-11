from __future__ import annotations

from src.models import Role
from src.models.user import UserDTO


class UserController:
    _instance: UserController | None = None

    def __new__(cls) -> UserController:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_role_label(self, role: Role) -> str:
        labels = {
            Role.ADMIN: "Administrador",
            Role.AUDITOR: "Auditor",
            Role.CLIENT: "Cliente",
        }
        return labels.get(role, "Desconocido")

    def get_role_color(self, role: Role) -> str:
        colors = {
            Role.ADMIN: "red",
            Role.AUDITOR: "amber",
            Role.CLIENT: "green",
        }
        return colors.get(role, "grey")

    def get_full_name(self, user: UserDTO) -> str:
        return f"{user.name.firstname} {user.name.lastname}"

    def get_full_address(self, user: UserDTO) -> str:
        return f"{user.address.street} {user.address.number}, {user.address.city} ({user.address.zipcode})"
