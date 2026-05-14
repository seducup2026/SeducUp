from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import Usuario, Aluno

auth = Blueprint('auth', __name__)


# ----------------------------------------------------------------
# INDEX
# ----------------------------------------------------------------
@auth.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.tipo == 'aluno':
            return redirect(url_for('aluno.dashboard'))
        return redirect(url_for('coordenador.dashboard'))
    return render_template('index.html')


# ----------------------------------------------------------------
# SELECIONAR PERFIL
# ----------------------------------------------------------------
@auth.route('/selecionar-perfil')
def selecionar_perfil():
    return render_template('selecionar_perfil.html')


# ----------------------------------------------------------------
# LOGIN (aluno e coordenador)
# ----------------------------------------------------------------
@auth.route('/login/<tipo>', methods=['GET', 'POST'])
def login(tipo):
    if tipo not in ('aluno', 'coordenador'):
        return redirect(url_for('auth.selecionar_perfil'))

    if current_user.is_authenticated:
        if current_user.tipo == 'aluno':
            return redirect(url_for('aluno.dashboard'))
        return redirect(url_for('coordenador.dashboard'))

    if request.method == 'POST':
        senha = request.form.get('senha', '').strip()

        if tipo == 'aluno':
            ra      = request.form.get('ra', '').strip()
            usuario = Usuario.query.filter_by(ra=ra, tipo='aluno').first()
        else:
            matricula = request.form.get('matricula', '').strip()
            usuario   = Usuario.query.filter_by(matricula=matricula, tipo='coordenador').first()

        if usuario and bcrypt.check_password_hash(usuario.senha, senha):
            login_user(usuario)
            flash(f'Bem-vindo, {usuario.nome.split()[0]}!', 'success')
            if usuario.tipo == 'aluno':
                return redirect(url_for('aluno.dashboard'))
            return redirect(url_for('coordenador.dashboard'))
        else:
            flash('Credenciais incorretas. Verifique e tente novamente.', 'danger')

    # Cria objetos mock de form para o template usar
    class MockField:
        def __init__(self, name):
            self.name = name
            self.errors = []
        def __call__(self, **kwargs):
            field_type = 'password' if 'senha' in self.name else 'text'
            attrs = ' '.join(f'{k}="{v}"' for k, v in kwargs.items())
            return f'<input type="{field_type}" name="{self.name}" {attrs}>'

    class MockForm:
        def __init__(self):
            self.ra             = MockField('ra')
            self.matricula      = MockField('matricula')
            self.senha          = MockField('senha')
        def hidden_tag(self):
            return ''

    return render_template('login.html', tipo=tipo, form=MockForm())


# ----------------------------------------------------------------
# CADASTRO COORDENADOR
# ----------------------------------------------------------------
@auth.route('/cadastro-coordenador', methods=['GET', 'POST'])
def cadastro_coordenador():
    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        matricula = request.form.get('matricula', '').strip()
        email     = request.form.get('email', '').strip().lower()
        senha     = request.form.get('senha', '')
        confirmar = request.form.get('confirmar_senha', '')

        # Validações
        erro = None
        if not nome or not matricula or not email or not senha:
            erro = 'Preencha todos os campos.'
        elif senha != confirmar:
            erro = 'As senhas não coincidem.'
        elif len(senha) < 6:
            erro = 'A senha deve ter pelo menos 6 caracteres.'
        elif Usuario.query.filter_by(matricula=matricula).first():
            erro = 'Essa matrícula já está cadastrada.'
        elif Usuario.query.filter_by(email=email).first():
            erro = 'Esse e-mail já está cadastrado.'

        if erro:
            flash(erro, 'danger')
            return render_template('cadastro_coordenador.html', form=_mock_cadastro_form())

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        coord = Usuario(
            nome      = nome,
            matricula = matricula,
            email     = email,
            senha     = senha_hash,
            tipo      = 'coordenador',
        )
        db.session.add(coord)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login', tipo='coordenador'))

    return render_template('cadastro_coordenador.html', form=_mock_cadastro_form())


def _mock_cadastro_form():
    """Form simples sem WTForms para o cadastro."""
    class Field:
        def __init__(self, name, field_type='text'):
            self.name       = name
            self.field_type = field_type
            self.errors     = []
        def __call__(self, **kwargs):
            cls   = kwargs.pop('class', '')
            ph    = kwargs.pop('placeholder', '')
            attrs = ' '.join(f'{k}="{v}"' for k, v in kwargs.items())
            return (f'<input type="{self.field_type}" name="{self.name}" '
                    f'class="{cls}" placeholder="{ph}" {attrs}>')

    class Form:
        nome            = Field('nome')
        matricula       = Field('matricula')
        email           = Field('email', 'email')
        senha           = Field('senha', 'password')
        confirmar_senha = Field('confirmar_senha', 'password')
        def hidden_tag(self): return ''

    return Form()


# ----------------------------------------------------------------
# LOGOUT
# ----------------------------------------------------------------
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.index'))