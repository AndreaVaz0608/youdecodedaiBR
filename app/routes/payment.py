from flask import Blueprint, redirect, url_for, flash, current_app, request
import stripe
import os
import re

payment_bp = Blueprint("payment", __name__)

# Stripe secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout(plan: str, price_id: str, mode: str):
    try:
        coupon = request.args.get("coupon")
        valid_coupon = re.match(r"^[a-zA-Z0-9_-]{4,30}$", coupon) if coupon else None

        checkout_args = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price': price_id,
                'quantity': 1,
            }],
            'mode': mode,
            'allow_promotion_codes': True,
            'success_url': url_for("user.pagamento_sucesso", _external=True) + f"?session_id={{CHECKOUT_SESSION_ID}}&plano={plan.lower()}",
            'cancel_url': url_for("user.select_product", _external=True),
        }

        if valid_coupon:
            checkout_args['discounts'] = [{'coupon': coupon}]

        checkout_session = stripe.checkout.Session.create(**checkout_args)

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        current_app.logger.error(f"[Stripe Error - {plan.upper()}] {e}")
        flash("We couldn't start the payment process. Please try again later.", "danger")
        return redirect(url_for('user.select_product'))

@payment_bp.route('/checkout/premium')
def checkout_premium():
    return create_checkout(
        plan="Premium",
        price_id="price_1RJtEMAIkDznuZuYH4IQlK1I",  # Replace with real price ID from Stripe
        mode="payment"
    )

@payment_bp.route('/checkout/pro')
def checkout_pro():
    return create_checkout(
        plan="Pro",
        price_id="price_1RMIAJAIkDznuZuYcMF4YdTs",  # Replace with real price ID from Stripe
        mode="subscription"
    )
