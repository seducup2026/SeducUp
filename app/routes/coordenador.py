from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Usuario, Aluno, Turma, Pontuacao
from sqlalchemy import func

coordenador = Blueprint('coordenador', __name__)


# ----------------------------------------------------------------
# Helper: sidebar items do coordenador
# ----------------------------------------------------------------
def sidebar_coordenador(pagina_ativa):
    return [
        {'label': 'Início',  'icon': 'house-fill',      'url': url_for('coordenador.dashboard'), 'active': pagina_ativa == 'inicio'},
        {'label': 'Turmas',  'icon': 'people-fill',     'url': url_for('coordenador.turmas'),    'active': pagina_ativa == 'turmas'},
        {'label': 'Lançar',  'icon': 'plus-circle-fill','url': url_for('coordenador.lancar'),    'active': pagina_ativa == 'lancar'},
        {'label': 'Dados',   'icon': 'bar-chart-fill',  'url': url_for('coordenador.dados'),     'active': pagina_ativa == 'dados'},
        {'label': 'Perfil',  'icon': 'person-circle',   'url': url_for('coordenador.perfil'),    'active': pagina_ativa == 'perfil'},
    ]


# ----------------------------------------------------------------
# Decorator: só coordenador acessa
# ----------------------------------------------------------------
def apenas_coordenador(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo != 'coordenador':
            flash('Acesso restrito a coordenadores.', 'danger')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated


# ----------------------------------------------------------------
# DASHBOARD — Início
# ----------------------------------------------------------------
@coordenador.route('/coordenador/dashboard')
@login_required
@apenas_coordenador
def dashboard():
    total_alunos  = Aluno.query.count()
    total_turmas  = Turma.query.count()
    total_lancado = db.session.query(func.sum(Pontuacao.valor)).scalar() or 0
    media_raw     = db.session.query(func.avg(Aluno.pontos)).scalar()
    media_pontos  = round(float(media_raw), 1) if media_raw else 0

    return render_template(
        'coordenador/dashboard.html',
        sidebar_items    = sidebar_coordenador('inicio'),
        sidebar_home_url = url_for('coordenador.dashboard'),
        perfil_url       = url_for('coordenador.perfil'),
        total_alunos     = total_alunos,
        total_turmas     = total_turmas,
        total_lancado    = total_lancado,
        media_pontos     = media_pontos,
    )


# ----------------------------------------------------------------
# TURMAS
# ----------------------------------------------------------------
@coordenador.route('/coordenador/turmas')
@login_required
@apenas_coordenador
def turmas():
    # Agrupa turmas por série
    todas = Turma.query.order_by(Turma.serie, Turma.nome).all()
    turmas_por_serie = {}
    for t in todas:
        turmas_por_serie.setdefault(t.serie, []).append(t)

    return render_template(
        'coordenador/turmas.html',
        sidebar_items     = sidebar_coordenador('turmas'),
        sidebar_home_url  = url_for('coordenador.dashboard'),
        perfil_url        = url_for('coordenador.perfil'),
        turmas_por_serie  = turmas_por_serie,
    )


# ----------------------------------------------------------------
# LANÇAR — seleção de categoria
# ----------------------------------------------------------------
@coordenador.route('/coordenador/lancar')
@login_required
@apenas_coordenador
def lancar():
    return render_template(
        'coordenador/lancar.html',
        sidebar_items    = sidebar_coordenador('lancar'),
        sidebar_home_url = url_for('coordenador.dashboard'),
        perfil_url       = url_for('coordenador.perfil'),
    )


# ----------------------------------------------------------------
# LANÇAR — formulário por categoria
# ----------------------------------------------------------------
@coordenador.route('/coordenador/lancar/<categoria>', methods=['GET', 'POST'])
@login_required
@apenas_coordenador
def lancar_categoria(categoria):
    categorias_validas = [
        'avaliacao_seduc', 'avaliacao_escola',
        'olimpiada', 'miniteste_matematica',
        'miniteste_portugues', 'projeto'
    ]
    if categoria not in categorias_validas:
        flash('Categoria inválida.', 'danger')
        return redirect(url_for('coordenador.lancar'))

    # Minitestes: submenu de matéria
    MINITESTES = ['miniteste_matematica', 'miniteste_portugues']

    if request.method == 'POST':
        nome_avaliacao  = request.form.get('nome_avaliacao', '').strip()
        total_questoes  = request.form.get('total_questoes', type=int)
        aluno_ids       = request.form.getlist('aluno_ids')
        acertos_list    = request.form.getlist('acertos')

        if not aluno_ids:
            flash('Adicione pelo menos um aluno antes de confirmar.', 'warning')
        else:
            for i, aluno_id in enumerate(aluno_ids):
                aluno = Aluno.query.get(int(aluno_id))
                if not aluno:
                    continue
                acertos = int(acertos_list[i]) if i < len(acertos_list) else 0
                # Pontuação proporcional: (acertos / total_questoes) * 100
                if total_questoes and total_questoes > 0:
                    valor = round((acertos / total_questoes) * 100)
                else:
                    valor = acertos

                p = Pontuacao(
                    aluno_id       = aluno.id,
                    coordenador_id = current_user.id,
                    valor          = valor,
                    categoria      = categoria,
                    nome_avaliacao = nome_avaliacao or None,
                    total_questoes = total_questoes,
                    acertos        = acertos,
                )
                db.session.add(p)
                aluno.pontos += valor
                aluno.atualizar_nivel()

            db.session.commit()
            flash('Pontuação lançada com sucesso!', 'success')
            return redirect(url_for('coordenador.lancar'))

    # GET: busca alunos para o modal de adicionar
    alunos = db.session.query(Aluno, Usuario, Turma)\
        .join(Usuario, Aluno.usuario_id == Usuario.id)\
        .outerjoin(Turma, Aluno.turma_id == Turma.id)\
        .order_by(Turma.nome, Usuario.nome)\
        .all()

    return render_template(
        'coordenador/lancar_categoria.html',
        sidebar_items    = sidebar_coordenador('lancar'),
        sidebar_home_url = url_for('coordenador.dashboard'),
        perfil_url       = url_for('coordenador.perfil'),
        categoria        = categoria,
        eh_miniteste     = categoria in MINITESTES,
        alunos           = alunos,
    )


# ----------------------------------------------------------------
# DADOS — Classificação geral
# ----------------------------------------------------------------
@coordenador.route('/coordenador/dados')
@login_required
@apenas_coordenador
def dados():
    serie_filtro = request.args.get('serie', 'todas')
    turma_filtro = request.args.get('turma', 'todas')

    query = db.session.query(Aluno, Usuario, Turma)\
        .join(Usuario, Aluno.usuario_id == Usuario.id)\
        .outerjoin(Turma, Aluno.turma_id == Turma.id)

    if serie_filtro != 'todas':
        query = query.filter(Turma.serie == serie_filtro)
    if turma_filtro != 'todas':
        query = query.filter(Turma.nome == turma_filtro)

    resultados = query.order_by(Aluno.pontos.desc()).all()

    # Listas para filtros
    series = db.session.query(Turma.serie).distinct().order_by(Turma.serie).all()
    series = [s[0] for s in series]

    turmas_da_serie = []
    if serie_filtro != 'todas':
        turmas_da_serie = Turma.query.filter_by(serie=serie_filtro)\
            .order_by(Turma.nome).all()

    return render_template(
        'coordenador/dados.html',
        sidebar_items     = sidebar_coordenador('dados'),
        sidebar_home_url  = url_for('coordenador.dashboard'),
        perfil_url        = url_for('coordenador.perfil'),
        resultados        = resultados,
        series            = series,
        serie_filtro      = serie_filtro,
        turma_filtro      = turma_filtro,
        turmas_da_serie   = turmas_da_serie,
    )


# ----------------------------------------------------------------
# PERFIL
# ----------------------------------------------------------------
@coordenador.route('/coordenador/perfil')
@login_required
@apenas_coordenador
def perfil():
    return render_template(
        'coordenador/perfil.html',
        sidebar_items    = sidebar_coordenador('perfil'),
        sidebar_home_url = url_for('coordenador.dashboard'),
        perfil_url       = url_for('coordenador.perfil'),
    )