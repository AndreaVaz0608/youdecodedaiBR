from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_jwt_extended import jwt_required
from app.models import Question
from app.main import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
@jwt_required()
def admin_dashboard():
    if request.method == 'POST':
        q_id = request.form.get('id')
        q_text = request.form.get('text')
        q_type = request.form.get('type')

        if q_id and q_text and q_type:
            if not Question.query.get(q_id):
                question = Question(id=q_id, text=q_text, type=q_type)
                db.session.add(question)
                db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))

    questions = Question.query.order_by(Question.id).all()
    return render_template('admin_dashboard.html', questions=questions)

@admin_bp.route('/admin/delete/<int:question_id>', methods=['POST'])
@jwt_required()
def delete_question(question_id):
    question = Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))
