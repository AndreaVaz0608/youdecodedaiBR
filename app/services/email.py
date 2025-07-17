from flask_mail import Message
from flask import render_template, current_app
from app.main import mail


def enviar_email_boas_vindas(user):
    try:
        msg = Message(
            subject="Bem-vindo(a) ao YouDecoded.AI ✨",
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        msg.html = render_template("emails/welcome.html", nome=user.name)
        mail.send(msg)
        current_app.logger.info(f"✅ E-mail de boas-vindas enviado para {user.email}")
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao enviar e-mail de boas-vindas para {user.email}: {e}")


def enviar_email_relatorio(user, sessao_id, perfil):
    try:
        link_relatorio = f"https://youdecoded-ai.onrender.com/gerar-relatorio?sessao_id={sessao_id}"

        msg = Message(
            subject="🧠 Seu Relatório de Personalidade com IA está pronto!",
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        msg.html = render_template(
            "emails/report_email.html",
            nome=user.name,
            mbti=perfil.get("mbti", "N/A"),
            disc=perfil.get("disc", "N/A"),
            eneagrama=perfil.get("eneagrama", "N/A"),
            link=link_relatorio
        )

        mail.send(msg)
        current_app.logger.info(f"✅ E-mail de relatório enviado para {user.email}")
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao enviar e-mail de relatório para {user.email}: {e}")


def send_recovery_email(recipient_email, reset_token):
    try:
        reset_link = f"https://youdecoded-ai.onrender.com/reset-password?token={reset_token}"

        msg = Message(
            subject="🔒 Instruções para Recuperar sua Senha • YouDecoded.AI",
            recipients=[recipient_email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        msg.html = f"""
        <h2>Olá!</h2>
        <p>Recebemos uma solicitação para redefinir sua senha no YouDecoded.AI.</p>
        <p>Clique no link abaixo para criar uma nova senha:</p>
        <p><a href="{reset_link}" style="color: #d4af37; font-weight: bold;">Redefinir minha senha</a></p>
        <br>
        <p>Se você não solicitou essa recuperação, por favor ignore esta mensagem.</p>
        <p>Obrigado,<br>Equipe YouDecoded.AI</p>
        """

        mail.send(msg)
        current_app.logger.info(f"✅ E-mail de recuperação enviado para {recipient_email}")
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao enviar e-mail de recuperação para {recipient_email}: {e}")
