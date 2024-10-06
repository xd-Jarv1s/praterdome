import json
import requests
from datetime import datetime

# Define your Telegram bot token and chat ID
TOKEN = ''
CHAT_ID = ''

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

# Function to delete a message from Telegram by its message_id
def delete_telegram_message(message_id):
    response = requests.post(
        f'https://api.telegram.org/bot{TOKEN}/deleteMessage',
        data={'chat_id': CHAT_ID, 'message_id': message_id}
    )
    return response.json()

# Function to get recent messages from the chat to check for duplicates
def get_recent_messages(limit=100):
    response = requests.get(
        f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    )
    return response.json().get('result', [])[-limit:]

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

# Fetch recent messages to check for duplicates
recent_messages = get_recent_messages()

# Process each event and remove duplicate Telegram messages
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
        # Check for duplicate messages
        for recent_message in recent_messages:
            if 'message' in recent_message:
                text = recent_message['message'].get('text', '')
                # If the message text matches, delete the duplicate
                if message in text:
                    message_id = recent_message['message']['message_id']
                    delete_response = delete_telegram_message(message_id)
                    if delete_response.get('ok'):
                        print(f"Deleted duplicate message with ID: {message_id}")
                    else:
                        print(f"Failed to delete message with ID: {message_id}. Response: {delete_response}")
                    break  # Stop checking after finding a duplicate

        # Send a new message if it hasn't been sent yet
        if not was_event_sent(event_link):
            response = send_telegram_message(message)
            if response.get('ok'):
                message_id = response['result']['message_id']
                print(f"Message sent successfully. Message ID: {message_id}")
                sent_events[event_link] = message_id  # Track the message
            else:
                print(f"Failed to send message. Response: {response}")
