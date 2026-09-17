import os
import discord
from discord import utils

# Скрипт создаёт структуру каналов и ролей примерно по образцу, который ты прислал.
# Использование:
# - Вставь DISCORD_TOKEN и TARGET_GUILD_ID в environment (Railway Variables)
# - Запусти. Скрипт создаст роли, корневые каналы, категории и каналы внутри категорий, затем завершится.

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

# Роли: (имя, эмодзи)
ROLES = [
    ("Глава Гильдии", "👑"),
    ("Заместитель", "⚜️"),
    ("Офицер", "🛡️"),
    ("Новичек", "🌱"),
    ("Девочка", "👧"),
    ("Стример", "🎥"),
    ("Модер", "🔨"),
    ("Aion Classic", "💠"),
    ("Throne and Liberty", "🔥"),
]

# Корневые (топ) каналы, текстовые
ROOT_TEXT_CHANNELS = [
    ("🎉 welcome", "text"),
    ("🧭 навигация", "text"),
    ("🎭 роли", "text"),
    ("📣 объявления", "text"),
    ("🎁 розыгрыши", "text"),
    ("📺 youtube", "text"),
    ("❗ проблемы", "text"),
]

# Категории и их каналы
# Формат: (категория_база, эмодзи, [ (channel_name, type) ... ])
CATEGORIES = [
    ("Aion Classic", "💠", [
        ("новости-aion-classic", "text"),
        ("гайды", "text"),
        ("общий", "text"),
        ("сбор-в-данж", "text"),
        ("сбор-кп", "text"),
        ("Общий голосовой", "voice"),
        ("Пати 1", "voice"),
        ("Пати 2", "voice"),
        ("Пати 3", "voice"),
        ("🔴 стрим", "voice"),
    ]),
    ("Throne and Liberty", "🔥", [
        ("новости-throne", "text"),
        ("гайды-tl", "text"),
        ("общий-tl", "text"),
        ("сбор-в-данж-tl", "text"),
        ("Общий голосовой", "voice"),
        ("Пати 1", "voice"),
        ("Пати 2", "voice"),
        ("🔴 стрим", "voice"),
    ]),
    ("Музыка", "🎵", [
        ("музыкальный-чат", "text"),
        ("музыкальная-комната", "voice"),
    ]),
    ("КАНАЛЫ СИЛЬНЫХ", "💙", [
        ("панель-управления", "text"),
        ("админ-голос", "voice"),
    ]),
]

# Дополнительные корневые каналы, которые можно создать
EXTRA_ROOT = ["rules", "info", "бот-команды"]


def desired_name(base, emoji):
    return f"{emoji} {base}"

async def ensure_role(guild, base, emoji):
    name = desired_name(base, emoji)
    existing = next((r for r in guild.roles if base in r.name), None)
    if existing:
        if existing.name != name:
            try:
                await existing.edit(name=name)
                print(f"Renamed role '{existing.name}' -> '{name}'")
            except Exception as e:
                print(f"Failed to rename role {existing.name}: {e}")
        else:
            print(f"Role already exists: {name}")
    else:
        try:
            await guild.create_role(name=name)
            print(f"Created role: {name}")
        except Exception as e:
            print(f"Failed to create role {name}: {e}")

async def ensure_text_channel(guild, name):
    existing = discord.utils.get(guild.text_channels, name=name)
    if existing:
        print(f"Text channel exists: {name}")
    else:
        try:
            await guild.create_text_channel(name)
            print(f"Created text channel: {name}")
        except Exception as e:
            print(f"Failed to create text channel {name}: {e}")

async def ensure_category_and_channels(guild, base, emoji, channels):
    cat_name = desired_name(base, emoji)
    category = next((c for c in guild.categories if base in c.name), None)
    if category:
        if category.name != cat_name:
            try:
                await category.edit(name=cat_name)
                print(f"Renamed category '{category.name}' -> '{cat_name}'")
            except Exception as e:
                print(f"Failed to rename category {category.name}: {e}")
        else:
            print(f"Category already exists: {cat_name}")
    else:
        try:
            category = await guild.create_category(cat_name)
            print(f"Created category: {cat_name}")
        except Exception as e:
            print(f"Failed to create category {cat_name}: {e}")
            category = None

    if not category:
        return

    for ch_name, ch_type in channels:
        # Добавляем префиксы emoji не нужно — делаем имена "чистыми" (как в шаблоне)
        final_name = ch_name
        if ch_type == "text":
            existing_ch = discord.utils.get(category.text_channels, name=final_name)
            if existing_ch:
                print(f"Text channel exists in '{cat_name}': {final_name}")
            else:
                try:
                    await category.create_text_channel(final_name)
                    print(f"Created text channel '{final_name}' in category '{cat_name}'")
                except Exception as e:
                    print(f"Failed to create text channel '{final_name}' in '{cat_name}': {e}")
        elif ch_type == "voice":
            existing_vch = discord.utils.get(category.voice_channels, name=final_name)
            if existing_vch:
                print(f"Voice channel exists in '{cat_name}': {final_name}")
            else:
                try:
                    await category.create_voice_channel(final_name)
                    print(f"Created voice channel '{final_name}' in category '{cat_name}'")
                except Exception as e:
                    print(f"Failed to create voice channel '{final_name}' in '{cat_name}': {e}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")
    guild_id = os.environ.get("TARGET_GUILD_ID")
    if not guild_id:
        print("ERROR: TARGET_GUILD_ID not set. Set it in environment variables.")
        await client.close()
        return

    try:
        guild = client.get_guild(int(guild_id))
    except Exception as e:
        print(f"ERROR: Invalid TARGET_GUILD_ID: {e}")
        await client.close()
        return

    if guild is None:
        print(f"ERROR: Bot is not in the guild with ID {guild_id} or cannot access it.")
        await client.close()
        return

    # Создаём/обновляем роли
    for base, emoji in ROLES:
        await ensure_role(guild, base, emoji)

    # Создаём корневые текстовые каналы
    for ch_name, _ in ROOT_TEXT_CHANNELS:
        await ensure_text_channel(guild, ch_name)

    # Создаём дополнительные корневые
    for ch in EXTRA_ROOT:
        await ensure_text_channel(guild, ch)

    # Создаём категории и их каналы
    for base, emoji, channels in CATEGORIES:
        await ensure_category_and_channels(guild, base, emoji, channels)

    print("All done — closing bot.")
    await client.close()

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("ERROR: DISCORD_TOKEN not set.")
    else:
        client.run(token)
