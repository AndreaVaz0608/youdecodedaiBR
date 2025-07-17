import requests
import os
import time
import base64
from dotenv import load_dotenv
from flask import current_app

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"[DID][DEBUG] load_dotenv() exception: {e}")

DID_API_URL = "https://api.d-id.com/clips"
DID_API_KEY = os.getenv("DID_API_KEY")
AVATAR_SOURCE_URL = "https://models.d-id.com/emily/Emily%20rev1.mp4"

# Headers com autenticação segura
def get_headers():
    if DID_API_KEY and ":" in DID_API_KEY:
        encoded_key = base64.b64encode(DID_API_KEY.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
    return {
        "Authorization": f"Bearer {DID_API_KEY}",
        "Content-Type": "application/json"
    }

def limitar_texto(texto, limite=800):
    if len(texto) <= limite:
        return texto
    return texto[:limite].rsplit(".", 1)[0] + "."

@user_bp.route('/coaching-video', methods=['POST'])
def coaching_video_endpoint():
    if 'user_id' not in session:
        return {"erro": "Not logged in"}, 401

    user_id = session['user_id']
    pergunta = request.form.get("pergunta", "").strip()

    if not pergunta:
        return {"erro": "Empty question"}, 400

    # Busca perfil
    ultima_sessao = (
        TestSession.query
        .filter_by(user_id=user_id)
        .filter(TestSession.ai_result.isnot(None))
        .order_by(TestSession.created_at.desc())
        .first()
    )

    mbti = ultima_sessao.mbti_result if ultima_sessao else "N/A"
    disc = ultima_sessao.disc_result if ultima_sessao else "N/A"
    eneagrama = ultima_sessao.eneagrama_result if ultima_sessao else "N/A"

    prompt = f"""
You are a wise and empathetic personal and career coach AI.
The user has the following behavioral profile:
- MBTI: {mbti}
- DISC: {disc}
- Enneagram: {eneagrama}

Their question is:
\"{pergunta}\"

Give a response that is practical, inspiring, emotionally intelligent, and tailored to this personality.
Keep the response under 300 words.
"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a wise and empathetic coaching assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75,
            max_tokens=500
        )
        texto = response.choices[0].message.content.strip()

        # ✅ NÃO chama solicitar_video nem retorna clip_id
        return {
            "resposta_texto": texto,
            "clip_id": None
        }

    except Exception as e:
        current_app.logger.error(f"[COACHING_TEXT_ONLY ERROR] {e}")
        return {"erro": "Internal error"}, 500
