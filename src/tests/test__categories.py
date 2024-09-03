import pytest

from domain.category.commands import update_category, UpdateCategoryDTO, delete_category, DeleteCategoryByIdDTO
from domain.category.commands.create_category import create_general_category, CreateGeneralCategoryDTO, \
    create_custom_category, CreateCustomCategoryDTO
from domain.category.queries import GetCategoryByIdDTO, get_category_by_id, get_categories, GetCategoriesDTO
from shared.exceptions import EntityNotFoundException, ThisActionIsForbidden
from tests.conftest import existing_general_category, existing_custom_category, existing_custom_category__another_user


@pytest.mark.asyncio
async def test__create_general_category(clean_db, container):
    category = 'food'
    new_category = await create_general_category(
        CreateGeneralCategoryDTO(name=category)
    )

    assert new_category.name == category
    assert new_category.user_id is None
    assert new_category.id is not None


@pytest.mark.asyncio
async def test__create_custom_category(clean_db, container, user):
    category = 'sport'
    new_category = await create_custom_category(
        CreateCustomCategoryDTO(name=category, user_id=user.id)
    )

    assert new_category.name == category
    assert new_category.user_id == user.id
    assert new_category.id is not None


@pytest.mark.asyncio
async def test__create_custom_category__another_user_with_same_category(
        clean_db,
        container,
        user,
        existing_custom_category__another_user
):
    category_name = existing_custom_category__another_user.name
    new_category = await create_custom_category(
        CreateCustomCategoryDTO(name=category_name, user_id=user.id)
    )

    assert new_category.name == existing_custom_category__another_user.name
    assert new_category.user_id == user.id
    assert new_category.id is not None


@pytest.mark.asyncio
async def test__update_general_category(clean_db, container, user, existing_general_category):
    new_category_name = 'FOOD'

    with pytest.raises(ThisActionIsForbidden):
        updated = await update_category(
            UpdateCategoryDTO(
                id=existing_general_category.id,
                user_id=user,
                name=new_category_name
            )
        )


@pytest.mark.asyncio
async def test__update_custom_category(clean_db, container, user, existing_custom_category):
    new_name = 'JEANS'

    updated = await update_category(
        UpdateCategoryDTO(
            id=existing_custom_category.id,
            user_id=user.id,
            name=new_name
        )
    )

    assert updated.id == existing_custom_category.id
    assert updated.name == new_name
    assert updated.user_id == user.id


@pytest.mark.asyncio
async def test__update_custom_category__another_user(clean_db, container, another_user, existing_custom_category):
    new_name = 'JEANS'

    with pytest.raises(EntityNotFoundException):
        updated = await update_category(
            UpdateCategoryDTO(
                id=existing_custom_category.id,
                user_id=another_user.id,
                name=new_name
            )
        )


@pytest.mark.asyncio
async def test__delete_custom_category(
        clean_db,
        container,
        user,
        existing_custom_category
):
    result = await delete_category(
        DeleteCategoryByIdDTO(
            id=existing_custom_category.id,
            user_id=user.id
        )
    )

    with pytest.raises(EntityNotFoundException):
        deleted = await get_category_by_id(
            GetCategoryByIdDTO(
                id=existing_custom_category.id,
                user_id=user.id
            )
        )


@pytest.mark.asyncio
async def test__delete_general_category(
        clean_db,
        container,
        user,
        existing_general_category
):
    with pytest.raises(ThisActionIsForbidden):
        result = await delete_category(
            DeleteCategoryByIdDTO(
                id=existing_general_category.id,
                user_id=user.id
            )
        )

    not_deleted = await get_category_by_id(
        GetCategoryByIdDTO(
            id=existing_general_category.id,
            user_id=user.id
        )
    )

    assert not_deleted == existing_general_category


@pytest.mark.asyncio
async def test__add_category_that_was_deleted(
        clean_db,
        container,
        user,
        existing_custom_category
):
    await delete_category(
        DeleteCategoryByIdDTO(
            id=existing_custom_category.id,
            user_id=user.id
        )
    )

    new_category = await create_custom_category(
        CreateCustomCategoryDTO(
            user_id=user.id,
            name=existing_custom_category.name
        )
    )


@pytest.mark.asyncio
async def test__get_custom_by_id_category(
        clean_db,
        container,
        user,
        existing_custom_category,
        existing_general_category
):
    category = await get_category_by_id(
        GetCategoryByIdDTO(
            id=existing_custom_category.id,
            user_id=user.id
        )
    )

    assert category.id == existing_custom_category.id
    assert category.user_id == user.id
    assert category.name == existing_custom_category.name


@pytest.mark.asyncio
async def test__get_general_by_id_category(
        clean_db,
        container,
        user,
        existing_custom_category,
        existing_general_category
):
    category = await get_category_by_id(
        GetCategoryByIdDTO(
            id=existing_general_category.id,
            user_id=user.id
        )
    )

    assert category.id == existing_general_category.id
    assert category.user_id is None
    assert category.name == existing_general_category.name


@pytest.mark.asyncio
async def test__list_all_user_categories(
        clean_db,
        container,
        user,
        existing_custom_category,
        existing_general_category,
        existing_custom_category__another_user
):
    categories = await get_categories(
        GetCategoriesDTO(
            user_id=user.id
        )
    )

    assert len(categories) == 2
    assert categories[0].id == existing_custom_category.id
    assert categories[0].name == existing_custom_category.name
    assert categories[0].user_id == existing_custom_category.user_id
    assert categories[1].id == existing_general_category.id
    assert categories[1].name == existing_general_category.name
    assert categories[1].user_id is None


@pytest.mark.asyncio
async def test__list_custom_categories(
        clean_db,
        container,
        user,
        existing_custom_category,
        existing_general_category,
        existing_custom_category__another_user
):
    categories = await get_categories(
        GetCategoriesDTO(
            user_id=user.id,
            with_general=False
        )
    )

    assert len(categories) == 1
    assert categories[0].id == existing_custom_category.id
    assert categories[0].name == existing_custom_category.name
    assert categories[0].user_id == existing_custom_category.user_id
