import json
import requests
from datetime import datetime

# Define your Telegram bot token and chat ID
TOKEN = '[YOUR BOT TOKEN]'
CHAT_ID = '[YOUR CHANNEL/CHAT ID]'

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

# Remove duplicate events based on 'event_link'
unique_events = []
seen_event_links = set()

for event in data:
    event_link = event.get('event_link', 'No link available')

    # Check if the event link is a duplicate
    if event_link not in seen_event_links:
        unique_events.append(event)  # Add event if it's unique
        seen_event_links.add(event_link)  # Mark the event link as seen
    else:
        print(f"Duplicate event found and removed: {event_link}")

# Update the 'data' with the unique events
data = unique_events

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
