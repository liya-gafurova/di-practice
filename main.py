import asyncio

from core.dependencies import Container
from domain.user.commands import create_user, CreateUserDTO
from domain.user.queries import GetUserDTO, get_user_by_id


async def async_main():
    container = Container()
    container.wire(modules=[__name__])

    new_user = await create_user(CreateUserDTO(name='NAME of user'))
    user = await get_user_by_id(GetUserDTO(id=new_user.id))
    assert user.id == new_user.id


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
