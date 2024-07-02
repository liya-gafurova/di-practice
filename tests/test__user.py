import pytest
import pytest_asyncio
from dependency_injector.wiring import inject, Provide

from dependencies import Container
from user.entities import User
from user.commands import CreateUserDTO, create_user, update_user, UpdateUserDTO
from user.queries import get_user_by_id, GetUserDTO, get_all_users, GetUsersDTO


@pytest.fixture
def container():
    container = Container()
    container.wire(modules=[__name__])
    return container


@pytest_asyncio.fixture
@inject
async def user(container, storage=Provide[Container.storage]):
    user = User(id=User.next_id(), name='user name', email='example@test.com')
    await storage.add(user)

    return user


@pytest_asyncio.fixture
@inject
async def users(container, storage=Provide[Container.storage]):
    users = [
        User(id=User.next_id(), name='user name', email='example@test.com'),
        User(id=User.next_id(), name='user2 name', email='example2@test.com'),
        User(id=User.next_id(), name='user3 name', email='example3@test.com'),
        User(id=User.next_id(), name='user4 name', email='example4@test.com')
    ]
    for user in users:
        await storage.add(user)

    return users


@pytest.mark.asyncio
async def test__create_user(container):
    name = 'Name'
    email = 'example@test.com'

    test_user = await create_user(CreateUserDTO(name=name, email=email))

    assert test_user.name == name
    assert test_user.email == email
    assert test_user.id is not None


@pytest.mark.asyncio
@inject
async def test__get_user_by_id(container, user):
    user_by_id = await get_user_by_id(GetUserDTO(id=user.id))

    assert user_by_id.name == user.name
    assert user_by_id.email == user.email


@pytest.mark.asyncio
@inject
async def test__get_users(container, users):
    all_users = await get_all_users(GetUsersDTO())

    assert len(all_users) == len(users)
    assert all_users[0].id == users[0].id
    assert all_users[-1].id == users[-1].id


@pytest.mark.asyncio
@inject
async def test__update_user_by_id(container, user):

    new_name = 'New Name'
    new_email = 'test@mail.com'

    await update_user(UpdateUserDTO(id=user.id, name=new_name, email=new_email))

    updated_user = await get_user_by_id(GetUserDTO(id=user.id))

    assert updated_user.name == new_name
    assert updated_user.email == new_email
    assert updated_user.id == user.id
