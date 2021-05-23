from aiogram.utils.exceptions import BotBlocked
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery)
from aiogram.utils.callback_data import CallbackData
import database
from config import admin_id
from load_all import dp, bot

db = database.DBCommands()

# Используем CallbackData для работы с коллбеками
sub_ev = CallbackData("sub", "event_id", "user_id")
unsub_ev = CallbackData("unsub", "event_id", "user_id")


# Для команды /start есть специальный фильтр, который можно тут использовать
@dp.message_handler(CommandStart())
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    user = await db.add_new_user()

    text = ("Приветствую!\n"
            "Этот бот поможет Вам записаться на спортивные мероприятия!\n"
            "Открыть меню:\t /menu")
    try:
        await bot.send_message(chat_id, text)
    except BotBlocked:
        None



@dp.message_handler(commands=["menu"])
async def show_menu(message: Message):
    chat_id = message.from_user.id
    if message.from_user.id == admin_id:
        text = ("Добавить новое мероприятие:\t /addevent\n"
                "Посмотреть список мероприятий:\t /showallevents\n"
                "Посмотреть список мероприятий, на которые Вы подписаны:\t /showmyevents\n"
                "Посмотреть список пользователей системы:\t /showusers\n"
                "Посмотреть список пользователей на конкретном мероприятии:\t/users_events\n")

    else:
        text = ("Посмотреть список мероприятий:\t /showallevents\n"
                "Посмотреть список мероприятий, на которые Вы подписаны:\t /showmyevents\n")
    await bot.send_message(chat_id, text)


@dp.message_handler(commands=["showallevents"])
async def show_events(message: Message):
    all_events = await db.show_events()
    user_id = message.from_user.id
    text = ("<b>Мероприятие</b> \t№{id}: <u>{type}</u>\n"
            "<b>Место:</b> \t{location}\n"
            "<b>Дата:</b> \t{date}\n")
    for event in all_events:
        markup_allevents = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "Подписаться" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Подписаться"),
                                         callback_data=sub_ev.new(event_id=event.id, user_id=user_id))
                ],
            ]
        )
        await message.answer(text.format(id=event.id,
                                         type=event.type,
                                         location=event.location,
                                         date=event.date),
                             reply_markup=markup_allevents)
    await message.answer("Вернуться в меню: \t/menu")


# Для фильтрования по коллбекам можно использовать sub_ev.filter()
@dp.callback_query_handler(sub_ev.filter())
async def sub_env(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    event_id = int(callback_data.get("event_id"))
    await call.message.edit_reply_markup()
    user_id = int(callback_data.get("user_id"))
    all_check = await db.show_check()
    user = await db.get_user(user_id)
    ID = user.id
    for check in all_check:
        if check.user_id == ID and check.event_id == event_id:
            text = "Вы уже подписаны на данное мероприятие!\n" \
                   "Вернуться в меню:\t/menu"
            await call.message.answer(text)
            return

    await db.sub_event(ID, event_id)
    text = ("Вы подписались на данное мероприятие!\n"
            "Вернуться в меню:\t/menu")
    await call.message.answer(text)


@dp.message_handler(commands=["showmyevents"])
async def my_events(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    ID = user.id
    flag = True
    text = ("<b>Вы подписаны на:</b>\n"
            "<b>Мероприятие</b> \t№{id}: <u>{type}</u>\n"
            "<b>Место:</b> \t{location}\n"
            "<b>Дата:</b> \t{date}\n")
    all_check = await db.show_check()
    for check in all_check:
        if ID == check.user_id:
            event_id = check.event_id
            event = await db.show_my_events(event_id)
            markup_myevents = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        # Создаем кнопку "Отписаться" и передаем ее айдишник в функцию создания коллбека
                        InlineKeyboardButton(text=("Отписаться"),
                                             callback_data=unsub_ev.new(event_id=event.id, user_id=user_id))
                    ],
                ]
            )
            await message.answer(text.format(id=event.id,
                                             type=event.type,
                                             location=event.location,
                                             date=event.date),
                                 reply_markup=markup_myevents)
            flag = False
    await message.answer("Вернуться в меню:\t/menu")
    if flag == True:
        text = "Вы не подписаны ни на одно из мероприятий!\n"
        await message.answer(text)


# Для фильтрования по коллбекам можно использовать unsub_ev.filter()
@dp.callback_query_handler(unsub_ev.filter())
async def unsub_env(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    event_id = int(callback_data.get("event_id"))
    await call.message.edit_reply_markup()
    user_id = int(callback_data.get("user_id"))
    all_check = await db.show_check()

    user = await db.get_user(user_id)
    ID = user.id
    for check in all_check:
        if check.user_id == ID and check.event_id == event_id:
            await db.unsub_event(ID, event_id)
            text = ("Вы успешно отписались от данного мероприятия!\n"
                    "Вернуться в меню:\t/menu")
            await call.message.answer(text)
            return
