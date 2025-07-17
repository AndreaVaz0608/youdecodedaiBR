import os
import openai
import logging

# ✅ Prompt builder com estrutura EXATA e espaçamento corrigido
def generate_behavior_prompt(profile_combination: dict, name: str = "você") -> str:
    mbti = profile_combination.get("mbti")
    disc = profile_combination.get("disc")
    enneagram = profile_combination.get("eneagrama")

    prompt = f"""
Você é um(a) analista comportamental com profundo conhecimento em MBTI, DISC e Eneagrama. Sua tarefa é gerar um relatório detalhado, estruturado e altamente personalizado com base na seguinte combinação de perfis:

- MBTI: {mbti}
- DISC: {disc}
- Eneagrama: {enneagram}

Use a estrutura abaixo com os títulos de seção e emojis exatamente como apresentado. Seja empático(a), perspicaz, humano(a) e direto(a). Evite clichês e repetições. Escreva em um tom conversacional, inspirador e acessível.

🌟 1. INTRODUÇÃO PERSONALIZADA  
Bem-vindo(a), {name}! Este relatório personalizado foi criado para oferecer insights profundos sobre seu comportamento, motivações e estilo de tomada de decisão. Utilizando as teorias do MBTI, DISC e do Eneagrama, ele é uma exploração sobre quem você é e como se relaciona com o mundo. Esperamos que isso o(a) motive a usar seus pontos fortes, reconhecer seus pontos cegos e crescer pessoal e profissionalmente.

🎯 2. SEU PERFIL EM UMA FRASE PODEROSA  
(Resuma a essência dessa personalidade em uma frase impactante e precisa.)

🔍 3. SUA PERSONALIDADE EM PROFUNDIDADE

🧠 Como Você Pensa (MBTI – {mbti})  
(Descreva como a pessoa processa informações, toma decisões e organiza ideias.)

⚡ Como Você Age e Interage (DISC – {disc})  
(Descreva o estilo de ação, comunicação e influência.)

❤️ Seus Motivadores Internos (Eneagrama Tipo {enneagram})  
(Destaque motivações principais, valores e tendências emocionais.)

🚀 4. SEUS PONTOS FORTES ÚNICOS  
(Listar talentos principais, comportamentos naturais e qualidades marcantes.)

⚠️ 5. PONTOS DE ATENÇÃO  
(Listar desafios potenciais, padrões rígidos ou comportamentos que exigem atenção.)

💡 6. DICAS PRÁTICAS PARA EVOLUIR  
(Compartilhe conselhos práticos que ajudem na jornada de crescimento.)

🔮 7. SEU POTENCIAL DE FUTURO  
(Pinte um quadro inspirador sobre o que a pessoa pode alcançar ao viver seu melhor potencial.)

🙌 8. ENCERRAMENTO INSPIRADOR  
(Encerre com palavras motivadoras e incentivo ao autodesenvolvimento.)

No final, inclua isso com formatação em negrito (markdown):

**Perfis Identificados**  
• MBTI: {mbti}  
• DISC: {disc}  
• Eneagrama: {enneagram}
"""
    return prompt.strip()


# ✅ Função principal de geração do relatório
def generate_behavioral_report(mbti: str, disc: str, enneagram: str, name: str = "você") -> tuple:
    logging.warning("⚠️ [DEPRECATED] generate_behavioral_report() está obsoleta. Use perfil_service.py como fonte única de verdade.")
    
    profile_combination = {
        "mbti": mbti,
        "disc": disc,
        "eneagrama": enneagram
    }
    prompt = generate_behavior_prompt(profile_combination, name)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY não está configurada nas variáveis de ambiente.")

    openai.api_key = api_key

    try:
        logging.info(f"[generate_behavioral_report] Prompt:\n{prompt}")

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um(a) especialista em análise comportamental."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=1600
        )

        result = response["choices"][0]["message"]["content"]
        logging.info(f"[generate_behavioral_report] Resultado:\n{result}")
        return prompt, result

    except Exception as e:
        logging.error(f"[generate_behavioral_report] Erro ao chamar a OpenAI: {str(e)}")
        raise Exception(f"Erro ao chamar a OpenAI: {str(e)}")
