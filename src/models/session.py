from __future__ import annotations

import json
import os
from pathlib import Path

from src.models.user import UserDTO
from src.models import Role


SESSION_FILE = Path.home() / ".proyecto_movil_session.json"


class Session:
    _instance: Session | None = None
    _user: UserDTO | None = None
    _role: Role | None = None

    def __new__(cls) -> Session:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def user(self) -> UserDTO | None:
        return self._user

    @property
    def role(self) -> Role | None:
        return self._role

    @property
    def is_authenticated(self) -> bool:
        return self._user is not None

    def save(self, user: UserDTO) -> None:
        self._user = user
        self._role = Role.from_id(user.id)
        data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "name": {
                "firstname": user.name.firstname,
                "lastname": user.name.lastname,
            },
            "address": {
                "city": user.address.city,
                "street": user.address.street,
                "number": user.address.number,
                "zipcode": user.address.zipcode,
                "geolocation": {
                    "lat": user.address.geolocation.lat,
                    "long": user.address.geolocation.long,
                },
            },
            "phone": user.phone,
        }
        SESSION_FILE.write_text(json.dumps(data), encoding="utf-8")

    def load(self) -> UserDTO | None:
        if self._user is not None:
            return self._user

        if not SESSION_FILE.exists():
            return None

        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            user = UserDTO.from_dict(data)
            self._user = user
            self._role = Role.from_id(user.id)
            return user
        except Exception:
            self.destroy()
            return None

    def destroy(self) -> None:
        self._user = None
        self._role = None
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
