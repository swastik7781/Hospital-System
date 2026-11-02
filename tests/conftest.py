import asyncio
import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.auth.password import get_password_hash
from app.auth.jwt import create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_hospital.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    if os.path.exists("./test_hospital.db"):
        try:
            os.remove("./test_hospital.db")
        except Exception:
            pass


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    from sqlalchemy import select
    res = await db_session.execute(select(User).where(User.email == "test_admin@hospital.com"))
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            email="test_admin@hospital.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def doctor_user(db_session: AsyncSession) -> User:
    from sqlalchemy import select
    res = await db_session.execute(select(User).where(User.email == "test_doctor@hospital.com"))
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            email="test_doctor@hospital.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test Doctor MD",
            role=UserRole.DOCTOR,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def receptionist_user(db_session: AsyncSession) -> User:
    from sqlalchemy import select
    res = await db_session.execute(select(User).where(User.email == "test_reception@hospital.com"))
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            email="test_reception@hospital.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test Receptionist",
            role=UserRole.RECEPTIONIST,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def patient_user(db_session: AsyncSession) -> User:
    from sqlalchemy import select
    res = await db_session.execute(select(User).where(User.email == "test_patient@hospital.com"))
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            email="test_patient@hospital.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test Patient",
            role=UserRole.PATIENT,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def admin_headers(admin_user: User) -> dict:
    token = create_access_token(data={"sub": str(admin_user.id), "role": admin_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def doctor_headers(doctor_user: User) -> dict:
    token = create_access_token(data={"sub": str(doctor_user.id), "role": doctor_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def receptionist_headers(receptionist_user: User) -> dict:
    token = create_access_token(data={"sub": str(receptionist_user.id), "role": receptionist_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def patient_headers(patient_user: User) -> dict:
    token = create_access_token(data={"sub": str(patient_user.id), "role": patient_user.role.value})
    return {"Authorization": f"Bearer {token}"}
