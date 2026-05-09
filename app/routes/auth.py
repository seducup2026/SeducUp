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
            usuario = Usuario.query.filter_by(matricula=matricula, tipo='coordenador').first()

        if usuario and bcrypt.check_password_hash(usuario.senha, senha):
            login_user(usuario)
            if usuario.tipo == 'aluno':
                return redirect(url_for('aluno.dashboard'))
            else:
                return redirect(url_for('coordenador.dashboard'))
        else:
            flash('Credenciais incorretas!', 'danger')

    return render_template('login.html', tipo=tipo)

@auth.route('/cadastro-coordenador', methods=['GET', 'POST'])
def cadastro_coordenador():
    if request.method == 'POST':
        nome = request.form.get('nome')
        matricula = request.form.get('matricula')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar = request.form.get('confirmar_senha')

        if senha != confirmar:
            flash('As senhas não coincidem!', 'danger')
            return render_template('cadastro_coordenador.html')

        if Usuario.query.filter_by(matricula=matricula).first():
            flash('Matrícula já cadastrada!', 'danger')
            return render_template('cadastro_coordenador.html')

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        coord = Usuario(nome=nome, matricula=matricula, email=email, senha=senha_hash, tipo='coordenador')
        db.session.add(coord)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('auth.login', tipo='coordenador'))

    return render_template('cadastro_coordenador.html')

@auth.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    return render_template('recuperar_senha.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))