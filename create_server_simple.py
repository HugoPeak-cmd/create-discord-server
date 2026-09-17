import os
import discord
from discord import utils

# Скрипт создаёт структуру сервера "Лунные Вестники" по согласованному шаблону.
# Перед запуском: установи DISCORD_TOKEN и TARGET_GUILD_ID в environment (Railway Variables).

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

# Роли: (имя без эмодзи, эмодзи)
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

# Отдельные корневые текстовые каналы (в верхней части сервера)
ROOT_TEXT_CHANNELS = [
    ("✅ welcome", "text"),
    ("📍 навигация", "text"),
    ("🎭 роли", "text"),
]

# Раздел "Важные штуки"
IMPORTANT_CHANNELS = [
    ("📣 объявления", "text"),
    ("🎉 розыгрыши", "text"),
    ("📺 youtube", "text"),
    ("❗ проблемы", "text"),
]

# Категории и их каналы (категория_база, эмодзи, список( (name, type) ))
CATEGORIES = [
    ("Общение", "💬", [
        ("общий-флуд", "text"),
        ("black-market", "text"),
        ("чёрная-книжка", "text"),
        ("вступление-в-легион", "text"),
    ]),

    ("AION 2", "❤️", [
        ("новости-aion-2", "text"),
        ("гайды", "text"),
        ("ошибка-решение", "text"),
        ("легионы", "text"),
        ("общий-голосовой", "voice"),
        ("пати-1", "voice"),
        ("пати-2", "voice"),
        ("🔴 стрим", "voice"),
    ]),

    ("Aion Classic", "💠", [
        ("новости-classic-ru", "text"),
        ("гайды-classic", "text"),
        ("будущее-обновление", "text"),
        ("общий-голосовой", "voice"),
        ("пати-1", "voice"),
        ("пати-2", "voice"),
        ("🔴 стрим", "voice"),
    ]),

    ("Музыка", "🎵", [
        ("музыкальный-чат", "text"),
        ("музыкальная-комната", "voice"),
    ]),

    ("КАНАЛЫ СИЛЬНЫХ", "🔧", [
        ("панель-управления", "text"),
        ("админ-голос", "voice"),
    ]),
]

# Дополнительные корневые
EXTRA_ROOT = [("rules", "text"), ("info", "text"), ("бот-команды", "text")]


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

    # Роли
    for base, emoji in ROLES:
        await ensure_role(guild, base, emoji)

    # Верхние корневые каналы
    for ch_name, _ in ROOT_TEXT_CHANNELS:
        await ensure_text_channel(guild, ch_name)

    # Важные
    for ch_name, _ in IMPORTANT_CHANNELS:
        await ensure_text_channel(guild, ch_name)

    # Дополнительные корневые
    for ch_name, _ in EXTRA_ROOT:
        await ensure_text_channel(guild, ch_name)

    # Категории и их каналы
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
