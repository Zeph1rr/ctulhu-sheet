from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import Callable

from fastapi import HTTPException
from fastapi import status
from fastapi import Request
from fastapi import Response
from pydantic import BaseModel
from pydantic import HttpUrl
from pydantic_core.core_schema import ErrorType


class ValidationErrorDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: ErrorType
    input: Optional[dict[str, Union[str, int, bool]]]
    url: HttpUrl


class ValidationErrorModel(BaseModel):
    detail: List[ValidationErrorDetail]


class ErrorResponseModel(BaseModel):
    detail: str


class BadRequestError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class NotFoundError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class NotAutorizedError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class ForbidenError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class InternalServerError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)