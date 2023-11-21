from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram import F
from  sqlite3 import  connect
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import requests
import re

bot1 = Bot('6326825722:AAEpqSunJLVtjehwam1w5kUCE-Tl0ue3l7Y')
dp = Dispatcher()
'''Функция для расписания'''
def response_rasp(name_group, data):

    group = name_group
    data = "2023-" + data.replace("." , "-").replace(" ", "-")
    groups = {}
    url_responce = 'https://edu.donstu.ru/api/raspGrouplist'
    grouplist = requests.get(url_responce)
    info = grouplist.json()

    for i in info["data"]:
        groups.update({i["name"] : i["id"]})
    url = "https://edu.donstu.ru/api/Rasp?idGroup=" + str(groups[group.upper()]) + "&sdate=" + data
    response = requests.get(url)
    rasp = response.json()

    message = ""
    for i in range(0, len(rasp["data"]["rasp"])):
        if rasp["data"]["rasp"][i]["дата"] == str(data) + "T00:00:00":
            message += f"Пара №{rasp['data']['rasp'][i]['номерЗанятия']}\n🗒 Дисциплина: {rasp['data']['rasp'][i]['дисциплина']}\n👩‍🏫 Преподаватель: {rasp['data']['rasp'][i]['преподаватель']}\n🕰 Начало в {rasp['data']['rasp'][i]['начало']} до {rasp['data']['rasp'][i]['конец']}\nАудитория: {rasp['data']['rasp'][i]['аудитория']}\n\n"
    if message == '':
        return 'в этот день занятий нет, нажмите далее или назад'
    return message
'''Функция для регистрации на еду донтсу требуется доработка'''
def edu_reg(surname,name,patronymic,credit_book,email):
    data = {}
    session = requests.Session()
    session.post('https://edu.donstu.ru/Account/Register.aspx',data=data)
    
@dp.message(Command('start'))
async def start(message:types.Message):
    '''Создаем таблицу в бд и добовляем в нее сразу Имя и айди телеграмм'''
    db = connect('first.db')
    curs = db.cursor()
    curs.execute('CREATE TABLE IF NOT EXISTS user1 (tg_id TEXT,name TEXT,Surname TEXT,patronymic TEXT,email TEXT,book TEXT,password TEXT)')
    db.commit()
    curs.execute(f'INSERT INTO user1 (tg_id,name) VALUES ({message.from_user.id},"{message.from_user.first_name}")')
    db.commit()
    
    curs.close()
    db.close()
    builder = InlineKeyboardBuilder()
    btn = types.InlineKeyboardButton(text='Перейти на сайт дгту',callback_data='site')
    builder.row(btn)
    builder.row(types.InlineKeyboardButton(text='подробнее',callback_data='info'))
    await message.answer('Привет первокурсник я - твой помощник!\n Перейди на сайт ДГТУ или нажми подробнее, чтобы узнать мои возможности.',reply_markup=builder.as_markup())
@dp.message(F.text==r'\d{7}(\w+)')
async def mess(message:types.Message):
    text = message.text.split()
    print(1)
    db = connect('first.db')
    curs = db.cursor()
    curs.execute(f'UPDATE user1 SET book = "{text[0]}" WHERE tg_id={message.from_user.id}')
    db.commit()
    curs.execute(f'UPDATE user1 SET password = "{text[1]}" WHERE tg_id={message.from_user.id}')
    curs.close()
    db.close()
'''Обработка регистрации на edu dontsu(требуется доработка)'''
@dp.message(F.text=='gjg')
async def reg(message:types.Message):
    global data
    global group
    flag = False
    text = message.text.split()
    data = [text[-1][0:2],text[-1][3:]]
    group = text[0]
    ent = message.entities
    '''Проверяем, если в сообщении есть email - то добавляем в бд зачетку ,почту,фамилию,отчество. Смотри последний callback_query '''
    if ent != None:
        for item in ent:
            if item.type == 'email':
                flag = True
                await message.answer('Вы успешно зарегистрировались!')
    '''добавляем в бд полученные данные'''
    if flag == True:
        db = connect('first.db')
        curs = db.cursor()
        curs.execute(f'UPDATE user1 SET book = "{text[4].capitalize()}" WHERE tg_id={message.from_user.id}')
        db.commit()
        curs.execute(f'UPDATE user1 SET email = "{text[3]}" WHERE tg_id={message.from_user.id}')
        db.commit()
        curs.execute(f'UPDATE user1 SET patronymic = "{text[2].capitalize()}" WHERE tg_id={message.from_user.id}')
        db.commit()
        curs.execute(f'UPDATE user1 SET Surname = "{text[0].capitalize()}" WHERE tg_id={message.from_user.id}')
        

        db.commit()
        curs.close()
        db.close()

    else:
        '''иначе обрабатываем расписание'''
        build = InlineKeyboardBuilder()
        build.row(types.InlineKeyboardButton(text='назад',callback_data='nazad'),types.InlineKeyboardButton(text='далее',callback_data='next'))
        build.row(types.InlineKeyboardButton(text='меню',callback_data='menu'))
        await message.answer(response_rasp(text[0],text[1]),reply_markup=build.as_markup())

'''Обрабатываем кнопку перейти на сайт'''
@dp.callback_query(F.data == 'site')
async def callback(call):
    markup = InlineKeyboardBuilder()
    markup.row(types.InlineKeyboardButton(text='Официальный сайт',url='https://donstu.ru/'))
    markup.row(types.InlineKeyboardButton(text='edu.dontsu',url='https://edu.donstu.ru'),types.InlineKeyboardButton(text='Мой дгту',url='https://my.e.donstu.ru/admin/user/auth/Main'))
    markup.row(types.InlineKeyboardButton(text='назад',callback_data='menu'))
    await call.message.edit_text(text='Выбирите нужный сайт:',reply_markup=markup.as_markup())
async def main():
    await dp.start_polling(bot1)
'''Обрабатываем кнопку назад'''
@dp.callback_query(F.data == 'menu')
async def menu(call):
    builder = InlineKeyboardBuilder()
    btn = types.InlineKeyboardButton(text='Перейти на сайт дгту',callback_data='site')
    builder.add(btn)
    builder.row(types.InlineKeyboardButton(text='подробнее',callback_data='info'))
    await call.message.edit_text('Привет первокурсник я - твой помощник!\n Перейди на сайт ДГТУ или нажми подробнее, чтобы узнать мои возможности.',reply_markup=builder.as_markup())
'''Обрабатываем кнопку подробнее'''
@dp.callback_query(F.data == 'info')
async def info(call):
    build = InlineKeyboardBuilder()
    build.row(types.InlineKeyboardButton(text='Расписание',callback_data='rasp'))
    build.row(types.InlineKeyboardButton(text='Установить напоминание',callback_data='pam'))
    build.row(types.InlineKeyboardButton(text='Задать интересующий вопрос',callback_data='vopros'))
    build.row(types.InlineKeyboardButton(text='авторизоваться на сайте',callback_data='reg'))
    build.row(types.InlineKeyboardButton(text='Запомнить данные',callback_data='zap'))
    build.row(types.InlineKeyboardButton(text='Напомнить данные',callback_data='nap'))

    await call.message.answer('Я могу все что тебе нужно\n-напомнить домашнее задание\n-сообщить расписание\n-ответить на любой вопрос по учебе\n Еще ты можешь сохранить номер своей зачетки и пароль от edu dontsu.\nЯ напомню их тебе - просто нажми на кнопку',reply_markup=build.as_markup())
'''Кнопка расписание.Требуется доработка'''
@dp.callback_query(F.data == 'rasp')
async def rasp(call):
    await call.message.answer("Введи номер совоей группы и дату. Сначала месяц потом день - **.**")
'''Кнопка установить памятку.Требуется доработка'''
@dp.callback_query(F.data == 'pam')
async def func(call):
    pass
'''Кнопка задать вопрос.Требуется доработка'''
@dp.callback_query(F.data == 'vopros')
async def vopros(call):
    await call.message.answer('Чтобы задать вопрос,напиши сообщение:\n -расскажи про\n -что такое\n зачем\для чего\n-как\nи далее пиши что тебя интересует')   
'''Обработка кнопки авторизация. Про мой дгту не понял, там вообще нет кнопки регистрация'''
@dp.callback_query(F.data == 'reg')
async def pam(call):
    markup = InlineKeyboardBuilder()
    markup.row(types.InlineKeyboardButton(text='edu.dontsu',callback_data='edu'),types.InlineKeyboardButton(text='Мой дгту',callback_data='Mydgtu'))
    await call.message.answer('Я могу помочь тебе авторизоваться на любой из сайтов ДГТУ!\n Сначала выбери сайт на котром хочешь авторизоваться:',reply_markup=markup.as_markup())
'''Кнопка "еду" при авторизации'''
@dp.callback_query(F.data=='edu')
async def edu(call):
    await call.message.answer('Введи через пробел:\n-Фамилия\n-Имя\n-Отчество\n-Почта\n-Номер зачетной книжки ')
'''кнопка "назад" для расписания'''
@dp.callback_query(F.data=='nazad')
async def nazad_day(call):
    global data
    build = InlineKeyboardBuilder()
    build.row(types.InlineKeyboardButton(text='назад',callback_data='nazad'),types.InlineKeyboardButton(text='далее',callback_data='next'))
    data[-1] = str(int(data[-1])- 1)
    build.row(types.InlineKeyboardButton(text='меню',callback_data='menu'))
    await call.message.edit_text(response_rasp(group,'.'.join(data)),reply_markup=build.as_markup())
'''кнопка "далее" для расписания'''
@dp.callback_query(F.data=='next')
async def next_day(call):
    global data
    build = InlineKeyboardBuilder()
    build.row(types.InlineKeyboardButton(text='назад',callback_data='nazad'),types.InlineKeyboardButton(text='далее',callback_data='next'))
    data[-1] = str(int(data[-1])+ 1)
    build.row(types.InlineKeyboardButton(text='меню',callback_data='menu'))
    await call.message.edit_text(response_rasp(group,'.'.join(data)),reply_markup=build.as_markup())
@dp.callback_query(F.data=='zap')
async def zap(call):
    await call.message.answer('Введи номер зачетки и пароль через пробел')
@dp.callback_query(F.data=='nap')
async def nap(call):
    print(call.from_user.id)
    db = connect('first.db')
    curs = db.cursor()
    for i in curs.execute('SELECT * FROM user1'):
        print(i)
        if int(i[0]) == int(call.from_user.id):
            await call.message.answer(f'Зачетка - {i[-2]}\n пароль от еду донтсу - {i[-1]}')
            break
if __name__ == "__main__":
    asyncio.run(main())