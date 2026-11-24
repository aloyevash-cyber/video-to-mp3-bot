import os
import asyncio
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "👋 Salom!\n\n"
        "🎵 YouTube video havolasini yuboring.\n"
        "Men uni MP3 formatga o‘tkazib beraman."
    )


@dp.message()
async def download_audio(message: types.Message):
    url = message.text.strip()

    if not url.startswith(("http://", "https://")):
        await message.answer("❌ Iltimos, video havolasini yuboring.")
        return

    msg = await message.answer("⏳ Video yuklanmoqda...")

    try:
        os.makedirs("downloads", exist_ok=True)

        output = "downloads/audio.%(ext)s"

        command = [
            "yt-dlp",
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "192K",
            "-o",
            output,
            url
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await msg.edit_text(
                "❌ Videoni yuklab bo‘lmadi.\n"
                "Havolani tekshirib qayta urinib ko‘ring."
            )
            return

        files = os.listdir("downloads")

        mp3_file = None

        for file in files:
            if file.endswith(".mp3"):
                mp3_file = os.path.join("downloads", file)
                break

        if not mp3_file:
            await msg.edit_text("❌ MP3 fayl yaratilmadi.")
            return

        await msg.edit_text("✅ Tayyor! MP3 fayl yuborilmoqda...")

        audio = FSInputFile(mp3_file)

        await message.answer_audio(
            audio=audio,
            caption="🎵 MP3 tayyor!"
        )

        os.remove(mp3_file)

    except Exception as e:
        print("ERROR:", e)
        await msg.edit_text(
            "❌ Xatolik yuz berdi. Keyinroq qayta urinib ko‘ring."
        )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
