import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp

TOKEN = os.getenv("8850478810:AAGS3bVqxMfC_oSO2mfVX38onOftZn6UKSo")  # Читаем из переменных окружения
PLAYLIST_CHAT_ID = int(os.getenv("-1003812294822", "-1003812294822"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def download_audio(query):
    # Уникальное имя для каждого запроса
    unique_id = str(uuid.uuid4())[:8]
    out_template = f"track_{unique_id}.%(ext)s"
    final_mp3 = f"track_{unique_id}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': out_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'source_address': '0.0.0.0',  # Для Railway
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        title = info['entries'][0]['title']
        
    return final_mp3, title

@dp.message_handler()
async def search_music(message: types.Message):
    await message.answer("🔍 Ищу...")
    
    try:
        file, title = download_audio(message.text)
        
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💾 Сохранить в плейлист", callback_data="save"))
        
        with open(file, 'rb') as audio:
            await message.answer_audio(audio, title=title, reply_markup=kb)
        
        os.remove(file)  # Удаляем после отправки
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

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
