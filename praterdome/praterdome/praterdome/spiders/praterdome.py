import json
import requests

# Define your Telegram bot token and chat ID
TOKEN = '7162097876:AAE27cvUGt6tUzuX3NI9VoNnoUsbNYYnBUM'
CHAT_ID = '-1002394818890'

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

# Process each event
for event in data:
    event_id = event.get('event_link', 'Unknown link')  # Use event link as identifier for simplicity

    # Check if the event was already sent
    if was_event_sent(event_id):
        print(f"Event '{event_id}' has already been sent. Skipping.")
        continue

    # Extract event details
    date = event.get('date', 'Unknown date')  # Use the date directly from JSON
    location = event.get('location', 'Unknown location')
    event_link = event.get('event_link', 'No link available')

    # Prepare the message
    message = (
        f"📅 *Event*: ({event_link})\n"
        f"🗓 *Date*: {date}\n"
        f"📍 *Location*: Prater Dome\n"
    )

    # Print the message to the console
    print(f"Message ready to be sent for event '{event_id}':\n{message}\n")

    # Send the message to Telegram
    response = send_telegram_message(message)
    if response.get('ok'):
        message_id = response['result']['message_id']
        print(f"Message has been sent. Message ID: {message_id}")
        # Add the event and message ID to the sent_events dictionary
        sent_events[event_id] = message_id
    else:
        print(f"Error failed to send message. Response: {response}")
