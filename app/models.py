from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'aluno' ou 'coordenador'
    ra = db.Column(db.String(20), unique=True, nullable=True)         # só aluno
    matricula = db.Column(db.String(20), unique=True, nullable=True)  # só coordenador
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    aluno_perfil = db.relationship('Aluno', backref='usuario', uselist=False,
                                   foreign_keys='Aluno.usuario_id')
    pontuacoes_lancadas = db.relationship('Pontuacao', backref='coordenador',
                                          foreign_keys='Pontuacao.coordenador_id')


class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)   # ex: '1ªA', '2ªB'
    serie = db.Column(db.String(20), nullable=False)  # ex: '1ª Série', '2ª Série'
    ano = db.Column(db.Integer, nullable=False)
    coordenador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    # Relacionamentos
    alunos = db.relationship('Aluno', backref='turma', lazy=True)


class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=True)
    pontos = db.Column(db.Integer, default=0)
    nivel = db.Column(db.String(50), default='Despertar do Saber')
    # Níveis: 'Despertar do Saber' | 'Aprendiz em Evolução' |
    #         'Destaque de Aprendizagem' | 'Protagonista do Saber'

    # Relacionamentos
    pontuacoes = db.relationship('Pontuacao', backref='aluno',
                                 foreign_keys='Pontuacao.aluno_id')

    def atualizar_nivel(self):
        """Recalcula o nível com base nos pontos totais."""
        if self.pontos >= 151:
            self.nivel = 'Protagonista do Saber'
        elif self.pontos >= 101:
            self.nivel = 'Destaque de Aprendizagem'
        elif self.pontos >= 51:
            self.nivel = 'Aprendiz em Evolução'
        else:
            self.nivel = 'Despertar do Saber'


class Pontuacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    coordenador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    valor = db.Column(db.Integer, nullable=False)

    # Categoria da avaliação
    categoria = db.Column(db.String(50), nullable=False)
    # Categorias: 'avaliacao_seduc' | 'avaliacao_escola' | 'olimpiada' |
    #             'miniteste_matematica' | 'miniteste_portugues' | 'projeto'

    nome_avaliacao = db.Column(db.String(200), nullable=True)
    # Nome livre: ex 'Simula+', 'Olimpíada de Matemática', 'Feira de Profissões'
    # Nulo para minitestes (categoria já define o nome)

    total_questoes = db.Column(db.Integer, nullable=True)
    acertos = db.Column(db.Integer, nullable=True)

    data = db.Column(db.DateTime, default=datetime.utcnow)

    # Label amigável para exibir no histórico do aluno
    CATEGORIAS = {
        'avaliacao_seduc':       'Avaliação Seduc',
        'avaliacao_escola':      'Avaliação Escola',
        'olimpiada':             'Olimpíada',
        'miniteste_matematica':  'Miniteste de Matemática',
        'miniteste_portugues':   'Miniteste de Português',
        'projeto':               'Projeto',
    }

    @property
    def categoria_label(self):
        return self.CATEGORIAS.get(self.categoria, self.categoria)