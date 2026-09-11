from __future__ import annotations

import httpx

from src.models.user import UserDTO


BASE_URL = "https://fakestoreapi.com"


class ApiService:
    _instance: ApiService | None = None

    def __new__(cls) -> ApiService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_users(self) -> list[UserDTO]:
        response = httpx.get(f"{BASE_URL}/users", timeout=15)
        response.raise_for_status()
        return [UserDTO.from_dict(u) for u in response.json()]

    def login(self, username: str, password: str) -> UserDTO:
        users = self.get_users()
        for user in users:
            if user.username == username and user.password == password:
                return user
        raise ValueError("Credenciales incorrectas")
