import json
import requests

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

# Function to retrieve message history from the Telegram channel
def get_message_history():
    print("[DEBUG] Retrieving message history from Telegram.")
    response = requests.post(f'https://api.telegram.org/bot{TOKEN}/getUpdates')
    if response.status_code == 200:
        print("[DEBUG] Successfully retrieved message history.")
        return response.json().get('result', [])
    else:
        print(f"[ERROR] Failed to retrieve message history. Status code: {response.status_code}.")
        return []

# Function to delete a message from Telegram by its message_id
def delete_telegram_message(message_id):
    print(f"[DEBUG] Attempting to delete message ID: {message_id}.")
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
    print("Error: The file 'praterdome_events.json' does not exist.")
    data = []

# Retrieve current messages in the channel
current_messages = get_message_history()
messages_seen = {}

# Store current messages for duplicate checking
for msg in current_messages:
    if 'message' in msg and 'text' in msg['message']:
        message_text = msg['message']['text']
        messages_seen[message_text] = msg['message']['message_id']

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
        f"📍 *Location*: {location}\n"
    )

    # Check if the message already exists in the channel
    if message in messages_seen:
        message_id = messages_seen[message]
        print(f"[DEBUG] Duplicate message found for event '{event_id}'. Deleting message ID: {message_id}.")
        delete_response = delete_telegram_message(message_id)
        if delete_response.get('ok'):
            print(f"[DEBUG] Successfully deleted duplicate message ID: {message_id}.")
        else:
            print(f"[ERROR] Failed to delete message ID: {message_id}. Response: {delete_response}")
        continue  # Skip sending the duplicate message

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
        print(f"[ERROR] Failed to send message. Response: {response}")
