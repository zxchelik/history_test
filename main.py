import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputFile, \
    InputMediaPhoto, FSInputFile

import settings
from database import Database

bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
db = Database("db.json")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# class
class Test(StatesGroup):
    q = State()
    a = State()


answer_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="a", callback_data="a"),
     InlineKeyboardButton(text="c", callback_data="c")],
    [InlineKeyboardButton(text="b", callback_data="b"),
     InlineKeyboardButton(text="d", callback_data="d")]
])
start_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Да", callback_data="start")]])
next_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Дальше", callback_data="start")]])


@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    media = InputMediaPhoto(type='photo', media=FSInputFile())

    await message.answer_media_group(media=media,caption="Вы готовы начать тест?", reply_markup=start_kb)
    await state.set_state(Test.q)
    await state.update_data(id=0)
    await state.update_data(score=0)


@dp.callback_query(StateFilter(Test.q))
async def ask_q(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id_ = data.get('id')
    q = db.get_question(id_)
    if not (q is None):
        media = InputMediaPhoto(type='photo', media=FSInputFile(f"photos/{id_}.jpeg"))
        await callback.message.edit_media(caption=q['text'], reply_markup=answer_kb, media=media)
        await state.set_state(Test.a)
    else:
        score = data.get('score')
        text = f"""Тест закончился.
Твой результат : {score}/{id_}"""
        await callback.message.edit_text(text=text)
        await state.clear()


@dp.callback_query(StateFilter(Test.a))
async def ans_q(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id_ = data.get('id')
    score = data.get('score')

    q = db.get_question(id_)
    text = ''
    if callback.data == q["correct_answer"]:
        text += "✅ Верно!\n\n"
        score += 1
    else:
        text += "❌ Не верно 😢\n\n"
    text += q.get("desk")
    await state.update_data(score=score, id=id_ + 1)
    await state.set_state(Test.q)
    await callback.message.edit_text(text=text, reply_markup=next_kb)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
