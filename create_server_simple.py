import os
import discord
from discord import utils

# Интенты
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
    ("Aion Classic", "🛡️"),
    ("Throne and Liberty", "👑"),
]

# Категории и каналы внутри них
CATEGORIES = [
    ("Aion Classic", "🛡️"),
    ("Throne and Liberty", "👑"),
]

# Для каждой категории создаются эти каналы (имя, тип)
CHANNELS_IN_CATEGORY = [
    ("общий", "text"),
    ("🔴 стрим", "voice"),  # сюда будешь стримить
]

# Дополнительные корневые каналы (по желанию)
ROOT_TEXT_CHANNELS = ["welcome", "rules", "announcements"]


def desired_name(base, emoji):
    return f"{emoji} {base}"

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

    # Создаём / обновляем роли
    for base, emoji in ROLES:
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

    # Создаём корневые текстовые каналы (если не существует)
    for ch_name in ROOT_TEXT_CHANNELS:
        existing = discord.utils.get(guild.text_channels, name=ch_name)
        if existing:
            print(f"Root text channel exists: {ch_name}")
        else:
            try:
                await guild.create_text_channel(ch_name)
                print(f"Created root text channel: {ch_name}")
            except Exception as e:
                print(f"Failed to create root channel {ch_name}: {e}")

    # Создаём / обновляем категории и каналы внутри них
    for base, emoji in CATEGORIES:
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

        # Если категория создана/найдена — создать в ней каналы
        if category:
            for ch_base, ch_type in CHANNELS_IN_CATEGORY:
                ch_name = ch_base
                if ch_type == "text":
                    existing_ch = discord.utils.get(category.text_channels, name=ch_name)
                    if existing_ch:
                        print(f"Text channel exists in '{cat_name}': {ch_name}")
                    else:
                        try:
                            await category.create_text_channel(ch_name)
                            print(f"Created text channel '{ch_name}' in category '{cat_name}'")
                        except Exception as e:
                            print(f"Failed to create text channel '{ch_name}' in '{cat_name}': {e}")
                elif ch_type == "voice":
                    existing_vch = discord.utils.get(category.voice_channels, name=ch_name)
                    if existing_vch:
                        print(f"Voice channel exists in '{cat_name}': {ch_name}")
                    else:
                        try:
                            await category.create_voice_channel(ch_name)
                            print(f"Created voice channel '{ch_name}' in category '{cat_name}'")
                        except Exception as e:
                            print(f"Failed to create voice channel '{ch_name}' in '{cat_name}': {e}")

    print("All done — closing bot.")
    await client.close()

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("ERROR: DISCORD_TOKEN not set.")
    else:
        client.run(token)
