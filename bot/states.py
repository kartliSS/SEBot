from aiogram.dispatcher.filters.state import StatesGroup, State


class NewEvent(StatesGroup):
    Type = State()
    Location = State()
    Day = State()
    Month = State()
    Year = State()
    Confirm = State()



