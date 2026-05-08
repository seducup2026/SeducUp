from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Usuario, Aluno, Turma, Pontuacao

coordenador = Blueprint('coordenador', __name__)

@coordenador.route('/coordenador/dashboard')
@login_required
def dashboard():
    return render_template('coordenador/dashboard.html')