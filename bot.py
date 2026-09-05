import os
import threading
import discord
from dotenv import load_dotenv
from flask import Flask
from groq import Groq, GroqError

# Load local environment variables
load_dotenv()

# --- DUMMY WEB SERVER FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Run web server on a background thread
threading.Thread(target=run_web_server, daemon=True).start()
# -----------------------------------

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

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
            try:
                # Call Groq API safely
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": clean_prompt}],
                    model="llama-3.1-8b-instant"
                )
                reply = chat_completion.choices[0].message.content

            except GroqError:
                reply = "Groq servers are experiencing high traffic right now. Please try again in a few moments!"
            except Exception as e:
                reply = "An error occurred while generating a response. Please try again."

        # Handle message length limits safely
        if len(reply) > 2000:
            for i in range(0, len(reply), 1900):
                await message.channel.send(reply[i:i+1900])
        else:
            await message.channel.send(reply)

client.run(DISCORD_TOKEN)