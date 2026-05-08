from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import db, bcrypt
from app.models import Usuario

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return render_template('index.html')

@auth.route('/selecionar-perfil')
def selecionar_perfil():
    return render_template('selecionar_perfil.html')

@auth.route('/login/<tipo>', methods=['GET', 'POST'])
def login(tipo):
    if request.method == 'POST':
        senha = request.form.get('senha')

        if tipo == 'aluno':
            ra = request.form.get('ra')
            usuario = Usuario.query.filter_by(ra=ra, tipo='aluno').first()
        else:
            matricula = request.form.get('matricula')
            usuario = Usuario.query.filter_by(matricula=matricula, tipo=tipo).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, senha):
            login_user(usuario)
            if usuario.tipo == 'aluno':
                return redirect(url_for('aluno.dashboard'))
            elif usuario.tipo == 'professor':
                return redirect(url_for('professor.dashboard'))
            elif usuario.tipo == 'coordenador':
                return redirect(url_for('coordenador.dashboard'))
        else:
            flash('Credenciais incorretas!', 'danger')

    return render_template('login.html', tipo=tipo)

@auth.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    return render_template('recuperar_senha.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))