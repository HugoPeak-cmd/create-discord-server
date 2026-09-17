import os
import asyncio
import discord
from discord import utils

# create_guild_exact.py
# Создаёт структуру сервера "Лунные Вестники" точно по согласованному шаблону
# и запускает persistent-бот, который поддерживает систему self-roles через реакции.
# Перед запуском установи в окружении:
# DISCORD_TOKEN — токен бота
# TARGET_GUILD_ID — ID сервера (куда создавать)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # нужно для назначения ролей

client = discord.Client(intents=intents)

# Роли (имя, эмодзи) — все роли будут созданы. Список порядка соответствует желаемому.
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

# Какие роли можно выбрать самостоятельно (reaction-role)
SELF_ASSIGN_ROLES = [
    "Новичек",
    "Девочка",
    "Стример",
    "Aion Classic",
    "Throne and Liberty",
]

# Сопоставление эмодзи -> роль (для реакции)
# Используются именно эмодзи (unicode). Если поменяешь эмодзи в ROLES, синхронизируй сюда.
ROLE_EMOJI_MAP = {
    "🌱": "Новичек",
    "👧": "Девочка",
    "🎥": "Стример",
    "💠": "Aion Classic",
    "🔥": "Throne and Liberty",
}

# Верхние каналы (точно как на скриншотах)
TOP_CHANNELS = [
    ("✅ welcome", "text"),
    ("📍 навигация", "text"),
    ("🎭 роли", "text"),
]

IMPORTANT_CHANNELS = [
    ("📣 объявления", "text"),
    ("🎉 розыгрыши", "text"),
    ("📺 youtube", "text"),
    ("❗ проблемы", "text"),
]

# Остальная структура (категория имя, эмодзи, список каналов (name,type) )
CATEGORIES = [
    ("💬 Общение", "💬", [
        ("общий-флуд", "text"),
        ("black-market", "text"),
        ("чёрная-книжка", "text"),
        ("вступление-в-легион", "text"),
    ]),
    ("❤️ AION 2", "❤️", [
        ("новости-aion-2", "text"),
        ("гайды", "text"),
        ("ошибка-решение", "text"),
        ("легионы", "text"),
        ("общий-голосовой", "voice"),
        ("пати-1", "voice"),
        ("пати-2", "voice"),
        ("🔴 стрим", "voice"),
    ]),
    ("💠 Aion Classic", "💠", [
        ("новости-classic-ru", "text"),
        ("гайды", "text"),
        ("будущее-обновление", "text"),
        ("общий-голосовой", "voice"),
        ("пати-1", "voice"),
        ("пати-2", "voice"),
        ("🔴 стрим", "voice"),
    ]),
    ("🎵 Музыка", "🎵", [
        ("музыкальный-чат", "text"),
        ("музыкальная-комната", "voice"),
    ]),
    ("🔧 КАНАЛЫ СИЛЬНЫХ", "🔧", [
        ("панель-управления", "text"),
        ("админ-голос", "voice"),
    ]),
]

EXTRA_ROOT = [("rules", "text"), ("info", "text"), ("бот-команды", "text")]

# Маркер для сообщения с реакциями, чтобы найти и обновить его при перезапуске
REACTION_MESSAGE_MARKER = "Роли — Лунные Вестники"


async def create_or_get_role(guild: discord.Guild, name: str):
    role = utils.get(guild.roles, name=name)
    if role:
        return role
    try:
        role = await guild.create_role(name=name)
        print(f"Created role: {name}")
        return role
    except Exception as e:
        print(f"Failed to create role {name}: {e}")
        return None


async def ensure_text_channel(guild: discord.Guild, name: str):
    ch = utils.get(guild.text_channels, name=name)
    if ch:
        return ch
    try:
        ch = await guild.create_text_channel(name)
        print(f"Created text channel: {name}")
        return ch
    except Exception as e:
        print(f"Failed to create text channel {name}: {e}")
        return None


async def ensure_category_and_channels(guild: discord.Guild, cat_name: str, channels):
    category = next((c for c in guild.categories if c.name == cat_name), None)
    if not category:
        try:
            category = await guild.create_category(cat_name)
            print(f"Created category: {cat_name}")
        except Exception as e:
            print(f"Failed to create category {cat_name}: {e}")
            return None
    else:
        print(f"Category exists: {cat_name}")

    for ch_name, ch_type in channels:
        if ch_type == "text":
            existing = discord.utils.get(category.text_channels, name=ch_name)
            if existing:
                print(f"Text exists in {cat_name}: {ch_name}")
            else:
                try:
                    await category.create_text_channel(ch_name)
                    print(f"Created text channel '{ch_name}' in '{cat_name}'")
                except Exception as e:
                    print(f"Failed to create text channel '{ch_name}' in '{cat_name}': {e}")
        elif ch_type == "voice":
            existing = discord.utils.get(category.voice_channels, name=ch_name)
            if existing:
                print(f"Voice exists in {cat_name}: {ch_name}")
            else:
                try:
                    await category.create_voice_channel(ch_name)
                    print(f"Created voice channel '{ch_name}' in '{cat_name}'")
                except Exception as e:
                    print(f"Failed to create voice channel '{ch_name}' in '{cat_name}': {e}")
    return category


async def prepare_reaction_role_message(guild: discord.Guild):
    # Найти канал ролей
    roles_channel_name = None
    for name, _ in TOP_CHANNELS:
        if "роли" in name.lower():
            roles_channel_name = name
            break
    if not roles_channel_name:
        print("Roles channel name not found in TOP_CHANNELS")
        return

    roles_channel = discord.utils.get(guild.text_channels, name=roles_channel_name)
    if not roles_channel:
        print(f"Roles channel '{roles_channel_name}' not found, creating")
        roles_channel = await guild.create_text_channel(roles_channel_name)

    # Попробуем найти существующее сообщение от бота с маркером
    existing_msg = None
    try:
        async for msg in roles_channel.history(limit=200):
            if msg.author == client.user and REACTION_MESSAGE_MARKER in (msg.content or ""):
                existing_msg = msg
                break
    except Exception as e:
        print(f"Failed to read history of roles channel: {e}")

    # Сформируем текст сообщения
    lines = [f"{REACTION_MESSAGE_MARKER}\nВыберите роли, реагируя на эмодзи.\n"]
    for emoji, role_name in ROLE_EMOJI_MAP.items():
        lines.append(f"{emoji} — {role_name}")
    content = "\n".join(lines)

    if existing_msg:
        try:
            await existing_msg.edit(content=content)
            message = existing_msg
            print("Updated existing reaction-role message")
        except Exception as e:
            print(f"Failed to edit existing reaction-role message: {e}")
            message = None
    else:
        try:
            message = await roles_channel.send(content)
            print("Sent new reaction-role message")
        except Exception as e:
            print(f"Failed to send reaction-role message: {e}")
            message = None

    # Добавим реакции к сообщению
    if message:
        for emoji in ROLE_EMOJI_MAP.keys():
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                print(f"Failed to add reaction {emoji}: {e}")

    return


@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")
    guild_id = os.environ.get("TARGET_GUILD_ID")
    if not guild_id:
        print("ERROR: TARGET_GUILD_ID not set. Set it in environment variables.")
        await client.close()
        return

    guild = client.get_guild(int(guild_id))
    if guild is None:
        print(f"ERROR: Bot is not in the guild with ID {guild_id} or cannot access it.")
        await client.close()
        return

    print(f"Preparing server structure in guild: {guild.name} ({guild.id})")

    # Создаём роли в нужном порядке
    for base, emoji in ROLES:
        name = f"{emoji} {base}"
        await create_or_get_role(guild, name)

    # Верхние каналы
    for ch_name, _ in TOP_CHANNELS:
        await ensure_text_channel(guild, ch_name)

    # Важные
    for ch_name, _ in IMPORTANT_CHANNELS:
        await ensure_text_channel(guild, ch_name)

    # Дополнительные
    for ch_name, _ in EXTRA_ROOT:
        await ensure_text_channel(guild, ch_name)

    # Категории и каналы
    for cat_name, emoji, channels in CATEGORIES:
        # cat_name уже содержит эмодзи/декор
        await ensure_category_and_channels(guild, cat_name, channels)

    # Подготовка сообщения с реакциями для самоназначения ролей
    await prepare_reaction_role_message(guild)

    print("Setup finished. Bot will continue running to handle role reactions.")


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # Игнорируем реакции от бота
    if payload.user_id == client.user.id:
        return

    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    emoji = payload.emoji.name
    if emoji not in ROLE_EMOJI_MAP:
        return

    role_base = ROLE_EMOJI_MAP[emoji]
    # В ролях на сервере имя с эмодзи — формируем точно
    # Найдём роль, где содержится base
    role = next((r for r in guild.roles if role_base in r.name), None)
    if role is None:
        print(f"Role for reaction not found: {role_base}")
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id)
        except Exception as e:
            print(f"Failed to fetch member {payload.user_id}: {e}")
            return

    try:
        await member.add_roles(role)
        print(f"Added role {role.name} to {member.display_name}")
    except Exception as e:
        print(f"Failed to add role: {e}")


@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    emoji = payload.emoji.name
    if emoji not in ROLE_EMOJI_MAP:
        return

    role_base = ROLE_EMOJI_MAP[emoji]
    role = next((r for r in guild.roles if role_base in r.name), None)
    if role is None:
        print(f"Role for reaction not found: {role_base}")
        return

    try:
        member = await guild.fetch_member(payload.user_id)
    except Exception as e:
        print(f"Failed to fetch member on reaction remove: {e}")
        return

    try:
        await member.remove_roles(role)
        print(f"Removed role {role.name} from {member.display_name}")
    except Exception as e:
        print(f"Failed to remove role: {e}")


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("ERROR: DISCORD_TOKEN not set.")
    else:
        client.run(token)
