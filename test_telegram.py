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
    
    # Check if notifications are enabled
    if not config.get('enabled', True):
        print("ℹ️ Telegram notifications are disabled in configuration")
        return True
    
    bot_token = config.get('bot_token')
    chat_id = config.get('chat_id')
    
    if not bot_token or not chat_id:
        print("❌ Missing bot_token or chat_id in configuration")
        return False
    
    try:
        bot = Bot(token=bot_token)
        
        # Test both message types
        print("📱 Testing change notification message...")
        change_message = "🧪 <b>Tesla Order Status Script Test</b>\n\n✅ <b>Change detected test:</b> This simulates a change notification! 🚀"
        await bot.send_message(chat_id=chat_id, text=change_message, parse_mode='HTML')
        print("✅ Change notification test sent!")
        
        # Wait a moment between messages
        await asyncio.sleep(1)
        
        print("📱 Testing no-change notification message...")
        if config.get('always_notify', False):
            # Show what a full order details message would look like
            no_change_message = """🚗 <b>Tesla Order Status Report</b>
📅 2025-09-22 20:50:00

<b>📋 Order 1</b>
🔢 Order ID: <code>RN123456789</code>
📊 Status: <b>Preparing for Delivery</b>
🚙 Model: <b>Model Y Long Range</b>
📅 Delivery Window: <b>October 15 - October 29</b>
🚚 ETA to Delivery: <b>Oct 20, 2025</b>
🏪 Delivery Location: <b>Tesla Center Berlin</b>

<i>🔄 This is a test of the full order details format when always_notify is enabled</i>"""
        else:
            no_change_message = "🧪 <b>Tesla Order Status Script Test</b>\n\n✅ <b>No changes test:</b> This simulates a 'no changes detected' notification! 📊"
        
        await bot.send_message(chat_id=chat_id, text=no_change_message, parse_mode='HTML')
        print("✅ No-change notification test sent!")
        
        # Show current configuration
        print(f"\n📋 Current configuration:")
        print(f"   Enabled: {config.get('enabled', True)}")
        print(f"   Always notify: {config.get('always_notify', False)}")
        if config.get('always_notify', False):
            print(f"   📱 When always_notify=true: Full order details will be sent")
        else:
            print(f"   📱 When always_notify=false: Only change notifications are sent")
        
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
