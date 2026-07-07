from app.core.security import hash_password, verify_password
from app.modules.users.models import User
from app.modules.users.schemas import RegisterRequest


class UserService:
    """Pure user domain helpers. Password hashing is delegated to core.security."""

    @staticmethod
    def build_user(data: RegisterRequest) -> User:
        return User(
            full_name=data.full_name.strip(),
            email=data.email,
            password_hash=hash_password(data.password),
        )

    @staticmethod
    def password_matches(user: User, password: str) -> bool:
        return verify_password(password, user.password_hash)
