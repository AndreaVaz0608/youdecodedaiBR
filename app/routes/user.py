from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from app.main import db
from app.models import User, Question, Response, TestSession
from app.services.perfil_service import generate_report_via_ai
import pdfkit
from datetime import datetime
import logging
import threading
import time
from flask import current_app
from app.services.email import enviar_email_relatorio
import os
from app.models import AISnapshot

user_bp = Blueprint('user', __name__)

@user_bp.route('/testar', methods=['GET'])
def assessment_view():
    if 'user_id' not in session:
        flash("Please log in to access the test.", "error")
        return redirect(url_for('auth_views.login_view'))

    user = User.query.get(session['user_id'])

    if not user.is_admin and user.plan not in ['Premium', 'Pro']:
        flash("Access restricted to Premium and Pro users.", "warning")
        return redirect(url_for('user.select_product'))

    if not user.is_admin:
        if user.plan == 'Pro':
            now = datetime.now()
            existing_test = TestSession.query.filter_by(user_id=user.id).filter(
                db.extract('year', TestSession.created_at) == now.year,
                db.extract('month', TestSession.created_at) == now.month
            ).first()

            if existing_test:
                flash("⚠️ As a Pro user, you can take only 1 test per month. Please come back next month!", "warning")
                return redirect(url_for('auth_views.dashboard'))

        elif user.plan == 'Premium':
            existing_test = TestSession.query.filter_by(user_id=user.id).first()
            if existing_test:
                flash("⚠️ As a Premium user, you can only take the test once. Upgrade to Pro for more!", "warning")
                return redirect(url_for('auth_views.dashboard'))

    questions = Question.query.order_by(Question.id).all()
    if not questions:
        flash("The test is not available yet. We're updating the questions!", "warning")
        return redirect(url_for('user.select_product'))

    respostas_salvas = {}
    ultima_sessao = TestSession.query.filter_by(user_id=user.id, ai_result=None).order_by(TestSession.created_at.desc()).first()
    if ultima_sessao:
        respostas = Response.query.filter_by(session_id=ultima_sessao.id, user_id=user.id).all()
        for r in respostas:
            respostas_salvas[r.question_id] = r.answer

    return render_template('assessment.html', questions=questions, respostas_salvas=respostas_salvas)

@user_bp.route('/submit-responses', methods=['POST'])
def submit_responses():
    if 'user_id' not in session:
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for('auth_views.login_view'))

    user_id = session['user_id']
    form_data = request.form

    test_session = TestSession(user_id=user_id)
    db.session.add(test_session)
    db.session.commit()

    respostas = []
    for key, value in form_data.items():
        if key.startswith("response_"):
            q_id = int(key.split("_")[1])
            answer = int(value)
            respostas.append(Response(
                user_id=user_id,
                question_id=q_id,
                session_id=test_session.id,
                answer=answer
            ))

    db.session.bulk_save_objects(respostas)
    db.session.commit()
    session.modified = True

    return redirect(url_for('user.processando_relatorio', sessao_id=test_session.id))

@user_bp.route('/processando-relatorio')
def processando_relatorio():
    if 'user_id' not in session:
        flash("Please log in to view your report.", "error")
        return redirect(url_for('auth_views.login_view'))

    sessao_id = request.args.get('sessao_id')

    def gerar_relatorio_background(sessao_id):
        from app.main import app  # <-- IMPORTANTE: agora está indentado!

        try:
            with app.app_context():  # Garante contexto Flask na thread
                sessao = TestSession.query.get(int(sessao_id))
                user = User.query.get(sessao.user_id)
                user_name = user.name

                respostas = (
                    db.session
                      .query(Response, Question)
                      .join(Question)
                      .filter(Response.session_id == sessao.id)
                      .all()
                )

                agrupado = {"MBTI": [], "DISC": [], "Eneagrama": []}
                for resposta, pergunta in respostas:
                    agrupado[pergunta.type].append({
                        "question_id": pergunta.id,
                        "answer": resposta.answer
                    })

                perfil_antigos = []
                if user.plan == "Pro":
                    sessoes_anteriores = (
                        TestSession.query
                                   .filter(
                                       TestSession.user_id == user.id,
                                       TestSession.id != sessao.id,
                                       TestSession.ai_result.isnot(None)
                                   )
                                   .order_by(TestSession.created_at.desc())
                                   .limit(6)
                                   .all()
                    )
                    for sessao_antiga in sessoes_anteriores:
                        perfil_antigos.append({
                            "mbti": sessao_antiga.mbti_result,
                            "disc": sessao_antiga.disc_result,
                            "eneagrama": sessao_antiga.eneagrama_result
                        })

                resultado = generate_report_via_ai(
                    agrupado,
                    perfil_antigos=perfil_antigos if perfil_antigos else None
                )

                if not resultado.get("erro"):
                    sessao.ai_result       = resultado["texto"]
                    sessao.mbti_result     = resultado["tipos"].get("mbti")
                    sessao.disc_result     = resultado["tipos"].get("disc")
                    sessao.eneagrama_result= resultado["tipos"].get("eneagrama")
                    db.session.commit()

                time.sleep(5)

        except Exception as e:
            # Agora pode usar current_app.logger.error normalmente
            current_app.logger.error(f"[BACKGROUND ERROR] {e}")

    threading.Thread(
        target=gerar_relatorio_background,
        args=(sessao_id,),
        daemon=True
    ).start()

    return render_template("carregando.html", sessao_id=sessao_id)

# Report screen
@user_bp.route('/gerar-relatorio')
def gerar_relatorio():
    if 'user_id' not in session:
        flash("You need to log in to view the report.", "error")
        return redirect(url_for('auth_views.login_view'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    user_name = session.get('user_name', 'User')
    sessao_id = request.args.get('sessao_id')

    if sessao_id:
        sessao = TestSession.query.filter_by(id=sessao_id, user_id=user_id).first()
    else:
        sessao = TestSession.query.filter_by(user_id=user_id).order_by(TestSession.created_at.desc()).first()

    if not sessao:
        flash("No session found.", "warning")
        return redirect(url_for('user.assessment_view'))

    respostas = db.session.query(Response, Question).join(Question).filter(Response.session_id == sessao.id).all()

    agrupado = {"MBTI": [], "DISC": [], "Eneagrama": []}
    for resposta, pergunta in respostas:
        agrupado[pergunta.type].append({
            "question_id": pergunta.id,
            "answer": resposta.answer
        })

    logging.info(f"[DEBUG] User {user_id} - Perfil agrupado para IA: {agrupado}")

    # ✅ Verifica se já existe resposta salva no banco
    if sessao.ai_result:
        resultado = {
            "texto": sessao.ai_result,
            "tipos": {
                "mbti": sessao.mbti_result or "N/A",
                "disc": sessao.disc_result or "N/A",
                "eneagrama": sessao.eneagrama_result or "N/A"
            }
        }

    else:
        resultado = generate_report_via_ai(agrupado)

    if not resultado.get("erro"):
        sessao.ai_result = resultado["texto"]
        sessao.mbti_result = resultado["tipos"].get("mbti")
        sessao.disc_result = resultado["tipos"].get("disc")
        sessao.eneagrama_result = resultado["tipos"].get("eneagrama")
        db.session.commit()
    
            # 🧠 Salvar snapshot no banco (somente para usuários Pro)
        if user.plan == "Pro":
            try:
                resumo_ia = resultado.get("resumo", "")[:1200]  # Limita a 1200 caracteres

                novo_snapshot = AISnapshot(
                    user_id=user.id,
                    session_id=sessao.id,
                    summary=resumo_ia,
                    mbti=resultado["tipos"].get("mbti"),
                    disc=resultado["tipos"].get("disc"),
                    eneagrama=resultado["tipos"].get("eneagrama")
                )

                db.session.add(novo_snapshot)
                db.session.commit()

                # 🔁 Manter só os 6 mais recentes
                snapshots = AISnapshot.query.filter_by(user_id=user.id).order_by(AISnapshot.created_at.desc()).all()
                if len(snapshots) > 6:
                    for s in snapshots[6:]:
                        db.session.delete(s)
                    db.session.commit()

            except Exception as e:
                current_app.logger.error(f"[SNAPSHOT ERROR] Falha ao salvar resumo da IA: {e}")

    erro_ia = resultado.get("erro")
    if erro_ia:
        flash("⚠️ An error occurred generating the AI report.", "danger")
        logging.error(f"[USER FLOW] Report generation error: {erro_ia}")

    return render_template("relatorio.html",
                           nome=user_name,
                           respostas=agrupado,
                           resultado=resultado,
                           sessao_id=sessao.id)

# Export report as PDF
@user_bp.route('/relatorio/pdf')
def relatorio_pdf():
    if 'user_id' not in session:
        flash("You must be logged in to download the PDF.", "error")
        return redirect(url_for('auth_views.login_view'))

    user = User.query.get(session['user_id'])
    if user.plan not in ['Premium', 'Pro']:
        flash("Only Premium and Pro users can download the full report.", "warning")
        return redirect(url_for('user.select_product'))

    user_id = user.id
    user_name = session.get('user_name', 'User')
    sessao_id = request.args.get('sessao_id')

    sessao = TestSession.query.filter_by(id=sessao_id, user_id=user_id).first() if sessao_id else \
             TestSession.query.filter_by(user_id=user_id).order_by(TestSession.created_at.desc()).first()

    if not sessao:
        flash("No session found to generate the PDF.", "warning")
        return redirect(url_for('user.assessment_view'))

    respostas = db.session.query(Response, Question).join(Question).filter(Response.session_id == sessao.id).all()
    agrupado = {"MBTI": [], "DISC": [], "Eneagrama": []}
    for resposta, pergunta in respostas:
        agrupado[pergunta.type].append({
            "question_id": pergunta.id,
            "answer": resposta.answer
        })

    if sessao.ai_result:
        resultado = {
            "texto": sessao.ai_result,
            "tipos": {
                "mbti": sessao.mbti_result or "N/A",
                "disc": sessao.disc_result or "N/A",
                "eneagrama": sessao.eneagrama_result or "N/A"
            }
        }
    else:
        resultado = generate_report_via_ai(agrupado)
        if not resultado.get("erro"):
            sessao.ai_result = resultado["texto"]
            sessao.mbti_result = resultado["tipos"].get("mbti")
            sessao.disc_result = resultado["tipos"].get("disc")
            sessao.eneagrama_result = resultado["tipos"].get("eneagrama")
            db.session.commit()
        else:
            flash("AI failed to generate the report. Please try again later.", "error")
            return redirect(url_for('user.assessment_view'))

    try:
        html = render_template(
            "relatorio.html",
            nome=user_name,
            respostas=agrupado,
            resultado=resultado,
            sessao_id=sessao.id
        )

        # Configuração padrão sem caminho customizado
        config = pdfkit.configuration()  # tenta usar o wkhtmltopdf padrão do sistema
        options = {
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'quiet': ''
        }

        pdf = pdfkit.from_string(html, False, configuration=config, options=options)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=report_{sessao.id}.pdf'
        return response

    except Exception as e:
        current_app.logger.error(f"[PDF ERROR] Failed to generate PDF: {e}")
        flash("An error occurred while generating the PDF report.", "danger")
        return redirect(url_for('user.assessment_view'))

# History of sessions
@user_bp.route('/historico')
def historico_view():
    if 'user_id' not in session:
        flash("Please log in to view your history.", "error")
        return redirect(url_for('auth_views.login_view'))

    user = User.query.get(session['user_id'])
    if user.plan != 'Pro':
        flash("Access restricted to Pro users.", "warning")
        return redirect(url_for('user.select_product'))

    sessoes = TestSession.query.filter_by(user_id=user.id).order_by(TestSession.created_at.desc()).all()
    return render_template('historico.html', sessoes=sessoes)

@user_bp.route('/products', methods=['GET', 'POST'])
def select_product():
    if request.method == 'POST':
        selected_package = request.form.get('package')
        session['selected_package'] = selected_package
        flash(f"You selected the {selected_package} package!", "success")

        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                # 🔄 Atualiza o plano no banco
                user.plan = selected_package
                db.session.commit()
                session['user_plan'] = selected_package  # opcional, para uso no frontend

                # ➜ Redirecionamento conforme plano
                if selected_package == "Premium":
                    return redirect(url_for('user.assessment_view'))

                elif selected_package == "Pro":
                    # Se já houver sessões anteriores, manda para o dashboard
                    previous_sessions = (
                        TestSession.query
                                   .filter_by(user_id=user.id)
                                   .first()
                    )
                    if previous_sessions:
                        return redirect(url_for('auth_views.dashboard'))
                    else:
                        return redirect(url_for('user.assessment_view'))

                else:  # Qualquer outro plano (ex.: Free)
                    flash("Upgrade to Premium or Pro to take the full assessment!", "warning")
                    return redirect(url_for('auth_views.dashboard'))

        # Fallback se não houver sessão
        return redirect(url_for('auth_views.login_view'))

    return render_template('products.html')

# Editar perfil
@user_bp.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, faça login para acessar seu perfil.", "error")
        return redirect(url_for('auth_views.login_view'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email:
            flash("Nome e e-mail são obrigatórios.", "error")
            return redirect(url_for('user.editar_perfil'))

        # ▸ Atualiza dados
        user.name = name
        user.email = email
        if password:
            user.set_password(password)

        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        session['user_name'] = name

        # ▸ Redireciona de acordo com o plano
        if user.plan == "Pro":
            return redirect(url_for('auth_views.dashboard'))
        else:  # Premium ou outro plano que dê direito ao teste
            return redirect(url_for('user.assessment_view'))

    return render_template('perfil.html', user=user)

@user_bp.route('/sucesso')
def pagamento_sucesso():
    if 'user_id' not in session:
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for('auth_views.login_view'))

    # ▸ Identifica o plano adquirido via Stripe
    plano = request.args.get('plano', 'premium').lower()
    user  = User.query.get(session['user_id'])

    if plano == 'pro':
        user.plan = "Pro"
        next_url = url_for('auth_views.dashboard')

    elif plano == 'premium':
        user.plan = "Premium"
        next_url = url_for('user.assessment_view')

    else:
        # Plano inesperado ou erro de callback
        flash("Plano inválido ou expirado. Escolha um pacote para continuar.", "warning")
        next_url = url_for('user.select_product')

    db.session.commit()
    session['user_plan'] = user.plan  # mantém em sessão para uso no frontend

    return render_template("pagamento_sucesso.html",
                           user_name=user.name,
                           next_url=next_url)

@user_bp.route('/coaching', methods=['POST'])
def pergunta_ia():
    if 'user_id' not in session:
        return {"erro": "Você não está logado(a)."}, 401

    user = User.query.get(session['user_id'])
    if user.plan != 'Pro':
        return {"erro": "Acesso restrito aos usuários Pro."}, 403

    pergunta = request.form.get("pergunta", "").strip()
    if not pergunta:
        return {"erro": "Pergunta vazia."}, 400

    # Buscar a última sessão válida com resultados
    ultima_sessao = (
        TestSession.query
        .filter_by(user_id=user.id)
        .filter(TestSession.ai_result.isnot(None))
        .order_by(TestSession.created_at.desc())
        .first()
    )

    mbti = ultima_sessao.mbti_result if ultima_sessao else "N/A"
    disc = ultima_sessao.disc_result if ultima_sessao else "N/A"
    eneagrama = ultima_sessao.eneagrama_result if ultima_sessao else "N/A"

    prompt = f"""
Você é uma inteligência artificial coach, empática e prática, especializada em desenvolvimento pessoal e carreira.
O(a) usuário(a) tem o seguinte perfil comportamental:
- MBTI: {mbti}
- DISC: {disc}
- Eneagrama: {eneagrama}

A pergunta feita foi:
\"{pergunta}\"

Responda de forma prática, inspiradora, emocionalmente inteligente e adequada ao perfil da pessoa.
Mantenha a resposta com menos de 300 palavras.
"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é uma assistente de coaching sábia, empática e eficaz."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75,
            max_tokens=500
        )
        texto = response.choices[0].message.content.strip()
        return {"resposta": texto}

    except Exception as e:
        current_app.logger.error(f"[COACHING AI ERROR] {e}")
        return {"erro": "Erro interno ao processar a resposta."}, 500
