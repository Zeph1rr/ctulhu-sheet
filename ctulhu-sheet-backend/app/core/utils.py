import json
import pathlib
from datetime import datetime
from datetime import timedelta
from uuid import UUID

import tomli
from jose import jwt


class UUIDEncoder(json.JSONEncoder):
    """Encoder for uuid to json responses"""

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def get_project_meta(
    project_path: pathlib.Path = pathlib.Path(__name__).parent.parent.parent,
) -> dict[str, str]:
    """Geting data from pyproject.toml"""
    pyproject_path = pathlib.Path(project_path, "pyproject.toml")
    with open(pyproject_path, mode="rb") as pyproject:
        return tomli.load(pyproject)["tool"]["poetry"]


def get_project_data() -> tuple[str, str]:
    """Getting app_name and app_version from pyproject.toml"""
    project_meta = get_project_meta()
    return project_meta["name"], project_meta["version"]


def create_jwt_token(
    data: dict,
    secret: str = "ChangeMe",
    algorithm: str = "HS256",
    expire: datetime = datetime.utcnow() + timedelta(days=15),
) -> str:
    """
    Arguments

    data -- data for encoding

    secret -- jwt secret word for encoding (default 'ChangeMe')

    algorithm -- encoding algorithm (default 'HS256')

    expire -- time when token expires (default datetime.utcnow() + timedelta(days=15))
    """
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt
