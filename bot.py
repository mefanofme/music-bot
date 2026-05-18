
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp
import os

TOKEN = "8520409146:AAGqLnTKaL_7E_mVIV0euabyTe2izFiJTEk"
PLAYLIST_CHAT_ID = -1003812294822  # твой id канала

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def download_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'track.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True
    }

    # Удаляем старый файл, если есть
    if os.path.exists("track.mp3"):
        os.remove("track.mp3")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        title = info['entries'][0]['title']
        return "track.mp3", title

@dp.message_handler()
async def search_music(message: types.Message):
    file, title = download_audio(message.text)

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💾 Сохранить в плейлист", callback_data="save"))

    await message.answer_audio(open(file, 'rb'), title=title, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "save")
async def save_track(callback: types.CallbackQuery):
    await bot.forward_message(
        PLAYLIST_CHAT_ID,
        callback.message.chat.id,
        callback.message.message_id
    )
    await callback.answer("Сохранено в плейлист 🎵")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)