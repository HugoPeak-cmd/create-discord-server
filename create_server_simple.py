# create_server_simple.py
# Простая версия: создаёт базовые роли и каналы с эмодзи и отправляет приветствие.
# Установка: pip install -q discord.py python-dotenv
# Запуск: python create_server_simple.py

import os
import asyncio
from dotenv import load_dotenv
import discord

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("TARGET_GUILD_ID")  # опционально

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

BASIC_ROLES = [
    "🛡️ Владелец",
    "⚔️ Офицер",
    "🎥 Стример",
    "🪓 Рейдер",
    "🧭 Рекрут",
    "🤖 Бот",
]

CATEGORIES = {
    "📢 Информация": ["📜-правила", "📰-анонсы", "👋-приветствие"],
    "🎮 Игровые": ["💬-общение", "🛡️-рейды", "🔎-поиск-пати", "📚-гайдсы"],
    "🎙️ Трансляции": ["🎥-стримы", "🔔-уведомления-стрима"],
    "🔊 Голосовые": ["🔊 Общий", "⚔️ Рейд"],
}

# Небольшая пауза между запросами, чтобы не попасть в rate limit
SLEEP = 0.6

async def ensure_roles(guild):
    existing = {r.name for r in guild.roles}
    created = []
    for name in BASIC_ROLES:
        if name not in existing:
            role = await guild.create_role(name=name, reason="Создание базовой роли")
            created.append(role.name)
            await asyncio.sleep(SLEEP)
    return created

async def ensure_channels(guild):
    existing_channels = {c.name for c in guild.channels}
    created = []
    for cat_name, ch_list in CATEGORIES.items():
        # Найти или создать категорию
        category = discord.utils.get(guild.categories, name=cat_name)
        if not category:
            category = await guild.create_category(cat_name, reason="Создание категории")
            await asyncio.sleep(SLEEP)
        for ch_name in ch_list:
            # Текстовые каналы (просто по имени) — если имя содержит пробел, получится текст/голос — здесь создаём текст
            if ch_name in existing_channels:
                continue
            # Решаем: если имя содержит пробел и не содержит '-', создаём голосовой
            if " " in ch_name and "-" not in ch_name:
                # голосовой
                await guild.create_voice_channel(ch_name, category=category, reason="Создание голосового канала")
            else:
                await guild.create_text_channel(ch_name, category=category, reason="Создание текстового канала")
            created.append(ch_name)
            await asyncio.sleep(SLEEP)
    return created

async def send_welcome(guild):
    ch = discord.utils.get(guild.text_channels, name="👋-приветствие")
    if not ch:
        # fallback to first text channel
        text_chs = [c for c in guild.text_channels]
        ch = text_chs[0] if text_chs else None
    if ch:
        try:
            invite = await ch.create_invite(max_uses=0, unique=False, reason="Постоянный инвайт")
            await ch.send(
                "Добро пожаловать! 👋\n"
                "• Прочитайте 📜-правила\n"
                "• Представьтесь здесь\n\n"
                f"Приглашение: {invite.url}\n\n"
                "Удачной игры и стримов! 🎮🎥"
            )
        except Exception:
            # если не можем создать инвайт — просто отправим сообщение
            await ch.send("Добро пожаловать! 👋 Прочитайте 📜-правила и представьтесь.")
        await asyncio.sleep(SLEEP)

@client.event
async def on_ready():
    print(f"Вошёл как {client.user} (id: {client.user.id})")
    guild = None
    if GUILD_ID:
        try:
            guild = client.get_guild(int(GUILD_ID))
        except Exception:
            guild = None
    if not guild:
        if not client.guilds:
            print("Бот не состоит в серверах. Пригласите бота и перезапустите.")
            await client.close()
            return
        print("Сервера, где есть бот:")
        for i, g in enumerate(client.guilds):
            print(f"{i}: {g.name} (ID: {g.id})")
        sel = input("Введите индекс сервера из списка или ID: ").strip()
        try:
            if sel.isdigit() and int(sel) < len(client.guilds):
                guild = client.guilds[int(sel)]
            else:
                guild = client.get_guild(int(sel))
        except Exception:
            print("Неверный ввод.")
            await client.close()
            return

    print("Запускаю создание на сервере:", guild.name)
    r = await ensure_roles(guild)
    print("Созданные роли:", r)
    c = await ensure_channels(guild)
    print("Созданные каналы:", c)
    await send_welcome(guild)
    print("Готово — базовая структура создана.")
    await client.close()

if __name__ == "__main__":
    if not TOKEN:
        print("Поместите DISCORD_TOKEN в .env")
    else:
        client.run(TOKEN)
