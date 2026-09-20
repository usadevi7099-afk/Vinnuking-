import time
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from config import OWNER_ID
from database.db import (
    get_all_chats,
    get_all_users,
    gban_user,
    ungban_user,
    is_gbanned,
    get_gban_list,
    get_maintenance,
    set_maintenance,
    set_start_img,
)

BOT_START_TIME = time.time()


def owner_only(func):
    async def wrapper(client: Client, message: Message):
        if message.from_user is None or message.from_user.id != OWNER_ID:
            await message.reply_text("🚫 This command can only be used by the bot owner.")
            return
        await func(client, message)

    return wrapper


# ---------------- Global gate: maintenance mode + global ban ----------------
# Runs before every other handler (group=-1) and stops propagation for
# gbanned users, and for everyone except the owner during maintenance.
@Client.on_message(filters.all, group=-1)
async def global_gate(client: Client, message: Message):
    if not message.from_user:
        return

    if await is_gbanned(message.from_user.id):
        message.stop_propagation()
        return

    if message.from_user.id == OWNER_ID:
        return  # owner is never blocked

    if await get_maintenance():
        if message.text and message.text.startswith("/"):
            await message.reply_text(
                "🛠 Bot is currently under maintenance. Please try again later."
            )
        message.stop_propagation()


# ---------------- /broadcast ----------------
@Client.on_message(filters.command("broadcast"))
@owner_only
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text(
            "❓ Reply to the message you want to broadcast with /broadcast.\n\n"
            "Add `groups` or `users` after the command to target only one "
            "audience, e.g. `/broadcast groups`. Default is both."
        )
        return

    target = message.command[1].lower() if len(message.command) > 1 else "all"
    targets = []
    if target in ("all", "groups"):
        targets += await get_all_chats()
    if target in ("all", "users"):
        targets += await get_all_users()

    status = await message.reply_text(f"📢 Broadcasting to {len(targets)} chats...")

    sent, failed = 0, 0
    for chat_id in targets:
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(chat_id)
                sent += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1

    await status.edit_text(f"✅ Broadcast complete.\nSent: {sent}\nFailed: {failed}")


# ---------------- /stats ----------------
@Client.on_message(filters.command("stats"))
@owner_only
async def stats_cmd(client: Client, message: Message):
    total_chats = len(await get_all_chats())
    total_users = len(await get_all_users())
    uptime_seconds = int(time.time() - BOT_START_TIME)
    h, rem = divmod(uptime_seconds, 3600)
    m, s = divmod(rem, 60)

    text = (
        "📊 **Bot Stats**\n\n"
        f"👥 Groups served: {total_chats}\n"
        f"🙋 Users served: {total_users}\n"
        f"⏱ Uptime: {h}h {m}m {s}s\n"
    )
    await message.reply_text(text)


# ---------------- /gban, /ungban, /gbanlist ----------------
@Client.on_message(filters.command("gban"))
@owner_only
async def gban_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("❓ Reply to a user's message with /gban [reason].")
        return

    user = message.reply_to_message.from_user
    if user.id == OWNER_ID:
        await message.reply_text("❌ You can't gban the bot owner.")
        return

    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason given"
    await gban_user(user.id, reason)
    await message.reply_text(f"🚫 {user.mention} has been globally banned.\nReason: {reason}")


@Client.on_message(filters.command("ungban"))
@owner_only
async def ungban_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("❓ Reply to a user's message with /ungban.")
        return

    user = message.reply_to_message.from_user
    await ungban_user(user.id)
    await message.reply_text(f"✅ {user.mention} has been unbanned globally.")


@Client.on_message(filters.command("gbanlist"))
@owner_only
async def gbanlist_cmd(client: Client, message: Message):
    banned = await get_gban_list()
    if not banned:
        await message.reply_text("📭 No globally banned users.")
        return
    lines = [f"• `{b['user_id']}` — {b.get('reason', 'No reason')}" for b in banned]
    await message.reply_text("🚫 **Globally Banned Users:**\n\n" + "\n".join(lines))


# ---------------- /maintenance ----------------
@Client.on_message(filters.command("maintenance"))
@owner_only
async def maintenance_cmd(client: Client, message: Message):
    new_val = not await get_maintenance()
    await set_maintenance(new_val)
    status = "🛠 ON — only the owner can use the bot now." if new_val else "✅ OFF — bot is available to everyone."
    await message.reply_text(f"Maintenance mode: {status}")


# ---------------- /setimg ----------------
@Client.on_message(filters.command("setimg"))
@owner_only
async def setimg_cmd(client: Client, message: Message):
    """
    Change the /start and /help banner image without redeploying.
    Reply to a photo with /setimg, or send /setimg <image_url>.
    """
    if message.reply_to_message and message.reply_to_message.photo:
        file_id = message.reply_to_message.photo.file_id
        await set_start_img(file_id)
        await message.reply_text("✅ Start image updated (from replied photo).")
        return

    if len(message.command) > 1:
        url = message.command[1]
        await set_start_img(url)
        await message.reply_text("✅ Start image updated (from URL).")
        return

    await message.reply_text(
        "❓ Reply to a photo with /setimg, or send /setimg <image_url>."
    )


# ---------------- /logs ----------------
@Client.on_message(filters.command("logs"))
@owner_only
async def logs_cmd(client: Client, message: Message):
    import os
    if os.path.exists("bot.log"):
        await message.reply_document("bot.log", caption="📄 Latest bot logs.")
    else:
        await message.reply_text("📭 No log file found yet.")
