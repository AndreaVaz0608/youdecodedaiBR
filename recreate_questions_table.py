from app.main import create_app, db
from app.models import Question
from seed_questions import mbti, disc, eneagrama

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Tabelas recriadas com sucesso!")

    perguntas = []

    # Contagens
    print("📊 Contagem de perguntas:")
    print("MBTI:", len(mbti))
    print("DISC:", len(disc))
    print("ENEAGRAMA:", len(eneagrama))
    print("TOTAL:", len(mbti) + len(disc) + len(eneagrama))

    # Inserção MBTI com ID manual
    for i, item in enumerate(mbti, start=1):
        perguntas.append(Question(
            id=1000 + i,
            type="MBTI",
            text={"en": item["text"]},
            label_left={"en": item["label_left"]} if item["scale_type"] == "dicotomica" else {},
            label_right={"en": item["label_right"]} if item["scale_type"] == "dicotomica" else {},
            scale_type=item["scale_type"]
        ))

    # Inserção DISC com ID manual
    for i, item in enumerate(disc, start=1):
        perguntas.append(Question(
            id=2000 + i,
            type="DISC",
            text={"en": item["text"]},
            label_left={"en": item["label_left"]} if item["scale_type"] == "dicotomica" else {},
            label_right={"en": item["label_right"]} if item["scale_type"] == "dicotomica" else {},
            scale_type=item["scale_type"]
        ))

    # Inserção Eneagrama com ID manual
    for i, item in enumerate(eneagrama, start=1):
        perguntas.append(Question(
            id=3000 + i,
            type="Eneagrama",
            text={"en": item["text"]},
            label_left={"en": item["label_left"]} if item["scale_type"] == "dicotomica" else {},
            label_right={"en": item["label_right"]} if item["scale_type"] == "dicotomica" else {},
            scale_type=item["scale_type"]
        ))

    db.session.add_all(perguntas)
    db.session.commit()
    print(f"✅ {len(perguntas)} perguntas inseridas com sucesso.")
