from __future__ import annotations

from urllib.parse import quote

import httpx

from src.models.product import Product
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

    def get_products(self) -> list[Product]:
        response = httpx.get(f"{BASE_URL}/products", timeout=15)
        response.raise_for_status()
        return [Product.from_dict(p) for p in response.json()]

    def get_categories(self) -> list[str]:
        response = httpx.get(f"{BASE_URL}/products/categories", timeout=15)
        response.raise_for_status()
        return response.json()

    def get_products_by_category(self, category: str) -> list[Product]:
        url = f"{BASE_URL}/products/category/{quote(category)}"
        response = httpx.get(url, timeout=15)
        response.raise_for_status()
        return [Product.from_dict(p) for p in response.json()]

    def get_product(self, product_id: int) -> Product:
        response = httpx.get(f"{BASE_URL}/products/{product_id}", timeout=15)
        response.raise_for_status()
        return Product.from_dict(response.json())

    def delete_product(self, product_id: int) -> None:
        response = httpx.delete(f"{BASE_URL}/products/{product_id}", timeout=15)
        response.raise_for_status()

    def update_product(self, product: Product) -> Product:
        payload = product.to_dict()
        response = httpx.put(f"{BASE_URL}/products/{product.id}", json=payload, timeout=15)
        response.raise_for_status()
        return Product.from_dict(response.json())
