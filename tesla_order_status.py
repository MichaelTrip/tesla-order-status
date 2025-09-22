import base64
import json
import os
import time
import hashlib
import requests
import webbrowser
import urllib.parse
import asyncio
from datetime import datetime

from tesla_stores import TeslaStore
from telegram import Bot
from telegram.error import TelegramError

# Define constants
CLIENT_ID = 'ownerapi'
REDIRECT_URI = 'https://auth.tesla.com/void/callback'
AUTH_URL = 'https://auth.tesla.com/oauth2/v3/authorize'
TOKEN_URL = 'https://auth.tesla.com/oauth2/v3/token'
SCOPE = 'openid email offline_access'
CODE_CHALLENGE_METHOD = 'S256'
STATE = os.urandom(16).hex()
TOKEN_FILE = 'tesla_tokens.json'
ORDERS_FILE = 'tesla_orders.json'
TELEGRAM_CONFIG_FILE = 'telegram_config.json'
APP_VERSION = '9.99.9-9999' # we can use a dummy version here, as the API does not check it strictly

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def generate_code_verifier_and_challenge():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip(
        b'=').decode('utf-8')
    return code_verifier, code_challenge


def get_auth_code():
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
        'state': STATE,
        'code_challenge': code_challenge,
        'code_challenge_method': CODE_CHALLENGE_METHOD,
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    print(color_text("> Opening the browser for authentication:", '94'), auth_url)
    webbrowser.open(auth_url)
    print(color_text("After authentication, you’ll be redirected to a new URL. The page might show a 'Page Not Found' error message, but the URL itself is still valid for this purpose.", '90'))
    redirected_url = input(color_text("Please enter the redirected URL here: ", '93'))
    parsed_url = urllib.parse.urlparse(redirected_url)
    return urllib.parse.parse_qs(parsed_url.query).get('code')[0]


def exchange_code_for_tokens(auth_code):
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    response.raise_for_status()
    return response.json()


def save_tokens_to_file(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)
    print(color_text(f"> Tokens saved to '{TOKEN_FILE}'", '94'))


def load_tokens_from_file():
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)


def is_token_valid(access_token):
    jwt_decoded = json.loads(base64.b64decode(access_token.split('.')[1] + '==').decode('utf-8'))
    return jwt_decoded['exp'] > time.time()


def refresh_tokens(refresh_token):
    token_data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'refresh_token': refresh_token,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    response.raise_for_status()
    return response.json()


def retrieve_orders(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    api_url = 'https://owner-api.teslamotors.com/api/1/users/orders'
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()['response']


def get_order_details(order_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    api_url = f'https://akamai-apigateway-vfx.tesla.com/tasks?deviceLanguage=en&deviceCountry=DE&referenceNumber={order_id}&appVersion={APP_VERSION}'
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()


def save_orders_to_file(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f)
    print(color_text(f"\n> Orders saved to '{ORDERS_FILE}'", '94'))


def load_orders_from_file():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return None


def load_telegram_config():
    """Load Telegram configuration from file"""
    if not os.path.exists(TELEGRAM_CONFIG_FILE):
        return None
    
    try:
        with open(TELEGRAM_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
        if not config.get('bot_token') or not config.get('chat_id'):
            return None
            
        return config
    except (json.JSONDecodeError, KeyError):
        return None


def setup_telegram_config():
    """Interactive setup for Telegram configuration"""
    print(color_text("\n> Setting up Telegram notifications...", '94'))
    print(color_text("To enable Telegram notifications, you need:", '90'))
    print(color_text("1. Create a Telegram bot by messaging @BotFather", '90'))
    print(color_text("2. Get your chat ID by messaging @userinfobot", '90'))
    print(color_text("3. Enter the details below", '90'))
    
    bot_token = input(color_text("Enter your Telegram bot token: ", '93')).strip()
    chat_id = input(color_text("Enter your chat ID: ", '93')).strip()
    
    if not bot_token or not chat_id:
        print(color_text("Invalid input. Skipping Telegram setup.", '91'))
        return None
    
    config = {
        'bot_token': bot_token,
        'chat_id': chat_id
    }
    
    try:
        with open(TELEGRAM_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(color_text(f"> Telegram configuration saved to '{TELEGRAM_CONFIG_FILE}'", '94'))
        return config
    except Exception as e:
        print(color_text(f"Error saving Telegram config: {e}", '91'))
        return None


async def send_telegram_message(bot_token, chat_id, message):
    """Send a message to Telegram"""
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        return True
    except TelegramError as e:
        print(color_text(f"Error sending Telegram message: {e}", '91'))
        return False
    except Exception as e:
        print(color_text(f"Unexpected error sending Telegram message: {e}", '91'))
        return False


def format_telegram_message(differences, order_count):
    """Format differences for Telegram message"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"🚗 <b>Tesla Order Status Update</b>\n"
    message += f"📅 {timestamp}\n\n"
    
    if order_count == 1:
        message += f"📋 Detected changes in your Tesla order:\n\n"
    else:
        message += f"📋 Detected changes in your Tesla orders:\n\n"
    
    # Process differences and make them more readable
    for diff in differences[:20]:  # Limit to first 20 changes to avoid message length issues
        # Remove ANSI color codes for Telegram
        clean_diff = diff.replace('\033[91m', '').replace('\033[92m', '').replace('\033[0m', '')
        
        if clean_diff.startswith('- '):
            message += f"❌ {clean_diff[2:]}\n"
        elif clean_diff.startswith('+ '):
            message += f"✅ {clean_diff[2:]}\n"
        else:
            message += f"ℹ️ {clean_diff}\n"
    
    if len(differences) > 20:
        message += f"\n... and {len(differences) - 20} more changes"
    
    message += f"\n\n🔄 Check your Tesla account for complete details."
    
    return message


def compare_dicts(old_dict, new_dict, path=''):
    differences = []
    for key in old_dict:
        if key not in new_dict:
            differences.append(color_text(f"- Removed key '{path + key}'", '91'))
        elif isinstance(old_dict[key], dict) and isinstance(new_dict[key], dict):
            differences.extend(compare_dicts(old_dict[key], new_dict[key], path + key + '.'))
        elif old_dict[key] != new_dict[key]:
            differences.append(color_text(f"- {path + key}: {old_dict[key]}", '91'))
            differences.append(color_text(f"+ {path + key}: {new_dict[key]}", '92'))

    for key in new_dict:
        if key not in old_dict:
            differences.append(color_text(f"+ Added key '{path + key}': {new_dict[key]}", '92'))

    return differences


def compare_orders(old_orders, new_orders):
    differences = []
    for i, old_order in enumerate(old_orders):
        if i < len(new_orders):
            differences.extend(compare_dicts(old_order, new_orders[i], path=f'Order {i}.'))
        else:
            differences.append(color_text(f"- Removed order {i}", '91'))
    for i in range(len(old_orders), len(new_orders)):
        differences.append(color_text(f"+ Added order {i}", '92'))
    return differences


# Main script logic
print(color_text("\n> Start retrieving the information. Please be patient...\n", '94'))

# Check if running in non-interactive mode (like cron)
is_interactive = os.isatty(0)  # Check if stdin is a terminal

# Load or setup Telegram configuration
telegram_config = load_telegram_config()
if not telegram_config and is_interactive:
    setup_choice = input(color_text("Would you like to set up Telegram notifications? (y/n): ", '93')).lower()
    if setup_choice == 'y':
        telegram_config = setup_telegram_config()

code_verifier, code_challenge = generate_code_verifier_and_challenge()

if os.path.exists(TOKEN_FILE):
    try:
        token_file = load_tokens_from_file()
        access_token = token_file['access_token']
        refresh_token = token_file['refresh_token']

        if not is_token_valid(access_token):
            print(color_text("> Access token is not valid. Refreshing tokens...", '94'))
            token_response = refresh_tokens(refresh_token)
            access_token = token_response['access_token']
            # refresh access token in file
            token_file['access_token'] = access_token
            save_tokens_to_file(token_file)

    except (json.JSONDecodeError, KeyError) as e:
        print(color_text("> Error loading tokens from file. Re-authenticating...", '94'))
        token_response = exchange_code_for_tokens(get_auth_code())
        access_token = token_response['access_token']
        refresh_token = token_response['refresh_token']
        save_tokens_to_file(token_response)
else:
    if not is_interactive:
        print(color_text("❌ No tokens found and running in non-interactive mode. Please run the script manually first to authenticate.", '91'))
        exit(1)
    
    token_response = exchange_code_for_tokens(get_auth_code())
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']
    if input(color_text("Would you like to save the tokens to a file in the current directory for use in future requests? (y/n): ", '93')).lower() == 'y':
        save_tokens_to_file(token_response)

old_orders = load_orders_from_file()
new_orders = retrieve_orders(access_token)

# Retrieve detailed order information
detailed_new_orders = []
for order in new_orders:
    order_id = order['referenceNumber']
    order_details = get_order_details(order_id, access_token)
    detailed_order = {
        'order': order,
        'details': order_details
    }
    detailed_new_orders.append(detailed_order)

if old_orders:
    differences = compare_orders(old_orders, detailed_new_orders)
    if differences:
        print(color_text("Differences found:", '90'))
        for diff in differences:
            print(diff)
        save_orders_to_file(detailed_new_orders)
        
        # Send Telegram notification if configured
        if telegram_config:
            print(color_text("\n> Sending Telegram notification...", '94'))
            telegram_message = format_telegram_message(differences, len(detailed_new_orders))
            
            # Run the async function
            try:
                success = asyncio.run(send_telegram_message(
                    telegram_config['bot_token'], 
                    telegram_config['chat_id'], 
                    telegram_message
                ))
                if success:
                    print(color_text("✅ Telegram notification sent successfully!", '92'))
                else:
                    print(color_text("❌ Failed to send Telegram notification", '91'))
            except Exception as e:
                print(color_text(f"❌ Error sending Telegram notification: {e}", '91'))
    else:
        print(color_text("No differences found.", '90'))
    
else:
    # ask user if they want to save the new orders to a file for comparison next time
    if is_interactive and input(color_text("Would you like to save the order information to a file for future comparison? (y/n): ", '93')).lower() == 'y':
        save_orders_to_file(detailed_new_orders)

for detailed_order in detailed_new_orders:
    order = detailed_order['order']
    order_details = detailed_order['details']
    scheduling = order_details.get('tasks', {}).get('scheduling', {})
    order_info = order_details.get('tasks', {}).get('registration', {}).get('orderDetails', {})
    final_payment_data = order_details.get('tasks', {}).get('finalPayment', {}).get('data', {})

    print(f"\n{'-'*45}")
    print(f"{'ORDER INFORMATION':^45}")
    print(f"{'-'*45}")

    print(f"{color_text('Order Details:', '94')}")
    print(f"{color_text('- Order ID:', '94')} {order['referenceNumber']}")
    print(f"{color_text('- Status:', '94')} {order['orderStatus']}")
    print(f"{color_text('- Model:', '94')} {order['modelCode']}")
    print(f"{color_text('- VIN:', '94')} {order.get('vin', 'N/A')}")
    
    print(f"\n{color_text('Reservation Details:', '94')}")
    print(f"{color_text('- Reservation Date:', '94')} {order_info.get('reservationDate', 'N/A')}")
    print(f"{color_text('- Order Booked Date:', '94')} {order_info.get('orderBookedDate', 'N/A')}")

    print(f"\n{color_text('Vehicle Status:', '94')}")
    print(f"{color_text('- Vehicle Odometer:', '94')} {order_info.get('vehicleOdometer', 'N/A')} {order_info.get('vehicleOdometerType', 'N/A')}")

    print(f"\n{color_text('Delivery Information:', '94')}")
    print(f"{color_text('- Routing Location:', '94')} {order_info.get('vehicleRoutingLocation', 'N/A')} ({TeslaStore(order_info.get('vehicleRoutingLocation', 0)).label})")
    print(f"{color_text('- Delivery Window:', '94')} {scheduling.get('deliveryWindowDisplay', 'N/A')}")
    print(f"{color_text('- ETA to Delivery Center:', '94')} {final_payment_data.get('etaToDeliveryCenter', 'N/A')}")
    print(f"{color_text('- Delivery Appointment:', '94')} {scheduling.get('apptDateTimeAddressStr', 'N/A')}")

    print(f"{'-'*45}\n")

