"""
Run this once locally to generate STRING_SESSION for your assistant
(userbot) account. This is the account that actually joins voice chats.

Usage:
    python3 string_session_generator.py

You will be asked to log in with the phone number of the account you
want to use as the assistant. Do NOT use your bot token here — this
must be a normal Telegram user account.
"""

from pyrogram import Client

API_ID = int(input("Enter your API_ID: "))
API_HASH = input("Enter your API_HASH: ")

with Client(name="assistant_session", api_id=API_ID, api_hash=API_HASH, in_memory=True) as app:
    print("\nYour STRING_SESSION is:\n")
    print(app.export_session_string())
    print("\nCopy this value into your STRING_SESSION environment variable.")
