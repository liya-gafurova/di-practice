import asyncio
from datetime import datetime

from dependency_injector.wiring import Provide, inject

from core.dependencies import Container
from core.settings import settings
from domain.user.commands import create_user, CreateUserDTO
from domain.user.queries import GetUserDTO, get_user_by_id


@inject
async def check_user(db_session=Provide[Container.db_session], repo=Provide[Container.user_repo]):
    repo.session = db_session
    new_user = await create_user(CreateUserDTO(name=f'NAME of user {datetime.utcnow()}'))
    user = await get_user_by_id(GetUserDTO(id=new_user.id))
    assert user.id == new_user.id


async def async_main():
    container = Container()
    container.config.from_dict(settings.__dict__)
    container.wire(modules=[__name__])

    await check_user()



def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
