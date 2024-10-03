from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import json

API_ID = 28870257  # Your API ID
API_HASH = 'e1438d4646b0028850650fcc9c73b058'  # Your API HASH
phone = '+421949550035'  # Your phone number

# Create a new Telegram client
client = TelegramClient('my-client', API_ID, API_HASH)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))

chats = []
last_date = None
chunk_size = 200
groups = []

# Retrieve the list of all groups
try:
    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)
except Exception as e:
    print(f"An error occurred while retrieving the chats: {e}")

# Display all types of groups
print('All available chats:')
for chat in chats:
    print(f"Chat: {chat.title}, is_megagroup: {getattr(chat, 'megagroup', False)}")
    groups.append(chat)  # Add all groups regardless of type

# Display selection of groups to scrape members and messages
print('Choose a group to scrape members and messages from:')
for i, g in enumerate(groups):
    print(f"{i} | {g.title}")

try:
    g_index = int(input("Enter a Number: "))
    target_group = groups[g_index]
except (ValueError, IndexError):
    print("Invalid input. Please enter a valid number.")
    exit(1)

print('Fetching Members and Messages...')
try:
    all_participants = client.get_participants(target_group, aggressive=True)
except Exception as e:
    print(f"An error occurred while fetching participants: {e}")
    exit(1)

# Save data to JSON file
print('Saving to file...')
members_data = []

async def fetch_messages_for_user(user):
    """Function to fetch messages for a specific user."""
    messages = []
    async for message in client.iter_messages(target_group, from_user=user):
        # Check if the message has text; if not, show as 'No text available'
        message_text = message.text if message.text else 'No text available'
        messages.append({
            "message_id": message.id,
            "text": message_text,
            "date": str(message.date)
        })
    return messages

async def main():
    """Main function to process members and their messages."""
    for user in all_participants:
        username = user.username if user.username else ""
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        name = (first_name + ' ' + last_name).strip()

        # Fetch messages for a specific user
        messages = await fetch_messages_for_user(user)

        member_info = {
            "username": username,
            "user_id": user.id,
            "access_hash": user.access_hash,
            "name": name,
            "group": target_group.title,
            "group_id": target_group.id,
            "messages": messages  # Add user messages
        }

        members_data.append(member_info)

    # Write data to JSON file
    with open("members_with_messages.json", "w", encoding="UTF-8") as f:
        json.dump(members_data, f, ensure_ascii=False, indent=4)

    print('Members and their messages scraped and saved to members_with_messages.json successfully.')

# Run the main function
with client:
    client.loop.run_until_complete(main())
