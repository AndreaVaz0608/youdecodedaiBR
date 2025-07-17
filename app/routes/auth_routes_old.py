from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.main import db
from app.models import User
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from app.services.email import enviar_email_boas_vindas  # ✅ NOVO import correto

auth_views_bp = Blueprint('auth_views', __name__)

@auth_views_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            session['user_id'] = user.id
            session['token'] = access_token
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('user.assessment_view'))
        flash('E-mail ou senha inválidos.', 'danger')
    return render_template('login.html')

@auth_views_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        accepted_terms = request.form.get("accepted_terms")

        if not accepted_terms:
            flash("Você precisa aceitar os termos de uso para continuar.", "danger")
            return redirect(url_for('auth_views.register_view'))

        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'warning')
            return redirect(url_for('auth_views.register_view'))

        user = User(email=email, name=name, accepted_terms=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        # ✅ Depuração: saber se o envio de e-mail está sendo executado
        print("⚠️ Vai tentar enviar o e-mail agora...")  # 👈 antes da função
        enviar_email_boas_vindas(user)
        print("✅ Linha de envio passou!")               # 👈 depois da função

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('user.assessment_view'))

    return render_template('register.html')

@auth_views_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth_views.login_view'))

@auth_views_bp.route('/forgot-password')
def forgot_password():
    flash('Funcionalidade de recuperação de senha em breve.', 'info')
    return redirect(url_for('auth_views.login_view'))

@auth_views_bp.route('/termos', endpoint='termos')
def termos():
    return render_template('termos.html')
