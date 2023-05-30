import asyncio
from config import LOGIN, PASS, DB_NAME, HOST, TOKEN
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from parser import finaly_parse
from working import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlalchemy as db
from sqlalchemy.orm import Session
from model import Users
import aioschedule

API_TOKEN = TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

allowed_command = ["/start", "/help", "/activate", "/add_anime", "/deactivate", "/get_my_anime", "/delete_anime"]

HELP_COMMAND = """
<b>/help</b> - <em>command list</em>
<b>/start</b> - <em>start bot</em> 
<b>/activate</b> - <em>if you wont stay tuned for anime</em> 
<b>/add_anime</b> -<em> send the anime you want track </em>
<b>/get_my_anime_list</b> -<em> show your anime </em>
<b>/delete_anime</b> -<em> delete anime from your list </em>
<b>/deactivate</b> -<em> unsubscribe from mailing lists  </em>
"""


kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_start.add(KeyboardButton('/help'))

kb_help = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_help.add(KeyboardButton('/help'))
kb_help.add(KeyboardButton('/activate'))

kb_agree = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_agree.add(KeyboardButton('/help'))
kb_agree.add(KeyboardButton('/activate'))
kb_agree.add(KeyboardButton('/add_anime'))
kb_agree.add(KeyboardButton('/get_my_anime'))
kb_agree.add(KeyboardButton('/delete_anime'))
kb_agree.add(KeyboardButton('/deactivate'))
kb_agree.add(KeyboardButton('/delete_anime'))



class ClientStatesGroup(StatesGroup):
    send_anime = State()
    send_update = State()
    delete_anime = State()


@dp.message_handler(lambda message: message.get_command() not in allowed_command)
async def answer_unknown_command(message: types.Message):
    await message.answer(f"Not available this command: {message.text}\nSend /help for see allowed commands")


@dp.message_handler(commands=['start'])
async def send_welkome(message: types.Message) -> None:
    hello = "Hi, i can help you keep track of new episodes of your favorite anime"
    await message.answer(text=hello, reply_markup=kb_start)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message) -> None:
    await message.answer(text=HELP_COMMAND, parse_mode='HTML', reply_markup=kb_agree)


@dp.message_handler(commands=['activate'])
async def agree_command(message: types.Message) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    if connect_base_users(user_id, user_name) == 0:
        create_user_personal_base(user_id)
        if check_status(user_id) == "inactive":
            change_status(user_id, "active")
        await message.answer(text="We remember you <3", reply_markup=kb_agree)
    else:
        await message.answer(text="Okeeey, let's gooooo.....")


@dp.message_handler(commands=['deactivate'])
async def agree_command(message: types.Message) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    if connect_base_users(user_id, user_name) == 1:
        await message.answer(text="You are already unsubscribed from the mailing list", reply_markup=kb_agree)
    else:
        if check_status(user_id) == "active":
            change_status(user_id, "inactive")
            await message.answer(text="It was a pleasure doing business with you", reply_markup=kb_agree)
        else:
            await message.answer(text="You are already unsubscribed from the mailing list", reply_markup=kb_agree)


@dp.message_handler(commands=['get_my_anime'])
async def get_user_anime(message: types.Message):
    if check_user_on_base(message.from_user.id) == 0:
        await message.answer(text="You should send '/activate' before")
    else:
        my_list = get_anime_list(message.from_user.id)
        ans = ""
        if len(my_list) == 0:
            await message.answer(text="There's no anime on your list")
        else:
            number = 0
            for anime in my_list:
                number += 1
                ans += f"{number} - {anime}\n"
            ans += f"Total number: {number}"
            await message.answer(text=ans)


@dp.message_handler(commands=['add_anime'])
async def send_anime(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await ClientStatesGroup.send_anime.set()
    await message.answer(
        text="Okey, Enter a anime name in your next message in ru language..\nI now it's weird because "
             "i'm tаlking to you in another language,\nbut i just need to practice my english")


@dp.message_handler(state=ClientStatesGroup.send_anime)
async def get_anime_name(message: types.Message, state: FSMContext):
    name = message.text
    if check_user_on_base(message.from_user.id) == 0:
        await message.answer(text="You should send '/activate' before")
    else:
        name = client_api(name)
        if name != 0:
            if not add_anime_in_user_base(message.from_user.id, name):
                await message.answer(text="Ooop's anime already in list,\ntry another name")
            else:
                await message.answer(text="We adedd this anime in your list")
        else:
            await message.answer(text="Sorry, I don't have this anime in my database(((\nTry send another name ")
    await state.finish()


@dp.message_handler(commands=['delete_anime'])
async def delete_anime(message: types.Message):
    await ClientStatesGroup.delete_anime.set()
    await message.answer(text="send the anime you want to delete")


@dp.message_handler(state=ClientStatesGroup.delete_anime)
async def delete_anime_state(message: types.Message, state: FSMContext):
    name = message.text
    user_id = message.from_user.id
    if check_user_on_base(user_id) == 0:
        await message.answer(text="You should send '/activate' before")
    else:
        if check_anime_in_user_base(name, user_id) is None:
            await message.answer(text="There's no such anime on your list")
        else:
            delete_anime_from_user(user_id, name)
            await message.answer(text="Anime delete successfully")
    await state.finish()


@dp.message_handler()
async def send_new_episode():
    engine = db.create_engine(f"postgresql://{LOGIN}:{PASS}@{HOST}/{DB_NAME}")
    new_list = check_new_episode_or_anime(finaly_parse())
    with Session(autoflush=False, bind=engine) as session:
        users = session.query(Users).filter(Users.status == "active")
        for user in users:
            user_id = user.user_id
            # print(new_list)
            for el in new_list:
                name = None
                name = check_anime_in_user_base(el, user_id)
                # print(name)
                if name is None:
                    pass
                else:
                    await bot.send_message(user_id, text=f"Hello, pidor, the new series of '<em><b>{name}</b></em>' has been released", parse_mode='HTML')



@dp.message_handler()
async def send_egor():
    await bot.send_message(1368953736, text="PIDOR")


async def scheduler():
    aioschedule.every().day.at("18:00").do(send_new_episode)
    aioschedule.every(1).day.at("20:24").do(send_new_episode)
    aioschedule.every().day.at("06:00").do(send_egor)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(5)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    # dp.loop.create_task(periodic())
    # print(type(dp))
    # scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
