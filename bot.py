import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import yt_dlp as youtube_dl
from spotdl import Spotdl

# Simple HTTP server to keep Render happy
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')
        
def run_http_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Initialize Spotify client globally
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_client = Spotdl(client_id=spotify_client_id, client_secret=spotify_client_secret)

# Telegram bot functionality
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я ваш музыкальный бот. Отправьте ссылку на музыку или плейлист, и я конвертирую её в MP3.')

def download_audio(url):
    if "spotify.com" in url:
        song = spotify_client.download([url])
        return song[0] if song else None
    else:
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

def handle_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    url_regex = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    urls = url_regex.findall(message_text)

    if urls:
        url = urls[0]
        update.message.reply_text('Скачиваю и конвертирую музыку...')
        try:
            filename = download_audio(url)
            if filename:
                with open(filename, 'rb') as audio_file:
                    update.message.reply_audio(audio=audio_file)
                os.remove(filename)  # Удалить файл после отправки
            else:
                update.message.reply_text('Не удалось скачать музыку. Пожалуйста, проверьте ссылку.')
        except Exception as e:
            update.message.reply_text(f'Произошла ошибка: {e}')
    else:
        update.message.reply_text('Пожалуйста, предоставьте ссылку на музыку или плейлист.')

def main() -> None:
    updater = Updater(os.getenv("TELEGRAM_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start HTTP server in a separate thread
    threading.Thread(target=run_http_server, daemon=True).start()

    # Start the Telegram bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
