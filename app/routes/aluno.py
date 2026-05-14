from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import Aluno, Turma, Pontuacao, Usuario
from app import db

aluno = Blueprint('aluno', __name__)


# ----------------------------------------------------------------
# Helper: sidebar items do aluno
# ----------------------------------------------------------------
def sidebar_aluno(pagina_ativa):
    return [
        {'label': 'Início', 'icon': 'house-fill',    'url': url_for('aluno.dashboard'), 'active': pagina_ativa == 'inicio'},
        {'label': 'Turma',  'icon': 'people-fill',   'url': url_for('aluno.turma'),     'active': pagina_ativa == 'turma'},
        {'label': 'Perfil', 'icon': 'person-circle', 'url': url_for('aluno.perfil'),    'active': pagina_ativa == 'perfil'},
    ]


# ----------------------------------------------------------------
# Decorator: só aluno acessa
# ----------------------------------------------------------------
def apenas_aluno(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo != 'aluno':
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated


# ----------------------------------------------------------------
# DASHBOARD — Início
# ----------------------------------------------------------------
@aluno.route('/aluno/dashboard')
@login_required
@apenas_aluno
def dashboard():
    aluno_obj = Aluno.query.filter_by(usuario_id=current_user.id).first_or_404()
    filtro    = request.args.get('filtro', 'todos')

    # Filtro do histórico
    query = Pontuacao.query.filter_by(aluno_id=aluno_obj.id)

    if filtro == 'provas':
        query = query.filter(Pontuacao.categoria.in_([
            'avaliacao_seduc', 'avaliacao_escola',
            'miniteste_matematica', 'miniteste_portugues'
        ]))
    elif filtro == 'olimpiadas':
        query = query.filter(Pontuacao.categoria == 'olimpiada')

    historico = query.order_by(Pontuacao.data.desc()).limit(10).all()

    return render_template(
        'aluno/dashboard.html',
        sidebar_items    = sidebar_aluno('inicio'),
        sidebar_home_url = url_for('aluno.dashboard'),
        perfil_url       = url_for('aluno.perfil'),
        aluno            = aluno_obj,
        historico        = historico,
        filtro           = filtro,
    )


# ----------------------------------------------------------------
# TURMA — Classificação da série
# ----------------------------------------------------------------
@aluno.route('/aluno/turma')
@login_required
@apenas_aluno
def turma():
    aluno_obj = Aluno.query.filter_by(usuario_id=current_user.id).first_or_404()
    turma_obj = aluno_obj.turma

    if not turma_obj:
        return render_template(
            'aluno/turma.html',
            sidebar_items    = sidebar_aluno('turma'),
            sidebar_home_url = url_for('aluno.dashboard'),
            perfil_url       = url_for('aluno.perfil'),
            turma_selecionada = None,
            turmas_serie      = [],
            alunos            = [],
            serie             = None,
        )

    serie = turma_obj.serie

    # Turmas da mesma série
    turmas_serie = Turma.query.filter_by(serie=serie).order_by(Turma.nome).all()

    # Turma selecionada via query param (padrão: turma do aluno)
    turma_nome = request.args.get('turma', turma_obj.nome)
    turma_sel  = Turma.query.filter_by(nome=turma_nome, serie=serie).first() or turma_obj

    # Alunos da turma selecionada ordenados por pontos
    alunos = db.session.query(Aluno, Usuario)\
        .join(Usuario, Aluno.usuario_id == Usuario.id)\
        .filter(Aluno.turma_id == turma_sel.id)\
        .order_by(Aluno.pontos.desc())\
        .all()

    return render_template(
        'aluno/turma.html',
        sidebar_items     = sidebar_aluno('turma'),
        sidebar_home_url  = url_for('aluno.dashboard'),
        perfil_url        = url_for('aluno.perfil'),
        turma_selecionada = turma_sel,
        turmas_serie      = turmas_serie,
        alunos            = alunos,
        serie             = serie,
        aluno_atual_id    = aluno_obj.id,
    )


# ----------------------------------------------------------------
# PERFIL
# ----------------------------------------------------------------
@aluno.route('/aluno/perfil')
@login_required
@apenas_aluno
def perfil():
    aluno_obj = Aluno.query.filter_by(usuario_id=current_user.id).first_or_404()

    return render_template(
        'aluno/perfil.html',
        sidebar_items    = sidebar_aluno('perfil'),
        sidebar_home_url = url_for('aluno.dashboard'),
        perfil_url       = url_for('aluno.perfil'),
        aluno            = aluno_obj,
    )