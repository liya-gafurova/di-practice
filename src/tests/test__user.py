import pytest
import pytest_asyncio
from dependency_injector.wiring import inject, Provide

from domain.user.commands import CreateUserDTO, UpdateUserDTO
from domain.user.queries import GetUserDTO, GetUsersDTO, GetUserByNameDTO


@pytest_asyncio.fixture
@inject
async def users(
        clean_db,
        container
):
    app = container.app()
    session = container.db_session()

    added_users = []

    users_data = [
        {'name': 'user name', 'email': 'example@test.com'},
        {'name': 'user2 name', 'email': 'example2@test.com'},
        {'name': 'user3 name', 'email': 'example3@test.com'},
        {'name': 'user4 name', 'email': 'example4@test.com'},
    ]


    for user in users_data:
        added_user = await app.execute(
            CreateUserDTO(name=user['name'], email=user['email']),
            container.db_session()
        )
        added_users.append(added_user)

    return added_users


@pytest.mark.asyncio
@inject
async def test__get_user_by_id(clean_db, container, user):
    app = container.app()

    user_by_id = await app.execute(
        GetUserDTO(id=user.id),
        container.db_session()
    )

    assert user_by_id.name == user.name
    assert user_by_id.id == user.id


@pytest.mark.asyncio
@inject
async def test__get_user_by_name(clean_db, container, user):
    app = container.app()
    user_by_name = await app.execute(GetUserByNameDTO(user.name), container.db_session())

    assert user_by_name.name == user.name
    assert user_by_name.id == user.id



@pytest.mark.asyncio
async def test__get_users(clean_db, container, users):
    app = container.app()
    all_users = await app.execute(GetUsersDTO(), container.db_session())

    sorted_users = sorted(users, key=lambda user: user.id)
    sorted_all_users = sorted(all_users, key=lambda user: user.id)

    assert len(sorted_all_users) == len(sorted_users)

    for user, db_user in zip(sorted_users, sorted_all_users):
        assert user.id == db_user.id
        assert user.name == db_user.name



@pytest.mark.asyncio
async def test__create_user(container, clean_db):
    app = container.app()
    name = 'Name'
    email = 'example@test.com'

    test_user = await app.execute(CreateUserDTO(name=name, email=email), container.db_session())

    assert test_user.name == name
    assert test_user.email == email
    assert test_user.id is not None


@pytest.mark.asyncio
async def test__update_user_by_id(clean_db, container, user):
    app = container.app()
    new_name = 'New Name'
    new_email = 'test@mail.com'

    await app.execute(UpdateUserDTO(id=user.id, name=new_name, email=new_email), container.db_session())

    updated_user = await app.execute(GetUserDTO(id=user.id), container.db_session())

    assert updated_user.name == new_name
    assert updated_user.id == user.id
