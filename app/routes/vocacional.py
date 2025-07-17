from flask import Blueprint, render_template, session, redirect, flash, url_for, request
from app.main import db
from app.models import VocationalSession, VocationalResponse
from datetime import datetime
from openai import OpenAI
import os
from flask import current_app, make_response
import pdfkit

vocacional_bp = Blueprint('vocacional', __name__)

@vocacional_bp.route('/vocational-test', methods=['GET'])
def vocational_test_view():
    if 'user_id' not in session:
        flash("Por favor, faça login para acessar o teste vocacional.", "error")
        return redirect(url_for('auth_views.login_view'))

    questions = [
        {
            "id": 1001,
            "text": "Ao aprender algo novo, o que mais te atrai?",
            "options": [
                "Entender a lógica por trás.",
                "Resolver um problema real.",
                "Ajudar outras pessoas com o que aprendeu.",
                "Criar algo único a partir disso."
            ]
        },
        {
            "id": 1002,
            "text": "Qual dessas atividades você faria por horas, mesmo sem receber por isso?",
            "options": [
                "Analisar dados ou sistemas.",
                "Criar conteúdo artístico ou visual.",
                "Ensinar ou orientar outras pessoas.",
                "Organizar e planejar projetos."
            ]
        },
        {
            "id": 1003,
            "text": "O que mais te frustra em um ambiente de trabalho?",
            "options": [
                "Falta de liberdade para inovar.",
                "Falta de propósito no que é feito.",
                "Excesso de regras e rigidez.",
                "Falta de reconhecimento."
            ]
        },
        {
            "id": 1004,
            "text": "Como você prefere trabalhar?",
            "options": [
                "Com autonomia e horários flexíveis.",
                "Em equipe, trocando ideias constantemente.",
                "Com metas claras e previsibilidade.",
                "Em ambientes dinâmicos e desafiadores."
            ]
        },
        {
            "id": 1005,
            "text": "Quando imagina seu futuro ideal, o que vem à sua mente?",
            "options": [
                "Causar um impacto positivo no mundo.",
                "Ser reconhecido(a) como referência na sua área.",
                "Ter estabilidade e segurança.",
                "Ter controle do seu tempo e decisões."
            ]
        },
        {
            "id": 1006,
            "text": "O que as pessoas costumam dizer sobre você?",
            "options": [
                "Que você é muito analítico(a).",
                "Que você é criativo(a) e original.",
                "Que você é bom(boa) ouvinte e prestativo(a).",
                "Que você é confiável e eficiente."
            ]
        },
        {
            "id": 1007,
            "text": "Qual frase melhor reflete sua visão de sucesso?",
            "options": [
                "Fazer o que amo e ser bem pago(a) por isso.",
                "Ajudar pessoas por meio do meu trabalho.",
                "Construir algo que dure além de mim.",
                "Alcançar independência financeira e pessoal."
            ]
        },
        {
            "id": 1008,
            "text": "Em que tipo de tarefa você costuma se destacar?",
            "options": [
                "Resolver problemas complexos.",
                "Comunicar ideias de forma envolvente.",
                "Apoiar emocionalmente outras pessoas.",
                "Estruturar processos e manter a ordem."
            ]
        },
        {
            "id": 1009,
            "text": "Se pudesse escolher agora, o que gostaria de desenvolver em si?",
            "options": [
                "Habilidades empreendedoras.",
                "Liderança e comunicação.",
                "Profundidade técnica.",
                "Inteligência emocional."
            ]
        },
        {
            "id": 1010,
            "text": "Com qual dessas áreas você mais se identifica?",
            "options": [
                "Tecnologia, dados, exatas.",
                "Artes, comunicação, design.",
                "Saúde, educação, impacto social.",
                "Negócios, gestão, operações."
            ]
        },
        {
            "id": 1011,
            "text": "O que mais te motiva na escolha de uma carreira?",
            "options": [
                "Resolver grandes desafios.",
                "Expressar minha identidade.",
                "Contribuir com o bem-estar das pessoas.",
                "Ter um caminho sólido e respeitado."
            ]
        },
        {
            "id": 1012,
            "text": "Como você lida com regras e estrutura?",
            "options": [
                "Prefiro total liberdade.",
                "Sigo regras, mas adapto quando necessário.",
                "Prefiro ambientes estruturados e organizados.",
                "Depende do propósito por trás das regras."
            ]
        },
        {
            "id": 1013,
            "text": "Se ganhasse na loteria hoje, o que faria depois de viajar?",
            "options": [
                "Abriria meu próprio negócio.",
                "Investiria em projetos criativos.",
                "Ajudaria pessoas a se desenvolverem.",
                "Estudaria algo que sempre sonhei."
            ]
        },
        {
            "id": 1014,
            "text": "Quando você se sente mais realizado(a) profissionalmente?",
            "options": [
                "Ao resolver um desafio técnico.",
                "Ao criar algo que não existia.",
                "Ao ver alguém crescer com sua ajuda.",
                "Ao concluir algo com excelência e organização."
            ]
        },
        {
            "id": 1015,
            "text": "Qual dessas frases mais combina com você?",
            "options": [
                "“Sou bom(boa) em resolver problemas.”",
                "“Me expresso com facilidade.”",
                "“As pessoas confiam em mim para conselhos.”",
                "“Organizo tudo com eficiência.”"
            ]
        }
    ]

    return render_template('vocacional_test.html', questions=questions)


@vocacional_bp.route('/submit-vocational', methods=['POST'])
def submit_vocational():
    if 'user_id' not in session:
        flash("Sessão expirada. Faça login novamente.", "error")
        return redirect(url_for('auth_views.login_view'))

    user_id = session['user_id']
    form_data = request.form

    session_obj = VocationalSession(user_id=user_id)
    db.session.add(session_obj)
    db.session.commit()

    respostas = []
    for key, value in form_data.items():
        if key.startswith("question_"):
            q_id = int(key.split("_")[1])
            resposta = VocationalResponse(
                session_id=session_obj.id,
                question_id=q_id,
                answer=value
            )
            respostas.append(resposta)

    db.session.bulk_save_objects(respostas)
    db.session.commit()

    flash("Seu teste vocacional foi enviado com sucesso!", "success")
    return redirect(url_for('vocacional.vocational_result_view', session_id=session_obj.id))


@vocacional_bp.route('/vocational-result/<int:session_id>', methods=['GET'])
def vocational_result_view(session_id):
    if 'user_id' not in session:
        flash("Por favor, faça login para visualizar o resultado.", "error")
        return redirect(url_for('auth_views.login_view'))

    session_obj = VocationalSession.query.get(session_id)
    if not session_obj or session_obj.user_id != session['user_id']:
        flash("Sessão não encontrada ou acesso não autorizado.", "error")
        return redirect(url_for('auth_views.dashboard'))

    respostas = VocationalResponse.query.filter_by(session_id=session_id).all()
    nome = session.get('user_name', 'Usuário')
    respostas_texto = "\n".join([f"Q{r.question_id}: {r.answer}" for r in respostas])

    prompt = f"""
Você é uma IA especialista em orientação vocacional. Um(a) usuário(a) chamado(a) {nome} acaba de responder um teste com 15 questões.  
Abaixo estão as respostas fornecidas:

{respostas_texto}

Com base nessas respostas, gere um relatório vocacional conciso com:
- Destaques sobre os maiores talentos do(a) usuário(a).
- Sugestão de 2 a 3 possíveis caminhos de carreira.
- Tom acolhedor, direto e inspirador.
- Limite de até 300 palavras.
"""

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é uma IA especialista em orientação vocacional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        texto_ia = completion.choices[0].message.content.strip()
        session_obj.ai_result = texto_ia
        db.session.commit()

    except Exception as e:
        current_app.logger.error(f"[VOCACIONAL IA ERROR] {e}")
        texto_ia = "⚠️ Ocorreu um erro ao gerar seu relatório. Por favor, tente novamente mais tarde."

    return render_template("vocacional_resultado.html", resultado=texto_ia, session_id=session_id)


@vocacional_bp.route('/vocacional/pdf/<int:session_id>')
def vocacional_pdf(session_id):
    if 'user_id' not in session:
        flash("Você precisa estar logado para baixar o PDF.", "error")
        return redirect(url_for('auth_views.login_view'))

    session_obj = VocationalSession.query.get(session_id)

    if not session_obj or session_obj.user_id != session['user_id']:
        flash("Acesso não autorizado.", "error")
        return redirect(url_for('auth_views.dashboard'))

    respostas = VocationalResponse.query.filter_by(session_id=session_id).all()
    nome = session.get("user_name", "Usuário")
    resultado = session_obj.ai_result or "Nenhum resultado disponível."

    html = render_template("vocacional_resultado.html", resultado=resultado, nome=nome, pdf_mode=True)

    try:
        config = pdfkit.configuration()
        options = {
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'quiet': ''
        }

        pdf = pdfkit.from_string(html, False, configuration=config, options=options)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_vocacional_{session_id}.pdf'
        return response

    except Exception as e:
        current_app.logger.error(f"[PDF ERROR] Falha ao gerar PDF vocacional: {e}")
        flash("Ocorreu um erro ao gerar o PDF.", "danger")
        return redirect(url_for('vocacional.vocational_result_view', session_id=session_id))
