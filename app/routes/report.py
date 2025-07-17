# app/routes/report.py

from flask import Blueprint, request, jsonify
from app.models import UserResponse
from app.services.perfil_service import generate_profile_key
from app.services.generate_behavioral_report import generate_behavioral_report
from app.main import db

report_bp = Blueprint("report", __name__)

@report_bp.route("/generate_profile", methods=["POST"])
def generate_profile():
    try:
        user_id = request.json.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # 🔍 Fetch all saved responses for the user
        respostas = UserResponse.query.filter_by(user_id=user_id).all()
        if not respostas:
            return jsonify({"error": "No responses found for this user"}), 404

        # 🧠 Convert answers into a dictionary: { question_id: answer }
        respostas_dict = {
            resposta.question_id: resposta.answer for resposta in respostas
        }

        # 🔑 Generate profile key: MBTI + DISC + Enneagram
        perfil = gerar_chave_perfil(respostas_dict)

        # 🤖 Generate behavioral report (mock or AI integration)
        relatorio = generate_behavioral_report(
            mbti=perfil["mbti"],
            disc=perfil["disc"],
            eneagrama=perfil["eneagrama"]
        )

        # Build JSON response
        response_data = {
            "profile": perfil,
            "report": relatorio
        }

        if isinstance(relatorio, dict) and "prompt" in relatorio:
            response_data["prompt_sent"] = relatorio["prompt"]

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": f"Error generating report: {str(e)}"}), 500
