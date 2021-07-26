from yandex_music import Client
import telebot
import os
import mutagen
import config

bot = telebot.TeleBot(config.bot_token)

client = Client.from_credentials(config.yandex_login, config.yandex_password)


@ bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.from_user.id,
                     'Здравствуй! Я Бот Юджин, могу отправить музыку. Напиши /help чтобы узнать подробнее.')


@ bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id,
                     'напиши название песни,и я отправлю тебе её')


@ bot.message_handler(content_types=['text'])
def get_text_messages(message):
    found = client.search(message.text, nocorrect=False, type_='track')
    if hasattr(found.tracks, 'results'):
        track = found.tracks.results[0]
        track.download('track.mp3')
        try:
            meta = mutagen.easyid3.EasyID3('track.mp3')
        except Exception:
            meta = mutagen.File('track.mp3', easy=True)
            meta.add_tags()

        meta['title'] = track.title
        # meta['year'] = track.meta_data.year
        if track.artists[0].error:
            meta['artist'] = 'Неизвестный исполнитель'
        else:
            meta['artist'] = track.artists[0].name

        if track.albums[0].error:
            meta['album'] = 'Неизвестный альбом'
        else:
            meta['album'] = track.albums[0].title
        meta.save()

        bot.send_audio(message.from_user.id,
                       open('track.mp3', 'rb'), caption=config.bot_caption)

        if os.path.isfile('track.mp3'):
            os.remove('track.mp3')
    else:
        bot.send_message(message.from_user.id,
                         'Ничего нет 😞')


bot.polling(none_stop=True, interval=0)
