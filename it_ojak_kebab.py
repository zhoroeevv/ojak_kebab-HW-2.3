# Напишите телеграмм бот для ojak kebab.


# Цель телеграмм бота выдавать информацию о заведении (меню, о нас, адрес,
# заказать еду)
# Сделайте кнопки (меню, о нас, адрес, заказать еду)
# (Доп задание) И также сделайте так при нажатии кнопки запустить чтобы данные
# пользователей сохранились в базу данных (id, username, first_name, last_name,
# date_joined)
# При нажатии кнопки меню, пусть ему отправляются меню из этого сайта
# https://nambafood.kg/ojak-kebap (раздел шашлыки)
# При нажатии кнопки о нас, пусть ему отправится информация с сайта
# https://ocak.uds.app/c/about
# При нажатии кнопки адрес, пусть ему отправится информация об адресе заведения
# ДОП ЗАДАНИЕ:
# И также при нажатии кнопки заказать еду, то вы должны у пользователя запросить
# данные как имя, номер телефона, адрес доставки и также после получения данных
# записать в базу данных
# Загрузить код в GitHub и не забудьте использовать файл .gitignore
# Дедлайн 2 урока. Сдать ДЗ до 14.12.2023



from config import token 
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
import logging, sqlite3, time 

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

connection = sqlite3.connect('itbot.db')
cursor = connection.cursor()
cursor.execute(f""" CREATE TABLE IF NOT EXISTS users(
    id INTEGER, 
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    user_name VARCHAR(100),
    date_joined VARCHAR(100)
);
""")     

cursor.execute(f"""CREATE TABLE IF NOT EXISTS lids(
    id INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    direction VARCHAR(100),
    phone VARCHAR(100),
    tg_user VARCHAR(255),
    created VARCHAR (100)
);
""")


start_keyboard = [ 
    types.KeyboardButton("Меню"), 
    types.KeyboardButton("Адрес"), 
    types.KeyboardButton("О Нас"), 
    types.KeyboardButton("Заказать еду") ]

start_button = types.ReplyKeyboardMarkup().add(*start_keyboard)

@dp.message_handler(commands= 'start')
async def start(message: types.Message):
    print (message)
    cursor.execute(f"SELECT id FROM users WHERE id = {message.from_user.id};")
    output_cursor = cursor.fetchall()
    print (output_cursor)
    if output_cursor == []:
        cursor.execute(f"INSERT INTO users VALUES (?,?,?,?,?)", (
        message.from_user.id, message.from_user.first_name,
        message.from_user.last_name, message.from_user.username, time.ctime()
        ))
        cursor.connection.commit()
    await message.answer(f'Привет {message.from_user.full_name}' ,reply_markup=start_button)

@dp.message_handler(commands='start') 
async def start(message:types.Message): 
    print(message) 
    await message.answer(f"Здраствуйте! {message.from_user.full_name}", 
    reply_markup=start_button) 

     
@dp.message_handler(text='Меню') 
async def menu(message:types.Message): 
    await message.reply(f'https://nambafood.kg/ojak-kebap') 
          
@dp.message_handler(text='Адрес') 
async def send_address(message:types.Message): 
    await message.reply(f"Наш адрес ​Курманжан датка, 209, 1 этаж, 3 филиала Ош") 
    await message.answer_location(40.526486, 72.795345) 
     
@dp.message_handler(text='О Нас') 
async def about_Us(message:types.Message): 
    await message.reply(f"информация О Нас  https://ocak.uds.app/c/about ") 


#Заказать еду
class LidsState(StatesGroup):
    first_name = State()
    last_name = State()
    direction = State()
    phone = State()

@dp.message_handler(text="Заказать еду") 
async def start_lids(message:types.Message): 
    await message.answer(f"{message.from_user.full_name} чтобы заказать еду заполните поля")
    await message.answer("Как: Имя, Фамилия, Адрес, Номер")
    await message.answer("Введите свое имя:")
    await LidsState.first_name.set()
    
@dp.message_handler(state=LidsState.first_name) 
async def get_last_name(message:types.Message, state:FSMContext): 
    await state.update_data(first_name=message.text)
    await message.answer("Введите фамилию:")
    await LidsState.last_name.set()
    
@dp.message_handler(state=LidsState.last_name) 
async def get_direction(message:types.Message, state:FSMContext): 
    await state.update_data(last_name=message.text)
    await message.answer("Введите адрес доставки:")
    await LidsState.direction.set()
    
@dp.message_handler(state=LidsState.direction) 
async def get_phone(message:types.Message, state:FSMContext): 
    await state.update_data(direction=message.text)
    await message.answer("Введите номер телефона:")
    await LidsState.phone.set()
    
@dp.message_handler(state=LidsState.phone) 
async def get_phone(message:types.Message, state:FSMContext): 
    await state.update_data(phone=message.text)
    await message.answer("сохраню данные...")
    result = await storage.get_data(user=message.from_user.id)
    print(result)

    cursor.execute("INSERT INTO lids VALUES (?,?,?,?,?,?);",
                  (result['first_name'], result['last_name'],
                   result ['direction'], result ['phone'],
                   f"{message.from_user.id} {message.from_user.username}",
                   time.ctime()) )
    cursor.connection.commit()
    await message.answer("данные записаны на базу")
    await state.finish()

@dp.message_handler(text="назад") 
async def backroll(message:types.Message): 
    await start(message)


executor.start_polling(dp)