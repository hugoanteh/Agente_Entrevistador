from dotenv import load_dotenv
import discord, os

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot conectado como: {client.user}')

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

token = os.getenv('TOKEN')
if not token:
    raise RuntimeError("No se recibió TOKEN desde el entorno (revisa Secrets)")

client.run(token)
