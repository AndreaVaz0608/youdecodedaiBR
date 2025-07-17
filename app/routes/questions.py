from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.main import db
from app.models import Question

questions_bp = Blueprint('questions', __name__)

# 🔎 GET all registered questions
@questions_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    questions = Question.query.order_by(Question.id).all()
    result = [{
        'id': q.id,
        'text': q.text,
        'type': q.type,
        'created_at': q.created_at.isoformat()
    } for q in questions]
    return jsonify(result), 200

# ⬆️ POST - Bulk insert questions
@questions_bp.route('/questions/load', methods=['POST'])
@jwt_required()
def load_questions():
    print("✅ [DEBUG] Route called: /questions/load")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("❌ [ERROR] Failed to parse JSON:", e)
        return jsonify({'error': 'Invalid JSON.'}), 400

    print("📦 [DEBUG] Received data:", data)

    if not isinstance(data, list):
        print("🚫 [ERROR] Payload is not a list.")
        return jsonify({'error': 'Invalid format. Expected: list of questions.'}), 400

    created, skipped = [], []

    for item in data:
        try:
            q_id = int(item.get('id'))
            q_text = str(item.get('text'))
            q_type = str(item.get('type'))
        except Exception as e:
            print(f"⚠️ [ERROR] Malformed data: {item} - {e}")
            continue

        if not q_id or not q_text or not q_type:
            print(f"⚠️ [WARNING] Missing fields in: {item}")
            continue

        if Question.query.get(q_id):
            print(f"⏭️ [SKIPPED] Question ID {q_id} already exists.")
            skipped.append(q_id)
            continue

        question = Question(id=q_id, text=q_text, type=q_type)
        db.session.add(question)
        created.append(q_id)
        print(f"✅ [CREATED] Question ID {q_id}")

    db.session.commit()

    return jsonify({
        'created': created,
        'skipped': skipped,
        'message': f"{len(created)} questions added, {len(skipped)} skipped (already existed)"
    }), 201

# 📤 POST - Get questions by type (MBTI, DISC, Enneagram)
@questions_bp.route('/questions/by-subject', methods=['POST'])
@jwt_required()
def get_questions_by_subject():
    data = request.get_json()
    subject = data.get("subject")

    print("🟣 [DEBUG] Received subject:", subject)

    if not subject or not isinstance(subject, str):
        return jsonify({'error': "The 'subject' field is required and must be a string."}), 400

    questions = Question.query.filter_by(type=subject).order_by(Question.id).all()
    result = [{
        'id': q.id,
        'text': q.text,
        'type': q.type,
        'created_at': q.created_at.isoformat()
    } for q in questions]

    return jsonify(result), 200
