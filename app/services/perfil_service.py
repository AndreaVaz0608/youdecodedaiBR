import openai
import os
from flask import current_app, session
from dotenv import load_dotenv

load_dotenv()  # Ensures environment variables are loaded

# === MBTI ===
MBTI_DIMENSIONS = {
    'E': [1001, 1005, 1010, 1012, 1020, 1040],
    'I': [1002, 1006, 1011, 1013, 1021, 1041],
    'S': [1003, 1007, 1015, 1039, 1049, 1052],
    'N': [1008, 1016, 1036, 1042, 1050, 1053],
    'T': [1004, 1017, 1022, 1037, 1043, 1054],
    'F': [1009, 1018, 1023, 1038, 1044, 1055],
    'J': [1014, 1019, 1024, 1045, 1048, 1056],
    'P': [1025, 1026, 1046, 1047, 1051, 1057],
}

# === DISC ===
DISC_FACTORS = {
    'D': [2001, 2003, 2005, 2008, 2011, 2014],
    'I': [2002, 2006, 2009, 2012, 2015, 2017],
    'S': [2004, 2007, 2010, 2016, 2018, 2020],
    'C': [2013, 2019, 2021, 2022, 2023, 2024],
}

# === Enneagram ===
ENNEAGRAM_TYPES = {
    '1': [3001, 3022, 3033, 3034, 3043],
    '2': [3002, 3011, 3023, 3035, 3044],
    '3': [3003, 3012, 3024, 3036, 3045],
    '4': [3004, 3013, 3025, 3037, 3046],
    '5': [3005, 3014, 3026, 3038, 3047],
    '6': [3006, 3015, 3027, 3039, 3048],
    '7': [3007, 3016, 3028, 3040, 3049],
    '8': [3008, 3017, 3029, 3041, 3050],
    '9': [3009, 3018, 3030, 3042, 3051],
}

def generate_behavior_prompt(profile_combination: dict, nome: str = "você") -> str:
    mbti = profile_combination.get("mbti")
    disc = profile_combination.get("disc")
    enneagram = profile_combination.get("eneagrama")

    mbti_description = {
        'E': "Extrovertido(a) – ganha energia com interação social",
        'I': "Introvertido(a) – recarrega na introspecção",
        'S': "Sensorial – atento(a) a fatos e realidade concreta",
        'N': "Intuitivo(a) – guiado(a) por ideias e possibilidades futuras",
        'T': "Pensamento – decide com lógica e objetividade",
        'F': "Sentimento – valoriza pessoas e emoções nas decisões",
        'J': "Julgador(a) – prefere estrutura e planejamento",
        'P': "Perceptivo(a) – valoriza liberdade e espontaneidade",
    }
    mbti_explained = ' / '.join([mbti_description.get(letter, '') for letter in mbti])

    disc_labels = {
        'D': "Dominância – foco em resultados, firmeza e competitividade",
        'I': "Influência – comunicativo(a), entusiasta, envolvente",
        'S': "Estabilidade – calmo(a), confiável, orientado(a) ao grupo",
        'C': "Cautela – preciso(a), analítico(a), foco na qualidade",
    }
    disc_explained = ' / '.join([disc_labels.get(letter, '') for letter in disc])

    enneagram_explained = f"Type {enneagram[0]} – (Dominant Type): See description below."

    prompt = f"""
Você é um(a) mentor(a) comportamental sênior, especialista em coaching, liderança e análise de personalidade com base em MBTI, DISC e Eneagrama. Sua missão é criar um relatório profundamente personalizado e prático com base nesses dados psicométricos.

O(a) usuário(a) se chama {nome}. Abaixo, os perfis identificados:

- MBTI: {mbti} → {mbti_explained}
- DISC: {disc} → {disc_explained}
- Eneagrama: Tipo {enneagram[0]} – padrão dominante

Contexto comportamental:
Esta pessoa é estratégica e cheia de energia, guiada por conexões e impacto real no mundo. Valoriza autonomia, evita rotinas engessadas e lidera com visão e influência. Sob pressão, pode alternar entre impulsividade e controle. Busca crescer, alcançar alta performance e manter autenticidade emocional.

O relatório deve parecer escrito exclusivamente para {nome} — evite respostas genéricas, linguagem vaga ou elogios vazios.

Use exatamente esta estrutura e escreva com tom acolhedor, seguro e pragmático:

### 🌟 1. INTRODUÇÃO PERSONALIZADA  
Explique como o relatório vai ajudar {nome} a compreender seus potenciais, pontos cegos e caminhos de evolução.

### 💡 2. INSIGHTS DO MBTI  
Interprete o tipo MBTI com base no ritmo de vida, valores e fontes de energia de {nome}.

### 🔥 3. ESTILO DISC  
Descreva como {nome} age, reage e lidera sob pressão, segundo o DISC.

### 🧭 4. VISÃO DO ENEAGRAMA  
Explique o tipo dominante ({enneagram}) com foco nos medos, padrões de fuga e talentos naturais.

### 🧩 5. INTEGRAÇÃO DOS MODELOS  
Cruze MBTI, DISC e Eneagrama para revelar 2 contradições comportamentais e 2 sinergias únicas.

### 🚀 6. FORÇAS E ARMADILHAS  
O que faz {nome} brilhar? Quais padrões podem atrapalhar?

### 🎯 7. TOMADA DE DECISÃO E AUTOGESTÃO  
Mostre como essa pessoa decide, duvida, se compromete — e como evoluir nesse ciclo.

### 💬 8. COMUNICAÇÃO E ENERGIA SOCIAL  
Descreva o estilo, volume e alinhamento na forma como {nome} se expressa e se conecta.

### 💞 9. RELACIONAMENTOS E LIDERANÇA  
Explique que tipo de presença {nome} representa em times, conflitos e vínculos emocionais.

### 📝 10. ANÁLISE DE EVOLUÇÃO HISTÓRICA  
Avalie os últimos 6 perfis do(a) usuário(a). Aponte padrões, melhorias ou regressões.  
- Destaque 1 força que se manteve estável.  
- Destaque 1 desafio que persiste.  
- Destaque 1 nova oportunidade com base na evolução.

### 📝 11. PLANO DE AÇÃO – PRÓXIMOS 30 DIAS  
Apresente 3 sugestões práticas e de alto impacto para desenvolvimento pessoal.

Finalize com uma nota de clareza e motivação, partindo do princípio de que {nome} está em jornada de crescimento e verdade.
"""
    return prompt.strip()

def generate_profile_key(responses: dict) -> dict:
    def calculate_mbti():
        scores = {k: 0 for k in MBTI_DIMENSIONS}
        for side, questions in MBTI_DIMENSIONS.items():
            for qid in questions:
                scores[side] += responses.get(qid, 3)
        print("🔍 MBTI Scores:", scores)
        return ''.join([
            'E' if scores['E'] >= scores['I'] else 'I',
            'S' if scores['S'] >= scores['N'] else 'N',
            'T' if scores['T'] >= scores['F'] else 'F',
            'J' if scores['J'] >= scores['P'] else 'P',
        ])

    def calculate_disc():
        scores = {k: sum(responses.get(qid, 3) for qid in qs) for k, qs in DISC_FACTORS.items()}
        print("🔍 DISC Scores:", scores)
        top_two = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        return ''.join([t[0] for t in top_two])

    def calculate_enneagram():
        scores = {k: sum(responses.get(qid, 3) for qid in qs) for k, qs in ENNEAGRAM_TYPES.items()}
        print("🔍 Enneagram Scores:", scores)
        top = max(scores.items(), key=lambda x: x[1])[0]
        return f"{top} - dominant"

    return {
        "mbti": calculate_mbti(),
        "disc": calculate_disc(),
        "eneagrama": calculate_enneagram()
    }

def generate_report_via_ai(grouped_responses: dict, perfil_antigos: list = None) -> dict:
    try:
        from openai import OpenAI
        responses_dict = {q['question_id']: q['answer'] for typ in grouped_responses.values() for q in typ}
        
        profile = generate_profile_key(responses_dict)
        nome = session.get("user_name", "you")
        
        # Novo: histórico resumido
        resumo_historico = ""
        if perfil_antigos:
            resumo_historico = "\n\nPerfis Anteriores:\n"
            for idx, antigo in enumerate(perfil_antigos[-6:], 1):  # últimos 6
                resumo_historico += f"- Previous Profile {idx}: MBTI {antigo.get('mbti')}, DISC {antigo.get('disc')}, Enneagram {antigo.get('eneagrama')}\n"

        prompt = f"""
        {resumo_historico}
        
        {generate_behavior_prompt(profile, nome)}
        """.strip()

        # 🔥 NOVO: Salvar o prompt em arquivo para auditoria
        try:
            with open("prompt_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write("\n\n--- Prompt gerado em nova sessão ---\n")
                log_file.write(prompt)
                log_file.write("\n\n-----------------------------------\n")
        except Exception as e:
            current_app.logger.error(f"[LOG ERROR] Failed to save prompt: {e}")

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI-powered behavioral analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        generated_text = response.choices[0].message.content.strip()
        texto = generated_text  # ✅ Correto

        # 🔍 Extrair os pontos 10 e 11 do texto gerado pela IA
        inicio_10 = texto.find("10. HISTORICAL EVOLUTION INSIGHTS")
        inicio_11 = texto.find("11. ACTION PLAN – NEXT 30 DAYS")

        if inicio_10 != -1 and inicio_11 != -1:
            trecho_evolucao = texto[inicio_10:inicio_11].strip()
            trecho_acao = texto[inicio_11:].strip()
            summary = f"{trecho_evolucao}\n\n{trecho_acao}"
        else:
            summary = texto[:800]  # fallback se o texto estiver mal formatado

        # ✅ Agora sim: retorno final completo
        return {
            "texto": generated_text,
            "tipos": profile,
            "resumo": summary
        }

    except Exception as e:
        current_app.logger.error(f"[AI ERROR] Failed to generate report via AI: {e}")
        return {
            "erro": str(e),
            "texto": "Sorry, we couldn’t generate your report at this time.",
            "tipos": {}
        }
