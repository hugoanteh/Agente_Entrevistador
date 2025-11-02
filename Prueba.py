# Prueba.py
from dotenv import load_dotenv
from openai import OpenAI
import discord
import os

# Carga variables de entorno (.env en local / Secrets en Actions)
load_dotenv()

# --- OpenAI ---
# Usa la clave estándar del entorno: OPENAI_API_KEY (configúrala en GitHub Secrets)
oa_client = OpenAI()  # no pases api_key aquí; la toma de OPENAI_API_KEY automáticamente

def call_openai(question: str) -> str:
    """Pide a OpenAI que responda como entrevistador."""
    q = (question or "").strip()
    if not q:
        return "Por favor, escribe tu pregunta después de $question."

    completion = oa_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": (
                    "Responde como un ENTREVISTADOR profesional, con tono cordial, "
                    "guiando la conversación y repreguntando de forma breve cuando aplique. "
                    f"Pregunta del candidato: {q}"
                ),
            }
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content

# --- Discord ---
intents = discord.Intents.default()
intents.message_content = True  # activar también en el Portal de Discord (Bot → Message Content Intent)

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como: {client.user}")

@client.event
async def on_message(message: discord.Message):
    # No responderse a sí mismo
    if message.author.id == client.user.id:
        return

    content = (message.content or "").strip()

    # Comando simple
    if content.startswith("$hello"):
        await message.channel.send("Hello!")
        return

    # Comando con pregunta a OpenAI: $question <texto>
    if content.startswith("$question"):
        # Extrae todo lo que viene después de "$question"
        user_question = content[len("$question"):].strip()

        try:
            response = call_openai(user_question)
        except Exception as e:
            # Log para diagnóstico en Actions
            print("OpenAI error:", repr(e))
            response = "Hubo un problema consultando a OpenAI. Intenta de nuevo en unos segundos."

        await message.channel.send(response)
        return

# --- Token Discord ---
token = os.getenv("TOKEN")
if not token:
    raise RuntimeError("No se recibió TOKEN desde el entorno. Revisa Settings → Secrets → Actions → TOKEN.")

print("TOKEN leído desde entorno:", "OK" if token else "NO ENCONTRADO")
print("OPENAI_API_KEY presente:", "OK" if os.getenv("OPENAI_API_KEY") else "NO ENCONTRADO")

client.run(token)
