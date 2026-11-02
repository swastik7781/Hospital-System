import bcrypt

# Ensure compatibility between Passlib and modern bcrypt versions
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type(
        "About", (), {"__version__": getattr(bcrypt, "__version__", "4.0.1")}
    )()

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
