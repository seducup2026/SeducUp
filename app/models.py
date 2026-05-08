from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'aluno', 'professor', 'coordenador'
    ra = db.Column(db.String(20), unique=True, nullable=True)        # só aluno
    matricula = db.Column(db.String(20), unique=True, nullable=True) # professor e coordenador
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
    pontos = db.Column(db.Integer, default=0)
    nivel = db.Column(db.String(50), default='Explorador do Conhecimento')

class Pontuacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    coordenador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    valor = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200))  # 'prova' ou 'olimpiada'
    data = db.Column(db.DateTime, default=datetime.utcnow)