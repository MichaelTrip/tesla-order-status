#!/usr/bin/env python3
"""
Telegram Chat ID Helper
This script helps you find your correct chat ID by showing all chats your bot can see.
"""

import asyncio
import json
from telegram import Bot
from telegram.error import TelegramError

async def get_chat_info():
    """Get information about available chats"""
    try:
        with open('telegram_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ telegram_config.json not found")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON in telegram_config.json")
        return

    bot_token = config.get('bot_token')
    if not bot_token:
        print("❌ No bot_token found in config")
        return

    try:
        bot = Bot(token=bot_token)
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"🤖 Bot info:")
        print(f"   Name: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   ID: {bot_info.id}")
        
        # Try to get updates to see recent messages
        print(f"\n📨 Recent updates (last 10):")
        updates = await bot.get_updates(limit=10)
        
        if not updates:
            print("❌ No recent messages found!")
            print("\n💡 To fix this:")
            print(f"   1. Open Telegram and search for: @{bot_info.username}")
            print("   2. Start a conversation by sending: /start")
            print("   3. Send any message like: Hello!")
            print("   4. Run this script again")
            return
        
        print(f"   Found {len(updates)} recent messages:")
        
        chat_ids_found = set()
        for update in updates:
            if update.message:
                chat = update.message.chat
                chat_ids_found.add(str(chat.id))
                print(f"   📍 Chat ID: {chat.id}")
                print(f"      Type: {chat.type}")
                if chat.first_name:
                    print(f"      Name: {chat.first_name}")
                if chat.username:
                    print(f"      Username: @{chat.username}")
                print(f"      Message: {update.message.text[:50]}...")
                print()
        
        if chat_ids_found:
            print("✅ Found chat IDs. You can use any of these in your telegram_config.json:")
            for chat_id in sorted(chat_ids_found):
                print(f"   {chat_id}")
                
            # Test sending a message to each found chat
            print(f"\n🧪 Testing message sending to found chats:")
            for chat_id in sorted(chat_ids_found):
                try:
                    await bot.send_message(
                        chat_id=int(chat_id), 
                        text="✅ <b>Success!</b> This chat ID works correctly.",
                        parse_mode='HTML'
                    )
                    print(f"   ✅ Chat ID {chat_id}: Message sent successfully!")
                except Exception as e:
                    print(f"   ❌ Chat ID {chat_id}: Error - {e}")
        
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")
        if "Unauthorized" in str(e):
            print("💡 This usually means your bot token is invalid.")
            print("   Please check your token from @BotFather")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🔍 Getting Telegram chat information...\n")
    asyncio.run(get_chat_info())
