# app/routes/stripe_webhook.py

from flask import Blueprint, request, jsonify
import stripe
import os
from app.main import db
from app.models import User

webhook_bp = Blueprint('webhook', __name__)

# Defina sua chave secreta de webhook do Stripe
endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')  # Ex: whsec_XXXX

@webhook_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Payload inválido
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Assinatura inválida
        return jsonify({'error': str(e)}), 400

    # 🎯 Evento de criação de assinatura
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')

        if session.get('mode') == 'subscription':
            user = User.query.filter_by(email=customer_email).first()
            if user:
                user.plan = "Pro"
                db.session.commit()

    return jsonify({'status': 'success'}), 200
