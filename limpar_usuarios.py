from app.main import create_app, db
from app.models import User, TestSession, Response

app = create_app()

with app.app_context():
    print("📌 Etapa 1: Deletando Responses...")
    db.session.query(Response).delete()
    db.session.commit()

    print("📌 Etapa 2: Deletando TestSessions...")
    db.session.query(TestSession).delete()
    db.session.commit()

    print("📌 Etapa 3: Deletando Usuários...")
    users = User.query.all()
    for user in users:
        print(f"Removendo: {user.email}")
        db.session.delete(user)

    db.session.commit()
    print("✅ Todos os usuários e dados associados foram removidos com sucesso!")
