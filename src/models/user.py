from __future__ import annotations

from dataclasses import dataclass, field


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
    name: UserName = field(default_factory=UserName)
    address: Address = field(default_factory=Address)
    phone: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> UserDTO:
        name_data = data.get("name", {})
        addr_data = data.get("address", {})
        geo_data = addr_data.get("geolocation", {})

        return cls(
            id=data.get("id", 0),
            email=data.get("email", ""),
            username=data.get("username", ""),
            password=data.get("password", ""),
            name=UserName(
                firstname=name_data.get("firstname", ""),
                lastname=name_data.get("lastname", ""),
            ),
            address=Address(
                city=addr_data.get("city", ""),
                street=addr_data.get("street", ""),
                number=addr_data.get("number", 0),
                zipcode=addr_data.get("zipcode", ""),
                geolocation=GeoLocation(
                    lat=geo_data.get("lat", ""),
                    long=geo_data.get("long", ""),
                ),
            ),
            phone=data.get("phone", ""),
        )
