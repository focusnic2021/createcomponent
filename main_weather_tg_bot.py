"""
навеяно - Telegram bot на Python + aiogram | Прогноз погоды в любом городе | API погоды | Парсинг JSON
https://www.youtube.com/watch?v=fa1FUW1jLAE
"""
import requests
import datetime
from config import open_weather_token, tg_bot_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
# print(f'open_weather_token={open_weather_token}, tg_bot_token={tg_bot_token}')


def protocol(event_mesaage):
    """Заносит в файл лога принятое сообщение. Сама определяется с датой - либо новый файл, либо дописывает в существующий
    """
    try:
        # открыть файл-протокол, занести сведения:
        file_name = f"{datetime.datetime.now().strftime('%Y%m%d')}.log"
        f = open(file_name, 'a')
        f.write(event_mesaage)
    finally:
        f.close()
    # ...def protocol(event_mesaage)


@dp.message_handler(commands=['start','help'])
async def start_command(message: types.Message):
    # внести сообщение о событии в протокол:
    event_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')};" \
                f"{message.from_user.id};" \
                f"{message.from_user.first_name} {message.from_user.last_name};" \
                f"command={message.text};\n"
    protocol(event_msg)

    # приветствовать пользователя:
    await message.reply('Погода на данный момент в определенном городе.\nПример запроса:\nУчалы\nkazan\nalanya')
    # ...async def start_command(message: types.Message)


@dp.message_handler()
async def get_weather(message: types.Message):
    response_result=''
    try:
        req = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric&lang=ru"
            )
        data = req.json()
        # print(data)

        if data.get('cod') and data.get('cod') == '404':    # 'message': 'city not found'
            await message.reply(data.get('message'))
            response_result = data.get('message')
            # ...data.get('cod') and data.get('cod') == '404'
        elif data.get('coord'):     # все хорошо, данные получены
            # данные о городе:
            city = data['name']                 # название города (из ответа)
            country = data['sys']['country']    # страна
            lat, lon = data['coord']['lat'], data['coord']['lon']   # координаты города
            # timezone = data['timezone']         # timezone - часовой пояс. Все вермена даны в Гринвиче
            # время в городе - с поправкой на часовой пояс:
            dt = datetime.datetime.fromtimestamp(data['dt']+data['timezone']).strftime('%d.%m.%Y %H:%M')
            # время восхода и заката на сегодня в этом городе - с поправкой на часовой пояс:
            sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise']+data['timezone']).strftime('%H:%M')
            sunset  = datetime.datetime.fromtimestamp(data['sys']['sunset']+data['timezone']).strftime('%H:%M')
            print(f"timezone={data['timezone']}")
            print(f"sunrise={sunrise}, sunset={sunset}")
            length_of_day = datetime.datetime.fromtimestamp(data['sys']['sunset']) - datetime.datetime.fromtimestamp(data['sys']['sunrise'])
            # данные о погоде:
            temp     = data['main']['temp']             # температура
            pressure = data['main']['pressure']         # давление
            humidity = data['main']['humidity']         # влажность
            wind_deg = data['wind']['deg']      # направление ветра
            # wind_kompas =''
            if wind_deg < 31:
                wind_kompas = 'Северный'
            elif wind_deg > 30 and wind_deg < 61:
                wind_kompas = 'Северо-Восточный'
            elif wind_deg > 60 and wind_deg < 121:
                wind_kompas = 'Восточный'
            elif wind_deg > 120 and wind_deg < 151:
                wind_kompas = 'Юго-Восточный'
            elif wind_deg > 150 and wind_deg < 211:
                wind_kompas = 'Южный'
            elif wind_deg > 210 and wind_deg < 241:
                wind_kompas = 'Юго-Западный'
            elif wind_deg > 240 and wind_deg < 301:
                wind_kompas = 'Западный'
            elif wind_deg > 300 and wind_deg < 331:
                wind_kompas = 'Северо-Западный'
            else:
                wind_kompas = 'Северный'
            wind_speed = data['wind']['speed']  # скорость ветра
            await message.reply(f"Погода в <b>{city}</b> - {country} (координаты: {lat},{lon})\n\t"
                f"по состоянию на {dt}\n\t"
                f"Температура: {temp} °С\n\tДавление: {pressure} мм.рт.ст\n\tВлажность: {humidity} %\n\t"
                f"Солнце:\n\tВосход - {sunrise}, Закат - {sunset}, Световой день - {length_of_day}\n\t"
                f"Ветер: {wind_kompas} ({wind_deg}°),  {wind_speed} м/с")

            response_result = f'{city} ({dt})'
            # ...elif data.get('coord')

        # занести в протокол:
        event_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')};" \
                    f"{message.from_user.id};" \
                    f"{message.from_user.first_name} {message.from_user.last_name};" \
                    f"message.text={message.text};" \
                    f"result={response_result}\n"
        protocol(event_msg)

    except Exception as ex:
        # занести в протокол:
        event_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')};" \
                    f"{message.from_user.id};" \
                    f"{message.from_user.first_name} {message.from_user.last_name};" \
                    f"message.text={message.text};" \
                    f"Exception={ex}\n"
        protocol(event_msg)

        await message.reply('Ошибка при обращении к серверу данных:\n', ex)
    # ...async def get_weather(message: types.Message)


@dp.message_handler()
async def send_location(message: types.Message):
    pass
    # ...async def send_location()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)