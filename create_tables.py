# create_tables.py
from app.main import create_app, db

def create_all_tables():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Todas as tabelas foram criadas com sucesso!")

if __name__ == '__main__':
    create_all_tables()
