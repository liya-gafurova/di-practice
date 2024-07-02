import asyncio

from dependencies import Container
from user.queries import GetUserDTO, get_user_by_id
from user.commands import CreateUserDTO, create_user


async def async_main():
    container = Container()
    container.wire(modules=[__name__])

    new_user = await create_user(CreateUserDTO(name='NAME of user'))
    usr = await get_user_by_id(GetUserDTO(id=new_user.id))

    print(usr.id)


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
