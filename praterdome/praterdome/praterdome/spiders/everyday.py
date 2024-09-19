import json
import requests
from datetime import datetime

# Define your Telegram bot token and chat ID
TOKEN = '7162097876:AAE27cvUGt6tUzuX3NI9VoNnoUsbNYYnBUM'
CHAT_ID = '-1002278281776'

# List to keep track of already sent events
sent_events = {}

# Function to check if the event was already sent
def was_event_sent(event_id):
    return event_id in sent_events

# Function to send a message to Telegram
def send_telegram_message(message):
    response = requests.post(
        f'https://api.telegram.org/bot{TOKEN}/sendMessage',
        data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    )
    return response.json()

# Load the events from the JSON file
try:
    with open('praterdome_events.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: The file 'praterdome_events.json' does not exist.")
    data = []

# Get today's date in the format 'Day Month'
today_date = datetime.now().strftime('%d %b')  # e.g., '18 Sep'
print(f"Today's date: {today_date}.")

# Process each event
for event in data:
    event_date_str = event.get('date', 'Unknown date')
    event_date = datetime.strptime(event_date_str, '%A, %d %b').strftime('%d %b')  # Convert to 'Day Month'

    location = event.get('location', 'Unknown location')
    event_link = event.get('event_link', 'No link available')

    # Prepare the message

    message = (
        f"📅 *Event*: ({event_link})\n"
        f"🗓 *Date*: {event_date_str}\n"
        f"📍 *Location*: Prater Dome\n"
    )

    if today_date == event_date:
        response = send_telegram_message(message)
