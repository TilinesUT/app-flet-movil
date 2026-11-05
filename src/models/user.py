from __future__ import annotations

from dataclasses import dataclass, field

from src.models.parsing import como_dict, entero, texto


@dataclass
class GeoLocation:
    lat: str = ""
    long: str = ""


@dataclass
class Address:
    city: str = ""
    street: str = ""
    number: int = 0
    zipcode: str = ""
    geolocation: GeoLocation = field(default_factory=GeoLocation)


@dataclass
class UserName:
    firstname: str = ""
    lastname: str = ""


@dataclass
class UserDTO:
    id: int = 0
    email: str = ""
    username: str = ""
    password: str = ""
    role: str = "CLIENT"
    name: UserName = field(default_factory=UserName)
    address: Address = field(default_factory=Address)
    phone: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> UserDTO:
        datos = como_dict(data)

        name_data = como_dict(datos.get("name"))
        if name_data:
            firstname = texto(name_data.get("firstname"))
            lastname = texto(name_data.get("lastname"))
        else:
            partes = texto(datos.get("name")).split(None, 1)
            firstname = partes[0] if partes else ""
            lastname = partes[1] if len(partes) > 1 else ""

        addr_data = como_dict(datos.get("address"))
        geo_data = como_dict(addr_data.get("geolocation"))

        return cls(
            id=entero(datos.get("id")),
            email=texto(datos.get("email")),
            username=texto(datos.get("user") or datos.get("username")),
            password=texto(datos.get("password")),
            role=texto(datos.get("role") or "CLIENT").upper(),
            name=UserName(
                firstname=firstname,
                lastname=lastname,
            ),
            address=Address(
                city=texto(addr_data.get("city")),
                street=texto(addr_data.get("street")),
                number=entero(addr_data.get("number")),
                zipcode=texto(addr_data.get("zipcode")),
                geolocation=GeoLocation(
                    lat=texto(geo_data.get("lat")),
                    long=texto(geo_data.get("long")),
                ),
            ),
            phone=texto(datos.get("phone")),
        )

    def nombre_completo(self) -> str:
        """Nombre y apellido del usuario."""
        return f"{self.name.firstname} {self.name.lastname}".strip()
