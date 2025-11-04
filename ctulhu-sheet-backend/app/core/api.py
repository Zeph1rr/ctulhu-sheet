from typing import Annotated

from fastapi import Depends
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from loguru import logger

from .security import decode_token
from ..db.session import async_session
from ..service import AuthService
from ..models.user import UserRead
from .errors import ForbidenError
from .errors import NotAutorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    request: Request, token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = NotAutorizedError(
        detail="Unable to validate token",
    )
    if not token:
        return None
    try:
        decoded_token = decode_token(token)
    except JWTError as e:
        logger.error(f"({request.state.req_id}) {e}")
        raise NotAutorizedError(detail=str(e))
    session = async_session()
    auth_service = AuthService(session)
    user = await auth_service.get(decoded_token["sub"])

    await session.close()
    if user is None:
        logger.warning(f"({request.state.req_id}) user is none")
        raise credentials_exception
    if user.access_token != token:
        logger.warning(f"({request.state.req_id}) access token not equals saved in database")
        raise credentials_exception
    return UserRead.model_validate(user.model_dump())


async def get_current_admin(
    current_user: UserRead = Depends(get_current_user),
):
    if not current_user.admin:
        raise ForbidenError(detail="У вас не достаточно прав")
    return current_user
