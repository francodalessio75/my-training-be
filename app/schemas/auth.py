from app.schemas.common import CamelModel


class LoginRequest(CamelModel):
    email: str
    password: str


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(CamelModel):
    id: str
    email: str
    display_name: str
    description: str | None = None
