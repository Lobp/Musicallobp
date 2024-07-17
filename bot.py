import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import youtube_dl

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я ваш музыкальный бот.')

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
        ydl.download([url])

def convert_music(update: Update, context: CallbackContext) -> None:
    url = context.args[0]
    update.message.reply_text('Скачиваю и конвертирую музыку...')
    download_youtube_audio(url)
    update.message.reply_text('Музыка готова!')

def main() -> None:
    updater = Updater(os.getenv("7092718962:AAEW969TSqCGUXlSn3bGNKSaFw37tfir7R8"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("convert", convert_music))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
