from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from app.config import Config

import logging
import smtplib

# Initialize global extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Register API blueprints
    from app.routes import responses, questions, report
    app.register_blueprint(responses.responses_bp, url_prefix="/api")
    app.register_blueprint(questions.questions_bp, url_prefix="/api")
    app.register_blueprint(report.report_bp, url_prefix="/api")

    # Register UI blueprints
    from app.routes.web import auth_views
    app.register_blueprint(auth_views)

    from app.routes.user import user_bp
    app.register_blueprint(user_bp)

    from app.routes.contato import contato_views
    app.register_blueprint(contato_views)

    # ✅ Register payment blueprint
    from app.routes.payment import payment_bp
    app.register_blueprint(payment_bp)

    # ✅ Register Stripe webhook blueprint
    from app.routes.stripe_webhook import webhook_bp
    app.register_blueprint(webhook_bp)

    # ✅ Register Vocational Test blueprint
    from app.routes.vocacional import vocacional_bp
    app.register_blueprint(vocacional_bp)

    # DEBUG SMTP (only if FLASK_DEBUG=1)
    if app.config.get("DEBUG", False):
        mail_logger = logging.getLogger("smtplib")
        mail_logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        mail_logger.addHandler(console_handler)

        smtplib.SMTP.debuglevel = 1

    return app

# Optional local execution
if __name__ == "__main__":
    from app.services.perfil_service import gerar_prompt_perfil_comportamental

    perfil = {
        "mbti": "INFJ",
        "disc": "DC",
        "eneagrama": "4w5 - sexual"
    }

    prompt = gerar_prompt_perfil_comportamental(perfil)
    print("\n📄 Generated behavioral profile prompt:\n")
    print(prompt)
