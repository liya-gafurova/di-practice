import pytest
import pytest_asyncio
from dependency_injector.wiring import inject, Provide

from core.dependencies import Container
from domain.user.entities import User
from domain.user.commands import create_user, CreateUserDTO, update_user, UpdateUserDTO
from domain.user.queries import get_user_by_id, GetUserDTO, get_all_users, GetUsersDTO


@pytest_asyncio.fixture
@inject
async def users(
        clean_db,
        container
):
    repo = container.user_repo()
    session_maker = container.db_session()
    repo.session = session_maker()

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
@inject
async def test__get_user_by_id(clean_db, container, user):
    user_by_id = await get_user_by_id(GetUserDTO(id=user.id))

    assert user_by_id.name == user.name
    assert user_by_id.id == user.id


@pytest.mark.asyncio
async def test__get_users(clean_db, container, users):
    all_users = await get_all_users(GetUsersDTO())

    assert len(all_users) == len(users)
    assert all_users[0].id == users[0].id
    assert all_users[-1].id == users[-1].id


@pytest.mark.asyncio
async def test__create_user(container, clean_db):
    name = 'Name'
    email = 'example@test.com'

    test_user = await create_user(CreateUserDTO(name=name, email=email))

    assert test_user.name == name
    assert test_user.email == email
    assert test_user.id is not None


@pytest.mark.asyncio
async def test__update_user_by_id(clean_db, container, user):
    new_name = 'New Name'
    new_email = 'test@mail.com'

    await update_user(UpdateUserDTO(id=user.id, name=new_name, email=new_email))

    updated_user = await get_user_by_id(GetUserDTO(id=user.id))

    assert updated_user.name == new_name
    assert updated_user.id == user.id
