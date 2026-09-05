import os
import discord
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the local .env file
load_dotenv()

# Setup Discord intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Retrieve keys safely
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

groq_client = Groq(api_key=GROQ_API_KEY)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} - Host status: 24/7 Online!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        clean_prompt = message.content.replace(f'<@{client.user.id}>', '').strip()

        if not clean_prompt:
            await message.channel.send("Hello! Ask me anything.")
            return

        async with message.channel.typing():
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": clean_prompt}],
                model="llama-3.3-70b-versatile"
            )
            reply = chat_completion.choices[0].message.content

        if len(reply) > 2000:
            for i in range(0, len(reply), 1900):
                await message.channel.send(reply[i:i+1900])
        else:
            await message.channel.send(reply)

client.run(DISCORD_TOKEN)