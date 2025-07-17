from datetime import datetime
from app.main import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON  # ✅ Suporte a campos JSON (PostgreSQL)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    accepted_terms = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(256), nullable=True)  # 🔥 ADICIONAR ISSO
    accepted_privacy = db.Column(db.Boolean, default=False)  # 🔥 NOVO

    # ✅ Adicione essa linha:
    plan = db.Column(db.String(20), default='Free')  # Free, Premium, Pro
    is_admin = db.Column(db.Boolean, default=False)  # ✅ Novo campo para acesso especial

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class TestSession(db.Model):
    __tablename__ = 'test_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ai_result = db.Column(db.Text, nullable=True)  # ✅ Resposta completa gerada pela IA

    # ✅ Perfis identificados
    mbti_result = db.Column(db.String(10), nullable=True)
    disc_result = db.Column(db.String(10), nullable=True)
    eneagrama_result = db.Column(db.String(20), nullable=True)
    big_five_result  = db.Column(db.String(50), nullable=True)   # ← 🆕 aqui

    responses = db.relationship('Response', backref='session', lazy=True)


class Response(db.Model):
    __tablename__ = 'responses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id'), nullable=False)
    answer = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(JSON, nullable=False)  # ✅ Agora suporta multilíngue
    type = db.Column(db.String(20), nullable=False)  # MBTI, DISC, Eneagrama

    label_left = db.Column(JSON, nullable=True)     # ✅ Agora multilíngue também
    label_right = db.Column(JSON, nullable=True)    # ✅ Igual acima
    scale_type = db.Column(db.String(20))           # "dicotomica" ou "concordancia"

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship('Response', backref='question', lazy=True)


# ✅ Respostas consolidadas para geração de perfil final
class UserResponse(db.Model):
    __tablename__ = 'user_responses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# app/models.py
from datetime import datetime
from app.main import db

class VocationalSession(db.Model):
    __tablename__ = 'vocational_sessions'  # ⚠️ Garante consistência com o nome da tabela no banco

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # ✅ Tabela correta: 'users'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_result = db.Column(db.Text)  # ✅ Novo campo para salvar resposta da IA

    responses = db.relationship('VocationalResponse', backref='session', lazy=True)

class VocationalResponse(db.Model):
    __tablename__ = 'vocational_responses'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('vocational_sessions.id'))
    question_id = db.Column(db.Integer)
    answer = db.Column(db.Text)  # ✅ ALTERADO DE String(200) para Text

class AISnapshot(db.Model):
    __tablename__ = 'ai_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id'))
    summary = db.Column(db.Text)
    mbti = db.Column(db.String(50))
    disc = db.Column(db.String(50))
    eneagrama = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='ai_snapshots')
    session = db.relationship('TestSession', backref='ai_snapshots')
