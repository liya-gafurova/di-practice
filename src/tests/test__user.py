import pytest
import pytest_asyncio
from dependency_injector.wiring import inject, Provide
from sqlalchemy import NullPool

from core.dependencies import Container, dumps, create_engine_once
from core.settings import settings
from domain.user.entities import User
from domain.user.commands import create_user, CreateUserDTO, update_user, UpdateUserDTO
from domain.user.queries import get_user_by_id, GetUserDTO, get_all_users, GetUsersDTO
from shared.database import Base


@pytest_asyncio.fixture
async def clean_db():
    engine = create_engine_once(settings.SQLALCHEMY_DATABASE_URI)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def container(clean_db):
    container = Container()
    container.config.from_dict(settings.__dict__)
    container.wire(modules=[__name__])

    return container


@pytest_asyncio.fixture
@inject
async def user(clean_db, container, session_maker = Provide[Container.db_session], repo=Provide[Container.user_repo]):
    user = User(id=User.next_id(), name='user name', email='example@test.com')
    repo.session = session_maker()
    await repo.add(user)

    return user


@pytest_asyncio.fixture
@inject
async def users(clean_db, container,db_session = Provide[Container.db_session], repo=Provide[Container.user_repo]):
    repo.session = db_session()

    users = [
        User(id=User.next_id(), name='user name', email='example@test.com'),
        User(id=User.next_id(), name='user2 name', email='example2@test.com'),
        User(id=User.next_id(), name='user3 name', email='example3@test.com'),
        User(id=User.next_id(), name='user4 name', email='example4@test.com')
    ]
    for user in users:
        await repo.add(user)

    return users


@pytest.mark.asyncio
async def test__create_user(container, clean_db):
    name = 'Name'
    email = 'example@test.com'

    test_user = await create_user(CreateUserDTO(name=name, email=email))

    assert test_user.name == name
    assert test_user.email == email
    assert test_user.id is not None


@pytest.mark.asyncio
@inject
async def test__get_user_by_id(clean_db, container, user):
    user_by_id = await get_user_by_id(GetUserDTO(id=user.id))

    assert user_by_id.name == user.name
    assert user_by_id.id == user.id


@pytest.mark.asyncio
@inject
async def test__get_users(clean_db, container, users):
    all_users = await get_all_users(GetUsersDTO())

    assert len(all_users) == len(users)
    assert all_users[0].id == users[0].id
    assert all_users[-1].id == users[-1].id


@pytest.mark.asyncio
@inject
async def test__update_user_by_id(clean_db, container, user):
    new_name = 'New Name'
    new_email = 'test@mail.com'

    await update_user(UpdateUserDTO(id=user.id, name=new_name, email=new_email))

    updated_user = await get_user_by_id(GetUserDTO(id=user.id))

    assert updated_user.name == new_name
    assert updated_user.id == user.id
