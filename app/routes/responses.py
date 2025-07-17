from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.main import db
from app.models import Response, TestSession
from datetime import datetime

responses_bp = Blueprint('responses', __name__)

@responses_bp.route('/responses', methods=['POST'])
@jwt_required()
def submit_response():
    data = request.get_json()

    question_id = data.get('question_id')
    answer = data.get('answer')

    if not question_id or answer is None:
        return jsonify({'error': 'Fields "question_id" and "answer" are required.'}), 400

    user_id = get_jwt_identity()

    # 🔄 Buscar ou criar uma sessão ativa para o usuário
    session = TestSession.query.filter_by(user_id=user_id).order_by(TestSession.created_at.desc()).first()
    if not session:
        session = TestSession(user_id=user_id, created_at=datetime.utcnow())
        db.session.add(session)
        db.session.commit()

    response = Response(
        user_id=user_id,
        question_id=question_id,
        answer=answer,
        session_id=session.id  # ✅ Agora com vínculo à sessão
    )

    db.session.add(response)
    db.session.commit()

    return jsonify({'message': 'Response successfully recorded.', 'session_id': session.id}), 201


@responses_bp.route('/responses', methods=['GET'])
@jwt_required()
def list_responses():
    user_id = get_jwt_identity()
    responses = Response.query.filter_by(user_id=user_id).all()

    result = [{
        'id': r.id,
        'question_id': r.question_id,
        'answer': r.answer,
        'session_id': r.session_id,
        'created_at': r.created_at.isoformat()
    } for r in responses]

    return jsonify(result), 200
