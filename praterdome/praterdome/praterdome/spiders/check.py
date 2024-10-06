import json
import asyncio
from telethon import TelegramClient

# Your API credentials from my.telegram.org
api_id = '28870257'  # Your API_ID
api_hash = 'e1438d4646b0028850650fcc9c73b058'  # Your API_HASH

# Channel ID of the "Praterdome" channel
channel_id = -1002449490106  # Praterdome channel ID

# File to save all messages
output_file = 'praterdome_messages.json'

# Create the client and connect
client = TelegramClient('praterdome_session', api_id, api_hash)

async def get_all_messages():
    try:
        # Connect to the client
        await client.start()

        # Get the channel entity
        channel = await client.get_entity(channel_id)

        # List to store all messages
        messages = []

        # Fetch all messages from the channel
        async for message in client.iter_messages(channel):
            messages.append({
                'message_id': message.id,
                'date': str(message.date),
                'sender_id': message.sender_id,
                'text': message.message,
            })

        # Save all messages to a JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

        print(f"Saved {len(messages)} messages to {output_file}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

# Run the async function
asyncio.run(get_all_messages())
