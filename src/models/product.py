from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Rating:
    rate: float = 0.0
    count: int = 0


@dataclass
class Product:
    id: int = 0
    title: str = ""
    price: float = 0.0
    description: str = ""
    category: str = ""
    image: str = ""
    rating: Rating = field(default_factory=Rating)

    @classmethod
    def from_dict(cls, data: dict) -> Product:
        rating_data = data.get("rating", {})
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            price=float(data.get("price", 0.0)),
            description=data.get("description", ""),
            category=data.get("category", ""),
            image=data.get("image", ""),
            rating=Rating(
                rate=float(rating_data.get("rate", 0.0)),
                count=int(rating_data.get("count", 0)),
            ),
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "category": self.category,
            "image": self.image,
        }