#!/usr/bin/env python3
"""
Test script for Telegram functionality
Run this to test if your Telegram bot configuration works
"""

import asyncio
import json
from telegram import Bot
from telegram.error import TelegramError

def load_telegram_config():
    """Load Telegram configuration from file"""
    try:
        with open('telegram_config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ telegram_config.json not found. Please create it first.")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in telegram_config.json")
        return None

async def test_telegram():
    """Test sending a message to Telegram"""
    config = load_telegram_config()
    if not config:
        return False
    
    bot_token = config.get('bot_token')
    chat_id = config.get('chat_id')
    
    if not bot_token or not chat_id:
        print("❌ Missing bot_token or chat_id in configuration")
        return False
    
    try:
        bot = Bot(token=bot_token)
        message = "🧪 <b>Tesla Order Status Script Test</b>\n\nThis is a test message to verify your Telegram notifications are working correctly! ✅"
        
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        print("✅ Test message sent successfully!")
        return True
        
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Telegram configuration...")
    success = asyncio.run(test_telegram())
    if success:
        print("🎉 Your Telegram notifications are configured correctly!")
    else:
        print("😞 Please check your configuration and try again.")
