from app import create_app, db, bcrypt
from app.models import Usuario, Aluno, Turma, Pontuacao
from datetime import datetime

app = create_app()

with app.app_context():

    # Limpa dados existentes para evitar duplicatas
    Pontuacao.query.delete()
    Aluno.query.delete()
    Turma.query.delete()
    Usuario.query.delete()
    db.session.commit()

    senha = bcrypt.generate_password_hash('123456').decode('utf-8')

    # ----------------------------------------------------------------
    # COORDENADOR DE TESTE
    # ----------------------------------------------------------------
    coord = Usuario(
        nome      = 'Ricardo Campos',
        tipo      = 'coordenador',
        matricula = 'COORD001',
        email     = 'coord.ricardo@seduc.com',
        senha     = senha,
    )
    db.session.add(coord)
    db.session.flush()

    # ----------------------------------------------------------------
    # TURMAS
    # ----------------------------------------------------------------
    turmas_data = [
        ('1ªA', '1ª Série'), ('1ªB', '1ª Série'), ('1ªC', '1ª Série'),
        ('2ªA', '2ª Série'), ('2ªB', '2ª Série'),
        ('3ªA', '3ª Série'),
    ]

    turmas = {}
    for nome, serie in turmas_data:
        t = Turma(nome=nome, serie=serie, ano=2026, coordenador_id=coord.id)
        db.session.add(t)
        db.session.flush()
        turmas[nome] = t

    # ----------------------------------------------------------------
    # ALUNOS DE TESTE
    # ----------------------------------------------------------------
    alunos_data = [
        # (nome, ra, email, turma)
        ('João da Silva',      'RA001', 'joao.silva@aluno.seduc',   '1ªA'),
        ('Maria Oliveira',     'RA002', 'maria.oliveira@aluno.seduc','1ªA'),
        ('Pedro Santos',       'RA003', 'pedro.santos@aluno.seduc', '1ªA'),
        ('Ana Costa',          'RA004', 'ana.costa@aluno.seduc',    '1ªA'),
        ('Lucas Ferreira',     'RA005', 'lucas.ferreira@aluno.seduc','1ªA'),
        ('Carla Dias',         'RA006', 'carla.dias@aluno.seduc',   '1ªB'),
        ('Bruno Lima',         'RA007', 'bruno.lima@aluno.seduc',   '1ªB'),
        ('Fernanda Souza',     'RA008', 'fernanda.souza@aluno.seduc','1ªB'),
        ('Rafael Alves',       'RA009', 'rafael.alves@aluno.seduc', '1ªB'),
        ('Juliana Reis',       'RA010', 'juliana.reis@aluno.seduc', '1ªC'),
        ('Gabriel Mendes',     'RA011', 'gabriel.mendes@aluno.seduc','1ªC'),
        ('Isabela Castro',     'RA012', 'isabela.castro@aluno.seduc','2ªA'),
        ('Matheus Rocha',      'RA013', 'matheus.rocha@aluno.seduc','2ªA'),
        ('Larissa Nunes',      'RA014', 'larissa.nunes@aluno.seduc','2ªB'),
        ('Thiago Barbosa',     'RA015', 'thiago.barbosa@aluno.seduc','3ªA'),
    ]

    aluno_objs = {}
    for nome, ra, email, turma_nome in alunos_data:
        u = Usuario(nome=nome, ra=ra, email=email, tipo='aluno', senha=senha)
        db.session.add(u)
        db.session.flush()
        a = Aluno(usuario_id=u.id, turma_id=turmas[turma_nome].id, pontos=0)
        db.session.add(a)
        db.session.flush()
        aluno_objs[ra] = a

    # ----------------------------------------------------------------
    # PONTUAÇÕES DE EXEMPLO
    # ----------------------------------------------------------------
    pontuacoes = [
        ('RA001', 'miniteste_matematica', None,           12, 10),
        ('RA001', 'miniteste_portugues',  None,           12, 11),
        ('RA001', 'avaliacao_escola',     '1ª Avaliação', 65, 55),
        ('RA002', 'miniteste_matematica', None,           12, 8),
        ('RA002', 'olimpiada',            'OBM 2026',     20, 15),
        ('RA003', 'avaliacao_seduc',      'Simula+',      52, 40),
        ('RA004', 'miniteste_portugues',  None,           12, 9),
        ('RA005', 'projeto',              'Feira de Ciências', 20, 18),
        ('RA006', 'miniteste_matematica', None,           12, 7),
        ('RA007', 'avaliacao_escola',     '1ª Avaliação', 65, 50),
        ('RA008', 'olimpiada',            'OBG 2026',     20, 12),
        ('RA009', 'miniteste_portugues',  None,           12, 6),
        ('RA010', 'avaliacao_seduc',      'Simula+',      52, 35),
        ('RA011', 'projeto',              'Feira de Profissões', 20, 16),
        ('RA012', 'miniteste_matematica', None,           12, 11),
        ('RA013', 'avaliacao_escola',     '1ª Avaliação', 65, 60),
        ('RA014', 'olimpiada',            'OBM 2026',     20, 18),
        ('RA015', 'avaliacao_seduc',      'Simula+',      52, 45),
    ]

    for ra, categoria, nome_aval, total_q, acertos in pontuacoes:
        aluno = aluno_objs[ra]
        valor = round((acertos / total_q) * 100)
        p = Pontuacao(
            aluno_id       = aluno.id,
            coordenador_id = coord.id,
            valor          = valor,
            categoria      = categoria,
            nome_avaliacao = nome_aval,
            total_questoes = total_q,
            acertos        = acertos,
            data           = datetime.utcnow(),
        )
        db.session.add(p)
        aluno.pontos += valor

    db.session.flush()

    # Recalcula níveis por série
    from app.models import Turma as T
    series = db.session.query(T.serie).distinct().all()
    for (serie,) in series:
        alunos_serie = (
            Aluno.query
            .join(T, Aluno.turma_id == T.id)
            .filter(T.serie == serie)
            .order_by(Aluno.pontos.desc())
            .all()
        )
        total = len(alunos_serie)
        c1 = max(1, round(total * 0.20))
        c2 = c1 + max(1, round(total * 0.20))
        c3 = c2 + max(1, round(total * 0.35))
        for i, a in enumerate(alunos_serie):
            if i < c1:
                a.nivel = 'Protagonista do Saber'
            elif i < c2:
                a.nivel = 'Destaque de Aprendizagem'
            elif i < c3:
                a.nivel = 'Aprendiz em Evolução'
            else:
                a.nivel = 'Despertar do Saber'

    db.session.commit()

    print("=" * 50)
    print("✅ Seed concluído com sucesso!")
    print("=" * 50)
    print()
    print("👤 COORDENADOR:")
    print("   Matrícula : COORD001")
    print("   Senha     : 123456")
    print()
    print("🎓 ALUNO DE TESTE (1ªA - maior pontuação):")
    print("   RA   : RA001")
    print("   Senha: 123456")
    print()
    print("🎓 ALUNO DE TESTE (1ªB):")
    print("   RA   : RA006")
    print("   Senha: 123456")
    print("=" * 50)