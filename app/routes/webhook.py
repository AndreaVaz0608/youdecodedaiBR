# app/routes/webhook.py

from flask import Blueprint, request, jsonify
from app.main import db
from app.models import User
import stripe
import os

webhook_bp = Blueprint('webhook', __name__)

# Carrega a chave secreta do webhook do Stripe do ambiente
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@webhook_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', None)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Payload inválido
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Assinatura inválida
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')
        if not customer_email:
            return jsonify({'error': 'No customer email'}), 400

        user = User.query.filter_by(email=customer_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Atualiza o plano do usuário para "Pro"
        user.plan = "Pro"
        db.session.commit()

        return jsonify({'message': 'Plano atualizado para Pro com sucesso'}), 200

    return jsonify({'message': 'Evento ignorado'}), 200
