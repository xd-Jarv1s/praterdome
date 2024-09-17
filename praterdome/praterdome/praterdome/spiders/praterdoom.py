import json
import requests
from datetime import datetime

# Define your Telegram bot token and chat ID
TOKEN = '7162097876:AAE27cvUGt6tUzuX3NI9VoNnoUsbNYYnBUM'
CHAT_ID = '-1002449490106'

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

# Function to delete a message from Telegram
def delete_telegram_message(message_id):
    response = requests.post(
        f'https://api.telegram.org/bot{TOKEN}/deleteMessage',
        data={'chat_id': CHAT_ID, 'message_id': message_id}
    )
    return response.json()

# Load the events from the JSON file
try:
    with open('praterdome_events.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Chyba: Súbor 'praterdome_events.json' neexistuje.")
    data = []

# Get today's date
today_date = datetime.today().strftime('%d %b')  # Format as 'day month'
print(f"Dnešný dátum: {today_date}.")

# Process each event
for event in data:
    event_date = f"{event.get('day', 'Unknown day')} {event.get('month', 'Unknown month')}"
    event_id = event.get('event_link', 'Unknown link')  # Use event link as identifier for simplicity

    # Check if the event's date is today
    if event_date != today_date:
        print(f"Event '{event_id}' is not planned for today ({today_date}). Skipping.")
        continue

    # Check if the event was already sent
    if was_event_sent(event_id):
        # Delete the old message if it exists
        old_message_id = sent_events[event_id]
        print(f"Event '{event_id}' has benn sent. Deleteing the message with ID: {old_message_id}.")
        delete_telegram_message(old_message_id)
        continue

    # Extract event details
    date = event_date
    location = event.get('location', 'Unknown location')
    event_link = event.get('event_link', 'No link available')

    # Prepare the message
    message = (
        f"📅 *Event*: [More Info]({event_link})\n"
        f"🗓 *Date*: {date}\n"
        f"📍 *Location*: {location}"
    )

    # Print the message to the console
    print(f"Message ready to sent to event '{event_id}':\n{message}\n")

    # Send the message to Telegram
    response = send_telegram_message(message)
    if response.get('ok'):
        message_id = response['result']['message_id']
        print(f"Message has been sent. ID message: {message_id}")
        # Add the event and message ID to the sent_events dictionary
        sent_events[event_id] = message_id
    else:
        print(f"Error failed to send message. Response: {response}")

# Save the updated sent_events to a file to persist the state
with open('sent_events.json', 'w') as file:
    json.dump(sent_events, file, indent=4)
