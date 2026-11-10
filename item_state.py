from enum import IntEnum


class Item(IntEnum):
    NONE = 0
    SMALL = 1
    LARGE = 2


selected = Item.SMALL


def select(value):
    global selected
    selected = Item(value)


def reset():
    select(Item.SMALL)
