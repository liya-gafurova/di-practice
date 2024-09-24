import asyncio
from datetime import datetime

from dependency_injector.wiring import Provide, inject

from core.dependencies import Container
from core.settings import settings
from domain.user.commands import CreateUserDTO
from domain.user.queries import GetUserDTO

@inject
async def check_user(container=Provide[Container]):
    app = container.app()
    new_user = await app.execute(CreateUserDTO(name=f'NAME of user {datetime.utcnow()}'), container.db_session())
    user = await app.execute(GetUserDTO(id=new_user.id), container.db_session(()))
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
