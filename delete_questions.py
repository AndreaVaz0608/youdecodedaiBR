from app.main import create_app, db
from app.models import Question, Response  # Certifique-se de importar Response

app = create_app()
with app.app_context():
    responses_deleted = Response.query.delete()
    questions_deleted = Question.query.delete()
    db.session.commit()
    print(f"🗑️ {responses_deleted} respostas deletadas")
    print(f"🗑️ {questions_deleted} perguntas deletadas")
