from app.main import create_app, db
from app.models import Question

# 20 perguntas MBTI
mbti = [
    {
        "text": "Você se sente confortável iniciando conversas com desconhecidos?",
        "label_left": "Discordo totalmente",
        "label_right": "Concordo totalmente",
        "scale_type": "concordancia"
    },
    {
        "text": "Você prefere socializar em grandes grupos ou em interações mais íntimas e individuais?",
        "label_left": "Grandes grupos",
        "label_right": "Um a um",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você tende a falar livremente ou prefere pensar antes de se expressar?",
        "label_left": "Fala livremente",
        "label_right": "Pensa antes",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você verbaliza seus pensamentos para processá‑los ou prefere refletir internamente?",
        "label_left": "Verbaliza",
        "label_right": "Reflete",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você se sente energizado ao falar sobre ideias ou ao refletir em silêncio?",
        "label_left": "Falando",
        "label_right": "Pensando",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você confia mais em experiências passadas ou em ideias voltadas para o futuro?",
        "label_left": "Experiência",
        "label_right": "Ideias",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere focar em detalhes tangíveis ou em potenciais ocultos?",
        "label_left": "Detalhes tangíveis",
        "label_right": "Potencial oculto",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você se atrai mais por tarefas estruturadas ou interpretativas?",
        "label_left": "Estruturadas",
        "label_right": "Interpretativas",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você gosta mais de analisar teorias abstratas ou resolver problemas práticos?",
        "label_left": "Abstratas",
        "label_right": "Práticos",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você confia mais no que pode ver e tocar ou no que pode imaginar?",
        "label_left": "Ver e tocar",
        "label_right": "Imaginar",
        "scale_type": "dicotomica"
    },
    {
        "text": "Ao tomar decisões importantes, você valoriza mais a lógica ou o impacto emocional?",
        "label_left": "Lógica",
        "label_right": "Emoção",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você lida com conflitos usando lógica ou compaixão?",
        "label_left": "Lógica",
        "label_right": "Compaixão",
        "scale_type": "dicotomica"
    },
    {
        "text": "Em um desacordo, você busca ser justo e factual ou empático e conciliador?",
        "label_left": "Justo",
        "label_right": "Empático",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere raciocínio lógico ou compreender os sentimentos das pessoas ao decidir?",
        "label_left": "Lógica",
        "label_right": "Sentimentos",
        "scale_type": "dicotomica"
    },
    {
        "text": "Quando alguém comete um erro, você prefere abordar diretamente ou considerar os sentimentos da pessoa primeiro?",
        "label_left": "Abordar diretamente",
        "label_right": "Considerar sentimentos",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere ter tudo planejado ou deixar as coisas acontecerem naturalmente?",
        "label_left": "Planejado",
        "label_right": "Espontâneo",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você se organiza com listas e cronogramas ou prefere liberdade e improviso?",
        "label_left": "Listas",
        "label_right": "Improviso",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere planejar com antecedência ou ajustar conforme surgem novas informações?",
        "label_left": "Planejar",
        "label_right": "Adaptar",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você realiza tarefas em ordem definida ou alterna entre elas livremente?",
        "label_left": "Ordem definida",
        "label_right": "Alterna livremente",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere orientações passo a passo ou criar seu próprio caminho?",
        "label_left": "Passo a passo",
        "label_right": "Criar seu jeito",
        "scale_type": "dicotomica"
    }
]

# 20 perguntas DISC
disc = [
    # ▸ D  – Dominância (5)
    {
        "text": "Você tende a assumir a liderança mesmo sem ser solicitado?",
        "scale_type": "concordancia"
    },
    {
        "text": "Quando há um conflito, você tenta resolvê‑lo diretamente ou evita a tensão?",
        "label_left": "Resolver",
        "label_right": "Evitar",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere correr riscos ou evitar erros?",
        "label_left": "Assumir Riscos",
        "label_right": "Evitar Erros",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere ser desafiado ou ter segurança no trabalho?",
        "label_left": "Desafiado",
        "label_right": "Segurança",
        "scale_type": "dicotomica"
    },
    {
        "text": "Sob pressão, você prefere assumir o comando ou esperar por uma direção clara?",
        "label_left": "Assumir comando",
        "label_right": "Esperar direção",
        "scale_type": "dicotomica"
    },

    # ▸ I  – Influência (5)
    {
        "text": "Você prefere persuadir as pessoas ou garantir a estabilidade dos processos?",
        "label_left": "Persuadir",
        "label_right": "Estabilidade",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você tende a se destacar naturalmente em reuniões ou prefere escutar mais?",
        "label_left": "Destacar‑se",
        "label_right": "Escutar",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você valoriza mais a influência sobre as pessoas ou a conformidade às regras?",
        "label_left": "Influência",
        "label_right": "Regras",
        "scale_type": "dicotomica"
    },
    {
        "text": "Em grupos, você gosta de energizar os outros ou manter um clima calmo?",
        "label_left": "Energizar os outros",
        "label_right": "Manter a calma",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você se sente mais confortável sendo uma referência motivacional ou técnica?",
        "label_left": "Motivacional",
        "label_right": "Técnica",
        "scale_type": "dicotomica"
    },

    # ▸ S  – Estabilidade (5)
    {
        "text": "Você prefere um ritmo de trabalho acelerado ou estável e calmo?",
        "label_left": "Acelerado",
        "label_right": "Calmo",
        "scale_type": "dicotomica"
    },
    {
        "text": "Quando há quebra de rotina, você se adapta rapidamente ou busca restabelecer a estabilidade?",
        "label_left": "Adaptar‑se rapidamente",
        "label_right": "Restabelecer estabilidade",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere resolver problemas sozinho ou com a equipe?",
        "label_left": "Sozinho",
        "label_right": "Equipe",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você se considera mais direto ou diplomático em conversas difíceis?",
        "label_left": "Direto",
        "label_right": "Diplomático",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere manter o que já está funcionando ou inovar?",
        "label_left": "Manter",
        "label_right": "Inovar",
        "scale_type": "dicotomica"
    },

    # ▸ C  – Conformidade (5)
    {
        "text": "Você se sente mais confortável seguindo regras ou propondo novas abordagens?",
        "label_left": "Seguir Regras",
        "label_right": "Propor Inovações",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere agir com emoção ou com cautela?",
        "label_left": "Emoção",
        "label_right": "Cautela",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você se sente mais confortável com tarefas bem definidas ou desafiadoras?",
        "label_left": "Bem Definidas",
        "label_right": "Desafiadoras",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você prefere padrões e processos ou liberdade e criatividade?",
        "label_left": "Padrões",
        "label_right": "Criatividade",
        "scale_type": "dicotomica"
    },
    {
        "text": "Em tarefas críticas, você prioriza a precisão ou decisões ousadas?",
        "label_left": "Precisão",
        "label_right": "Ousadia",
        "scale_type": "dicotomica"
    }
]

# 20 perguntas ENEAGRAMA
eneagrama = [
    # ▸ Tipo 1 – Reformador
    {
        "text": "Você sente que precisa estar sempre certo para ser respeitado?",
        "label_left": "Discordo totalmente",
        "label_right": "Concordo totalmente",
        "scale_type": "concordancia"
    },
    {
        "text": "Você tende a agir rapidamente ou com cautela em decisões urgentes?",
        "label_left": "Rapidamente",
        "label_right": "Com cautela",
        "scale_type": "dicotomica"
    },

    # ▸ Tipo 2 – Prestativo
    {
        "text": "Você mede seu valor pelo quanto os outros dependem de você?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você se sente culpado por colocar suas necessidades em primeiro lugar?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ Tipo 3 – Realizador
    {
        "text": "Você sente que precisa impressionar para ser amado?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você busca mais reconhecimento ou conexão genuína?",
        "label_left": "Reconhecimento",
        "label_right": "Conexão genuína",
        "scale_type": "dicotomica"
    },

    # ▸ Tipo 4 – Individualista
    {
        "text": "Você se sente mais confortável sendo diferente ou se integrando ao grupo?",
        "label_left": "Diferente",
        "label_right": "Integrando‑se",
        "scale_type": "dicotomica"
    },
    {
        "text": "Você evita situações em que possa se sentir vulnerável?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ Tipo 5 – Investigador
    {
        "text": "Você sente necessidade de entender profundamente tudo antes de confiar?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você evita depender dos outros, mesmo quando precisa?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ Tipo 6 – Leal
    {
        "text": "Você se sente desconfortável sem garantias claras?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você está sempre se preparando para o pior cenário possível?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ Tipo 7 – Entusiasta
    {
        "text": "Você evita o silêncio e o tédio buscando constantemente coisas novas?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você se sente mais motivado pela liberdade ou pelo sucesso?",
        "label_left": "Liberdade",
        "label_right": "Sucesso",
        "scale_type": "dicotomica"
    },

    # ▸ Tipo 8 – Desafiador
    {
        "text": "Você sente necessidade de controlar o ambiente ao seu redor?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você se sente mais confortável dando ordens ou recebendo direcionamento?",
        "label_left": "Dar ordens",
        "label_right": "Receber direção",
        "scale_type": "dicotomica"
    },

    # ▸ Tipo 9 – Pacificador
    {
        "text": "Você prefere evitar conflitos mesmo que isso signifique sacrificar a sua própria vontade?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você às vezes perde contato com seus próprios desejos para manter os outros em paz?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ Itens de centro (cobertura Gut / Heart)
    {
        "text": "Você tende a assumir o controle quando algo sai do planejado?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Você busca constantemente validação para se sentir relevante?",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    }
]

# 25 perguntas BIG FIVE
big_five = [
    # ▸ EXTROVERSÃO (E) — 5 itens
    {
        "text": "Eu me sinto cheio(a) de energia quando estou com outras pessoas.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Gosto de ser o centro das atenções em eventos sociais.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Tomo a iniciativa de conversar com desconhecidos.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Sinto‑me revigorado(a) após atividades em grupo.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Falo com entusiasmo sobre minhas ideias em público.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ ABERTURA (O) — 5 itens
    {
        "text": "Tenho imaginação fértil e gosto de explorar novas ideias.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Desfruto conhecer arte, música ou literatura diferentes.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Curto aprender sobre tópicos abstratos e teóricos.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Adoro viajar para lugares desconhecidos e experimentar culturas novas.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Sou curioso(a) sobre como as coisas funcionam e faço perguntas com frequência.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ CONSCIENCIOSIDADE (C) — 5 itens
    {
        "text": "Planejo minhas tarefas e cumpro prazos rigorosamente.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Mantenho meu espaço de trabalho bem organizado.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Sinto‑me responsável por concluir o que começo.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Reviso detalhes antes de finalizar um trabalho.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Trabalho de forma constante até atingir meus objetivos.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ AMABILIDADE (A) — 5 itens
    {
        "text": "Esforço‑me para ser atencioso(a) e educado(a) com todos.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Gosto de ajudar as pessoas sem esperar algo em troca.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Evito discussões agressivas e busco compromissos.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Sou sensível às necessidades emocionais dos outros.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Confio facilmente nas pessoas e espero o melhor delas.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },

    # ▸ ESTABILIDADE EMOCIONAL (NEURO −) — 5 itens
    {
        "text": "Permaneço calmo(a) em situações de pressão.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Raramente me preocupo excessivamente com problemas.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Recupero‑me rapidamente de contratempos.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Mantenho o controle emocional quando algo dá errado.",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    },
    {
        "text": "Consigo lidar com críticas sem ficar abalado(a).",
        "label_left": "",
        "label_right": "",
        "scale_type": "concordancia"
    }
]

# ----------------------------------------------------------------------
# FUNÇÃO DE INSERT
# ----------------------------------------------------------------------
def inserir(item, qid, tipo, criadas, ignoradas, concord_padrao=False):
    """Insere pergunta se o ID não existe; devolve contadores atualizados."""
    if not db.session.get(Question, qid):
        db.session.add(
            Question(
                id=qid,
                text=item["text"],
                type=tipo,
                label_left=item.get("label_left") or ("Discordo totalmente" if concord_padrao else ""),
                label_right=item.get("label_right") or ("Concordo totalmente" if concord_padrao else ""),
                scale_type=item["scale_type"],
            )
        )
        criadas += 1
    else:
        ignoradas += 1
    return criadas, ignoradas

# ----------------------------------------------------------------------
# SEED PRINCIPAL  (única definição!)
# ----------------------------------------------------------------------
def seed_perguntas():
    app = create_app()
    with app.app_context():
        criadas, ignoradas = 0, 0

        # MBTI 1000–1999
        for i, item in enumerate(mbti, 1):
            qid = 1000 + i
            padrao = item["scale_type"] == "concordancia" and not item.get("label_left")
            criadas, ignoradas = inserir(item, qid, "MBTI", criadas, ignoradas, padrao)

        # DISC 2000–2999
        for i, item in enumerate(disc, 1):
            qid = 2000 + i
            padrao = item["scale_type"] == "concordancia" and not item.get("label_left")
            criadas, ignoradas = inserir(item, qid, "DISC", criadas, ignoradas, padrao)

        # Eneagrama 3000–3999
        for i, item in enumerate(eneagrama, 1):
            qid = 3000 + i
            padrao = item["scale_type"] == "concordancia" and not item.get("label_left")
            criadas, ignoradas = inserir(item, qid, "Eneagrama", criadas, ignoradas, padrao)

        # Big Five 4000–4999  (todos sem labels explícitos)
        for i, item in enumerate(big_five, 1):
            qid = 4000 + i
            criadas, ignoradas = inserir(item, qid, "BigFive", criadas, ignoradas, concord_padrao=True)

        db.session.commit()
        print(f"✅ Criadas: {criadas}  |  ⏭️ Ignoradas (já existiam): {ignoradas}")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    seed_perguntas()
