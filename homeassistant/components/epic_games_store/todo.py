"""To-do platform for the Epic Games Store wish list."""

from typing import override

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EGSConfigEntry
from .entity import EGSWishListEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EGSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the wish list to-do list."""
    async_add_entities(
        [EGSWishListTodo(entry.runtime_data.wish_list, entry.entry_id, "wish_list")]
    )


class EGSWishListTodo(EGSWishListEntity, TodoListEntity):
    """The games on the wish list."""

    # Games are added through the select entity, which only offers catalog games
    _attr_supported_features = (
        TodoListEntityFeature.UPDATE_TODO_ITEM | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    @property
    @override
    def todo_items(self) -> list[TodoItem]:
        """Return the wish listed games."""
        return [
            TodoItem(
                summary=game["title"],
                uid=game["id"],
                status=(
                    TodoItemStatus.COMPLETED
                    if game.get("completed")
                    else TodoItemStatus.NEEDS_ACTION
                ),
            )
            for game in self._wish_list.games
        ]

    @override
    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Tick a game off the wish list; titles come from the catalog."""
        assert item.uid
        await self._wish_list.async_set_completed(
            item.uid, item.status == TodoItemStatus.COMPLETED
        )

    @override
    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Remove games from the wish list."""
        await self._wish_list.async_remove(set(uids))
