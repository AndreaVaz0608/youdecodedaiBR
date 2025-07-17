from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.models import User, TestSession
from app.main import db
import secrets
from app.services.email import enviar_email_boas_vindas, send_recovery_email

auth_views = Blueprint('auth_views', __name__)

# Redirecionar da raiz para o login
@auth_views.route('/')
def home_redirect():
    return redirect(url_for('auth_views.login_view'))

# Página de login
@auth_views.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_plan'] = user.plan
            flash(f"Bem-vindo(a), {user.name.split()[0]}!", "success")

            if user.plan == 'Pro':
                return redirect(url_for('auth_views.dashboard'))
            elif user.plan == 'Premium':
                return redirect(url_for('user.assessment_view'))
            else:
                return redirect(url_for('user.select_product'))

        flash("Credenciais inválidas. Tente novamente.", "error")
        return render_template('login.html')

    return render_template('login.html')

# Página de cadastro
@auth_views.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'POST':
        name  = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        accepted_terms   = request.form.get("accepted_terms")
        accepted_privacy = request.form.get("accepted_privacy")

        # ▸ Validações
        if not accepted_terms or not accepted_privacy:
            flash("Você precisa aceitar os Termos de Uso e a Política de Privacidade para continuar.", "danger")
            return redirect(url_for('auth_views.register_view'))

        if User.query.filter_by(email=email).first():
            flash("Este email já está em uso!", "error")
            return redirect(url_for('auth_views.register_view'))

        # ▸ Cria usuário
        user = User(
            name=name,
            email=email,
            accepted_terms=True,
            accepted_privacy=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # ▸ Inicia sessão
        session['user_id']   = user.id
        session['user_name'] = user.name
        session['user_plan'] = user.plan  # inicialmente None

        # ▸ E‑mail de boas‑vindas (best effort)
        try:
            enviar_email_boas_vindas(user)
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email de boas-vindas: {e}")

        flash(f"Cadastro realizado com sucesso, {name.split()[0]}!", "success")
        # ➜ Novo fluxo: escolher plano (Premium ou Pro)
        return redirect(url_for('user.select_product'))

    return render_template('register.html')

# Esqueci minha senha
@auth_views.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            flash("Informe seu email para continuar.", "warning")
            return redirect(url_for('auth_views.forgot_password'))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email não encontrado. Verifique e tente novamente.", "error")
            return redirect(url_for('auth_views.forgot_password'))

        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        db.session.commit()

        send_recovery_email(user.email, reset_token)

        flash("Enviamos instruções para redefinir sua senha. Verifique seu email!", "success")
        return redirect(url_for('auth_views.login_view'))

    return render_template('forgot_password.html')

# Sair
@auth_views.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da sua conta com sucesso!", "info")
    return redirect(url_for('auth_views.login_view'))

# Dashboard exclusivo para usuários Pro
@auth_views.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Você precisa estar logado(a) para acessar o painel.", "error")
        return redirect(url_for('auth_views.login_view'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    if user.plan != 'Pro':
        flash("O painel está disponível apenas para usuários Pro.", "warning")
        return redirect(url_for('user.select_product'))

    sessoes = (
        TestSession.query
        .filter_by(user_id=user_id)
        .order_by(TestSession.created_at.desc())
        .limit(6)
        .all()
    )

    ultima_sessao = sessoes[0] if sessoes else None
    total = len(sessoes)

    recomendacoes = []
    for sessao in sessoes:
        if sessao.ai_result:
            blocos = sessao.ai_result.split('###')
            for bloco in blocos:
                if bloco.strip().startswith('📝'):
                    recomendacoes.append({
                        'data': sessao.created_at.strftime('%d/%m/%Y'),
                        'mbti': sessao.mbti_result or "N/A",
                        'disc': sessao.disc_result or "N/A",
                        'eneagrama': sessao.eneagrama_result or "N/A",
                        'texto': bloco.strip()
                    })
                    break

    return render_template(
        "dashboard.html",
        nome=user.name,
        email=user.email,
        ultima_sessao=ultima_sessao,
        total=total,
        sessoes=sessoes,
        recomendacoes=recomendacoes,
    )

# Termos de uso
@auth_views.route('/termos')
def termos():
    return render_template('termos.html')

# Política de privacidade
@auth_views.route('/privacy')
def privacy():
    return render_template('privacy.html')

# Redefinir senha
@auth_views.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    if not token:
        flash("Token inválido ou ausente.", "danger")
        return redirect(url_for('auth_views.login_view'))

    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash("Link de redefinição inválido ou expirado.", "danger")
        return redirect(url_for('auth_views.login_view'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash("Preencha todos os campos.", "warning")
            return redirect(request.url)

        if password != confirm_password:
            flash("As senhas não coincidem.", "warning")
            return redirect(request.url)

        user.set_password(password)
        user.reset_token = None
        db.session.commit()

        flash("Senha redefinida com sucesso! Faça login.", "success")
        return redirect(url_for('auth_views.login_view'))

    return render_template('reset_password.html')
