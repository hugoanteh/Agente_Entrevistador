from dotenv import load_dotenv
from openai import OpenAI
import discord, os, traceback

load_dotenv()

oa_client = OpenAI()

# Modelo preferido y alternativa
PRIMARY_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")       # puedes dejar "gpt-4o"
FALLBACK_MODEL = os.getenv("OPENAI_FALLBACK", "gpt-4o-mini")

def ask_openai(model: str, question: str) -> str:
    completion = oa_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": (
                    "Responde como un ENTREVISTADOR profesional, con tono cordial, "
                    "guiando la conversación y repreguntando brevemente cuando aplique. "
                    f"Pregunta del candidato: {question.strip()}"
                ),
            }
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content

def call_openai(question: str) -> str:
    q = (question or "").strip()
    if not q:
        return "Por favor, escribe tu pregunta después de $question."

    # Intento con el modelo principal; si falla por permiso/acceso, probamos el fallback.
    try:
        return ask_openai(PRIMARY_MODEL, q)
    except Exception as e:
        # Logs completos al runner (Actions)
        print("=== OpenAI ERROR (primary) ===")
        print("Model:", PRIMARY_MODEL)
        print("Type:", e.__class__.__name__)
        print("Error:", repr(e))
        traceback.print_exc()

        # Si es un problema típico de acceso al modelo, probamos el fallback una sola vez
        err_text = str(e).lower()
        if any(t in err_text for t in ["permission", "access", "not found", "model", "404", "403"]):
            try:
                print("Reintentando con fallback:", FALLBACK_MODEL)
                return ask_openai(FALLBACK_MODEL, q)
            except Exception as e2:
                print("=== OpenAI ERROR (fallback) ===")
                print("Model:", FALLBACK_MODEL)
                print("Type:", e2.__class__.__name__)
                print("Error:", repr(e2))
                traceback.print_exc()
                return "No tengo acceso a los modelos configurados. Verifica que tu API key tenga permisos y crédito."
        # Otros errores (401/429, etc.)
        if any(t in err_text for t in ["unauthorized", "invalid api key", "billing", "quota", "rate limit", "401", "429"]):
            return "La API de OpenAI reporta un problema de credenciales, cuota o facturación."

        return "Hubo un problema consultando a OpenAI. Intenta de nuevo en unos segundos."

# … (intents y client como ya los tienes) …

@client.event
async def on_message(message: discord.Message):
    if message.author.id == client.user.id:
        return

    content = (message.content or "").strip()

    if content.startswith("$hello"):
        await message.channel.send("Hello!")
        return

    # Diagnóstico rápido
    if content.startswith("$diag"):
        await message.channel.send(
            f"Modelo primario: `{PRIMARY_MODEL}` | Fallback: `{FALLBACK_MODEL}`\n"
            f"API key presente: {'OK' if os.getenv('OPENAI_API_KEY') else 'NO'}"
        )
        return

    if content.startswith("$question"):
        user_q = content[len("$question"):].strip()
        resp = call_openai(user_q)
        await message.channel.send(resp)
        return
