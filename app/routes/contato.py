from flask import Blueprint, render_template, request, flash, current_app
from flask_mail import Message
from app.main import mail  # ✅ correto

contato_views = Blueprint('contato', __name__)

@contato_views.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('name')
        email = request.form.get('email')
        mensagem = request.form.get('message')

        try:
            msg = Message(
                subject="Novo Contato - YouDecoded.AI",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],  # ✅ pego do .env
                recipients=["youdecoded.ai@youdecodedai.online"],
                body=f"📩 Novo contato recebido pelo YouDecoded.AI:\n\n"
                     f"Nome: {nome}\n"
                     f"E-mail: {email}\n\n"
                     f"Mensagem:\n{mensagem}"
            )

            mail.send(msg)
            return render_template('contato.html', success=True)

        except Exception as e:
            print("Erro ao enviar e-mail:", e)
            flash("Ops! Algo deu errado. Por favor, tente novamente mais tarde.", "error")

    return render_template('contato.html')
