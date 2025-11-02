from dotenv import load_dotenv
from openai import OpenAI #OpenAI Library
import discord, os

load_dotenv()
OPENAI_KEY=os.getenv('OPENAI_API_KEY')
oa_client=OpenAI(api_key=OPENAI_API_KEY)

#Ask openai - respond like a interviewer

def call_openai(question):
    #call the openai api
    completion=oa_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"Respond like a interviewer to the following question: {question}",
            }
        ]
    )

    #Print the response
    response = completion.choices[0].message.content
    print(response)
    return response

#Set up the intents
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
    if message.content.startswith('$question'):
        print(f"Message: {message.content}")
        message_content = message.content.split("$question")[1]
        print(f"Question: {message_content}")
        response = call_openai(message_content)
        print(f"Assistant: {response}")
        print("---")
        await message.channel.send(response)

token = os.getenv('TOKEN')
if not token:
    raise RuntimeError("No se recibió TOKEN desde el entorno (revisa Secrets)")

client.run(token)
