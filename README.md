## Installation

To run the script, you need to install python3 for your operating system.

https://www.python.org/downloads/

Then you need to install the required libraries by running:
```sh
pip install -r requirements.txt
```

Or install them individually:
```sh
pip install requests python-telegram-bot
```

Optional: Copy the script to a new directory, the script asks to save the tokens and order details in the current directory for reusing the tokens and for comparing the data with the last time you fetched the order details.

## Telegram Notifications Setup (Optional)

To receive Telegram notifications when your Tesla order status changes:

1. **Create a Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow the instructions to create your bot
   - Save the bot token (something like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get your Chat ID:**
   - Search for `@userinfobot` in Telegram
   - Send `/start` command
   - Note down your Chat ID (a number like `123456789`)

3. **Configure the script:**
   - Run the script for the first time
   - When prompted, choose to set up Telegram notifications
   - Enter your bot token and chat ID
   - Choose notification preferences (always notify or only on changes)
   - Or manually create a `telegram_config.json` file:
   ```json
   {
       "bot_token": "YOUR_BOT_TOKEN_HERE",
       "chat_id": "YOUR_CHAT_ID_HERE",
       "enabled": true,
       "always_notify": false
   }
   ```

### Configuration Options

- **`enabled`** (boolean): Enable/disable Telegram notifications entirely
  - `true`: Notifications are active
  - `false`: No notifications will be sent

- **`always_notify`** (boolean): Control when notifications are sent
  - `true`: Send full order details every time the script runs (even when no changes)
  - `false`: Only send notifications when changes are detected (default)

4. **Test your configuration:**
   ```sh
   python3 test_telegram.py
   ```

5. **Manage your settings:**
   ```sh
   python3 config_telegram.py
   ```

## Usage

Then you can run the script by running:
```sh
python3 tesla_order_status.py
```

### Running Automatically

To check for changes automatically, you can set up a cron job. Note that after the initial setup, the script will run without interactive prompts if tokens and configuration are already saved:

```sh
# Edit your crontab
crontab -e

# Add this line to check every hour (adjust path as needed)
0 * * * * cd /path/to/tesla-order-status && python3 tesla_order_status.py > /tmp/tesla_check.log 2>&1
```

For silent operation (only outputs when changes are found), you can redirect the output and only get notified via Telegram.

### Telegram Notification Modes

When `always_notify: true` is enabled, you'll receive detailed order information every time the script runs, including:
- Order ID and current status
- Vehicle model and VIN (if assigned)
- Delivery window and estimated arrival
- Delivery appointment details
- Delivery center location

This is perfect for regular status updates, even when nothing has changed, so you can stay informed about your order's current state.

## Preview

#### Main information
![Image](https://github.com/user-attachments/assets/b19cf27c-e3a3-48a0-9b7f-ec2c649e4166)

#### Change tracking
![Image](https://github.com/user-attachments/assets/4f1f05cb-743e-4605-97ff-3c1d0d6ff67d)

