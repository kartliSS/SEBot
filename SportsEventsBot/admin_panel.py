import datetime
from aiogram.utils.exceptions import BotBlocked
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
import asyncio
from config import admin_id
from load_all import dp, bot
from states import NewEvent
import database
from aiogram.utils.callback_data import CallbackData
from database import Event

db = database.DBCommands()
us_ev = CallbackData("user_event", "event_id")
DELAY = 60*60*24


@dp.message_handler(user_id=admin_id, commands=["cancel"], state=NewEvent)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили создание товара!\n"
                         "Открыть меню:\t/menu")
    await state.reset_state()


@dp.message_handler(user_id=admin_id, commands=["showusers"])
async def show_users(message: types.Message):
    all_users = await db.show_users()
    await message.answer("<u>Список всех пользователей:</u>\n")
    for user in all_users:
        text = ("<b>Пользователь \t№{id}:</b> {username}\n"
                "Имя: \t{fullname}\n"
                "ID пользователя: \t{user_id}\n")
        await message.answer(text.format(id=user.id, username=user.username,
                                         fullname=user.fullname, user_id=user.user_id))
    await message.answer("Вернуться в меню:\t/menu")


@dp.message_handler(user_id=admin_id, commands=["users_events"])
async def show_events_for_users(message: types.Message):
    all_events = await db.show_events()
    await message.answer("<u>Список мероприятий:</u>")
    text = ("<b>Мероприятие</b> \t№{id}: <u>{type}</u>\n"
            "<b>Место:</b> \t{location}\n"
            "<b>Дата:</b> \t{date}\n")
    for event in all_events:
        markup_evus = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text=("Посмотреть"), callback_data=us_ev.new(event_id=event.id)
                )]
            ]
        )
        await message.answer(text.format(id=event.id, type=event.type,
                                         location=event.location, date=event.date), reply_markup=markup_evus)


@dp.callback_query_handler(us_ev.filter())
async def users_at_events(call: CallbackQuery, callback_data: dict, state: FSMContext):
    event_id = int(callback_data.get("event_id"))
    await call.message.edit_reply_markup()
    users = await db.show_ev_us(event_id)
    await call.message.answer(f"<u>Список, подписанных пользователей на мероприятие №{event_id}</u>")
    for user in users:
        text = ("<b>Пользователь №{id}:</b> {username}\n"
                "Имя: \t{fullname}\n"
                "ID пользователя: \t{user_id}\n")
        await call.message.answer(text.format(id=user.id, username=user.username,
                                              fullname=user.fullname, user_id=user.user_id))
    await call.message.answer("Вернуться в меню: /menu")


@dp.message_handler(user_id=admin_id, commands=["addevent"])
async def add_event(message: types.Message):
    await message.answer("Введите название мероприятия, например 'Футбол',\n"
                         "или нажмите /cancel")
    await NewEvent.Type.set()


@dp.message_handler(user_id=admin_id, state=NewEvent.Type)
async def enter_type(message: types.Message, state: FSMContext):
    type = message.text
    event = Event()
    event.type = type
    await message.answer(f"Название: {type}\n"
                         f"Введите место проведение или нажмите /cancel")
    await NewEvent.Location.set()
    await state.update_data(event=event)


@dp.message_handler(user_id=admin_id, state=NewEvent.Location)
async def enter_location(message: types.Message, state: FSMContext):
    location = message.text
    data = await state.get_data()
    event: Event = data.get("event")
    event.location = location
    await message.answer(f"Название: {event.type}\n"
                         f"Место проведение: {location}\n"
                         f"Введите день проведения или нажмите /cancel")
    await NewEvent.Day.set()
    await state.update_data(event=event)


@dp.message_handler(user_id=admin_id, state=NewEvent.Day)
async def enter_day(message: types.Message, state: FSMContext):
    data = await state.get_data()
    event: Event = data.get("event")
    day = int(message.text)
    if 0 < day < 32:
        await message.answer(f"День проведения: {day}\n"
                             f"Введите месяц проведения или нажмите /cancel\n")
        await NewEvent.Month.set()
        await state.update_data(event=event, day=day)
    else:
        await message.answer("Неверный формат даты попробуйте снова\n"
                             "или нажмите /cancel")
        return


@dp.message_handler(user_id=admin_id, state=NewEvent.Month)
async def enter_month(message: types.Message, state: FSMContext):
    data = await state.get_data()
    day = data.get("day")
    event: Event = data.get("event")
    month = int(message.text)
    if 0 < month < 13:
        await message.answer(f"День проведения: {day}\n"
                             f"Месяц проведения: {month}\n"
                             f"Введите год проведения или нажмите /cancel\n")
        await NewEvent.Year.set()
        await state.update_data(event=event, day=day, month=month)
    else:
        await message.answer("Неверный формат даты попробуйте снова\n"
                             "или нажмите /cancel")
        return


@dp.message_handler(user_id=admin_id, state=NewEvent.Year)
async def enter_year(message: types.Message, state: FSMContext):
    data = await state.get_data()
    day = data.get("day")
    month = data.get("month")
    event: Event = data.get("event")
    year = int(message.text)
    if 2020 < year < 2040:
        date = datetime.date(year, month, day)
        event.date = date
        markup_confirm = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text=("Подтверждаю"),
                    callback_data="confirm")],
                [types.InlineKeyboardButton(
                    text=("Ввести заново"),
                    callback_data="change")]
            ]
        )
        await message.answer(f"Название: {event.type}\n"
                             f"Место проведение: {event.location}\n"
                             f"Дата проведения: {date}\n"
                             f"Подтверждаете? Нажмите /cancel чтобы отменить создание мероприятия",
                             reply_markup=markup_confirm)
        await state.update_data(event=event)
        await NewEvent.Confirm.set()
    else:
        await message.answer("Неверный формат даты попробуйте снова\n"
                             "или нажмите /cancel")
        return


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewEvent.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново информацию о мероприятии\n"
                              "Название:")
    await NewEvent.Type.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewEvent.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    event: Event = data.get("event")
    await event.create()
    users = await db.show_users()
    for user in users:
        try:
            text = ("<u>Организовано новое мероприятие:\n</u>"
                    f"<b>Мероприятие</b> \t№{event.id}: <u>{event.type}</u>\n"
                    f"<b>Место:</b> \t{event.location}\n"
                    f"<b>Дата:</b> \t{event.date}\n")
            await bot.send_message(chat_id=user.user_id, text=text)
        except Exception:
            pass

    await call.message.answer("Мероприятие удачно создано.\n"
                              "Открыть меню:\t/menu")
    await state.reset_state()


async def mailing():
    all_events = await db.show_events()
    date = datetime.date.today()
    users = await db.show_users()
    for event in all_events:
        event_date = event.date
        diff = event_date - date
        if diff.days == 0 or diff.days == 3 or diff.days == 7:
            for user in users:

                text = (f"<u>Напоминание!!!\n</u>"
                        f"<b>Мероприятие</b> \t№{event.id}: <u>{event.type}</u>\n"
                        f"<b>Место:</b> \t{event.location}\n"
                        f"<b>Дата:</b> \t{event.date}\n")
                try:
                    await bot.send_message(chat_id=user.user_id, text=text)
                except BotBlocked:
                    break


def repeat(coro, loop):
    asyncio.ensure_future(coro, loop=loop)
    loop.call_later(DELAY, repeat, coro, loop)

