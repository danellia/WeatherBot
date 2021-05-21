import telebot
import requests
import pytz
from datetime import datetime
from telebot import types

bot = telebot.TeleBot('TOKEN')
markup = telebot.types.InlineKeyboardMarkup()

weather_token = "TOKEN"
part = "current,minutely,alerts"
lang = "ru"
units = "metric"

forecast = ""

@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id, text="Напиши, в каком городе ты живешь:")
  bot.register_next_step_handler(message, choose_city)

def choose_city(message):
  global lon, lat, response_current
  city = message.text
  response_current = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + weather_token + "&lang=" + lang + "&units=" + units).json()
  lon = str(response_current["coord"]["lon"])
  lat = str(response_current["coord"]["lat"])

  markup.add(telebot.types.InlineKeyboardButton(text="Текущая погода",callback_data=1))
  markup.add(telebot.types.InlineKeyboardButton(text="Почасовой прогноз на 2 дня", callback_data=2))
  markup.add(telebot.types.InlineKeyboardButton(text="Прогноз на неделю", callback_data=3))
  bot.send_message(message.chat.id, text="Выбери интересующий тебя прогноз погоды!" ,reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
  if call.data == '1':
    temp = str(response_current["main"]["temp"])
    feels_like = str(response_current["main"]["feels_like"])
    wind_speed = str(response_current["wind"]["speed"])
    description = response_current["weather"][0]["description"]
    forecast = "Сегодня " + description + ", " + temp + " C\nОщущается как " + feels_like + " C\nВетер " + wind_speed + " м/с"
    
  elif call.data == '2':
    response_onecall = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=" + lat + "&lon=" + lon + "&exclude=" + part + "&appid=" + weather_token + "&lang=" + lang + "&units=" + units).json()
    forecast = ""
    for hour in response_onecall["hourly"]:
      dt = datetime.fromtimestamp(hour["dt"], pytz.timezone('UTC'))
      dt_str = str(dt.date()) + " " + str(dt.hour)
      temp = str(hour["temp"])
      wind_speed = str(hour["wind_speed"])
      forecast += dt_str + "ч: " + temp + " C, ветер " + wind_speed + " м/с\n"

  elif call.data == '3':
    response_onecall = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=" + lat + "&lon=" + lon + "&exclude=" + part + "&appid=" + weather_token + "&lang=" + lang + "&units=" + units).json()
    forecast = ""
    for day in response_onecall["daily"]:
      dt = datetime.fromtimestamp(day["dt"], pytz.timezone('UTC'))
      dt_str = str(dt.date())
      temp = str(day["temp"]["day"])
      wind_speed = str(day["wind_speed"])
      description = day["weather"][0]["description"]
      forecast += dt_str + ": " + description + ", " + temp + "C, ветер " + wind_speed + " м/с\n"

  bot.send_message(call.message.chat.id, forecast)

bot.polling(none_stop=True)