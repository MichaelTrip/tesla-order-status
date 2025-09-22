#!/usr/bin/env python3
"""
Telegram Configuration Manager
Easily modify your Telegram notification settings
"""

import json
import os

TELEGRAM_CONFIG_FILE = 'telegram_config.json'

def load_config():
    """Load current configuration"""
    if not os.path.exists(TELEGRAM_CONFIG_FILE):
        print("❌ No telegram_config.json found. Run the main script first to set up Telegram.")
        return None
    
    try:
        with open(TELEGRAM_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in telegram_config.json")
        return None

def save_config(config):
    """Save configuration to file"""
    try:
        with open(TELEGRAM_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to {TELEGRAM_CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def show_current_config(config):
    """Display current configuration"""
    print("\n📋 Current Telegram Configuration:")
    print(f"   Bot Token: {config.get('bot_token', 'Not set')[:20]}...")
    print(f"   Chat ID: {config.get('chat_id', 'Not set')}")
    print(f"   Enabled: {config.get('enabled', True)}")
    print(f"   Always Notify: {config.get('always_notify', False)}")

def main():
    """Main configuration menu"""
    print("🔧 Tesla Order Status - Telegram Configuration Manager\n")
    
    config = load_config()
    if not config:
        return
    
    while True:
        show_current_config(config)
        print(f"\n⚙️ What would you like to do?")
        print("1. Enable/Disable notifications")
        print("2. Toggle 'always notify' setting")
        print("3. Change bot token")
        print("4. Change chat ID")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            current = config.get('enabled', True)
            new_value = not current
            config['enabled'] = new_value
            status = "enabled" if new_value else "disabled"
            print(f"✅ Notifications {status}")
            
        elif choice == '2':
            current = config.get('always_notify', False)
            new_value = not current
            config['always_notify'] = new_value
            if new_value:
                print("✅ Will now send notifications every time (even when no changes)")
            else:
                print("✅ Will now only send notifications when changes are detected")
                
        elif choice == '3':
            new_token = input("Enter new bot token: ").strip()
            if new_token:
                config['bot_token'] = new_token
                print("✅ Bot token updated")
            else:
                print("❌ Invalid token")
                
        elif choice == '4':
            new_chat_id = input("Enter new chat ID: ").strip()
            if new_chat_id:
                config['chat_id'] = new_chat_id
                print("✅ Chat ID updated")
            else:
                print("❌ Invalid chat ID")
                
        elif choice == '5':
            break
        else:
            print("❌ Invalid choice")
            continue
        
        # Save after each change
        save_config(config)
    
    print("\n👋 Configuration manager closed. Your settings have been saved!")

if __name__ == "__main__":
    main()
