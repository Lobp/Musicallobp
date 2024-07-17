import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import youtube_dlp as youtube_dl

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я ваш музыкальный бот. Используйте команду /convert <ссылка> для конвертации музыки.')

def download_youtube_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '/tmp/%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return filename

def convert_music(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Пожалуйста, предоставьте ссылку на видео.')
        return

    url = context.args[0]
    update.message.reply_text('Скачиваю и конвертирую музыку...')
    try:
        filename = download_youtube_audio(url)
        update.message.reply_text(f'Музыка готова! Файл: {filename}')
        with open(filename, 'rb') as audio_file:
            update.message.reply_audio(audio=audio_file)
    except Exception as e:
        update.message.reply_text(f'Произошла ошибка: {e}')

def main() -> None:
    updater = Updater(os.getenv("TELEGRAM_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("convert", convert_music))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
