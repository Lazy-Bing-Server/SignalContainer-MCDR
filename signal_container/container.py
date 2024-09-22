import json

from mcdreforged.api.all import *
from typing import Tuple, Optional


class InventoryProperty(Serializable):
    id: str
    Count: int
    Slot: int


class Container:
    def __init__(self, container_item: str, max_slots: int, allow_overstack_under_15: bool, stackable_fillings: str, unstackable_fillings: str):
        self.__id = container_item
        self.__slots = max_slots
        self.__allow_overstack_under_15 = allow_overstack_under_15
        self.__stackable_item = stackable_fillings
        self.__unstackable_item = unstackable_fillings

    def get_interval_count(self):
        return self.__slots * 64 / 14

    def get_item_count(self, signal: int) -> int:
        if signal == 0:
            return 0
        if signal == 15:
            return self.__slots * 64
        interval_item_count = self.get_interval_count()
        required_intervals = signal - 1
        return int(1 + (required_intervals * interval_item_count))

    def get_item_stack(self, signal: int) -> Optional[Tuple[int, int, int]]:
        """
        :param signal: signal
        :return: "unstackable" item full stack count, "unstackable" item count, stackable item count
        """
        if signal < 0:
            return None
        item_count = self.get_item_count(signal)
        stackable_item_count = item_count % 64
        stackable_stack_count = int(item_count / 64)
        unstackable_stack_count = int(stackable_stack_count / 64)
        unstackable_item_count = stackable_stack_count % 64
        if unstackable_stack_count + 1 > self.__slots:
            return None
        return unstackable_stack_count, unstackable_item_count, stackable_item_count

    def get_give_command(self, player: str, signal: int):
        slot_list = []
        item_stack_info = self.get_item_stack(signal)
        if item_stack_info is None:
            return None
        unstackable_stack, unstackable_item, stackable_item = item_stack_info
        while True:
            if unstackable_stack > 0:
                slot_list.append(
                    InventoryProperty(id=self.__unstackable_item, Slot=len(slot_list), Count=64)
                )
                unstackable_stack -= 1
            elif (unstackable_item >= self.__slots and stackable_item > 0) or (unstackable_item > 0 and self.__allow_overstack_under_15):
                slot_list.append(
                    InventoryProperty(id=self.__unstackable_item, Slot=len(slot_list), Count=unstackable_item)
                )
                unstackable_item = 0
            elif unstackable_item > 0 and not self.__allow_overstack_under_15:
                slot_list.append(
                    InventoryProperty(id=self.__unstackable_item, Slot=len(slot_list), Count=1)
                )
                unstackable_item -= 1
            elif stackable_item > 0:
                slot_list.append(
                    InventoryProperty(id=self.__stackable_item, Slot=len(slot_list), Count=stackable_item)
                )
                stackable_item = 0
            elif unstackable_item < 0 or unstackable_stack < 0 or stackable_item < 0:
                raise ValueError("Error occurred in data process: Illegal negative values found")
            else:
                break
        return f"give {player} {self.__id}" + "{BlockEntityTag:{Items:" + \
               json.dumps(serialize(slot_list), ensure_ascii=False) + "}} 1"


if __name__ == "__main__":
    container = Container("dropper", 9, False, 'shears', 'iron_nugget')
    for sig in range(0, 19):
        print(f'{sig} = {container.get_item_count(sig)} = {container.get_item_stack(sig)}')


