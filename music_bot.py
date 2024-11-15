import telebot
import yt_dlp as youtube_dl
import os
import time


BOT_TOKEN = '7817382079:AAEbs1E5DmLfcGrc8Le5d_mOz5LegRDuffo'

bot = telebot.TeleBot(BOT_TOKEN,timeout=60)

downloads_dir = 'downloads'
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
    'ffmpeg_location': r".\ffmpeg-2024-10-10-git-0f5592cfc7-full_build\bin\ffmpeg.exe",
    'noplaylist':True
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me the YouTube video name or link, and I'll send you the audio.")

def download_audio(query):
    if not query.startswith("http"):
        query = f"ytsearch:{query}"

    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        ydl.extract_info(query, download=True)
        time.sleep(1)
        downloaded_files = os.listdir(downloads_dir)
        latest_file = max(
            [os.path.join(downloads_dir, f) for f in downloaded_files],
            key=os.path.getctime
        )
        print(latest_file)
        return latest_file

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        query = message.text
        bot.reply_to(message, "Downloading the audio... Please wait.")
        
        audio_file = download_audio(query)

        if not os.path.isfile(audio_file):
            raise FileNotFoundError(f"The file {audio_file} does not exist.")

        with open(audio_file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)
        os.remove(audio_file)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

bot.polling()