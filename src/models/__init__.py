from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    AUDITOR = "auditor"
    CLIENT = "cliente"

    @staticmethod
    def from_id(user_id: int) -> "Role":
        if user_id in (1, 2):
            return Role.ADMIN
        if user_id == 3:
            return Role.AUDITOR
        return Role.CLIENT
