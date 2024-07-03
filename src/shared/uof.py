

def unit_of_work(function):
    async def wrapper(*args, **kwargs):
        assert kwargs.get('db_session') is not None

        asyncSession = kwargs['session']
        async with asyncSession() as async_session:
            async with async_session.begin():
                try:
                    await function(*args, **kwargs)
                except Exception as e:
                    print(e.args)

    return wrapper

