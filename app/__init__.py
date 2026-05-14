from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db           = SQLAlchemy()
bcrypt       = Bcrypt()
login_manager = LoginManager()
login_manager.login_view    = 'auth.selecionar_perfil'
login_manager.login_message = 'Faça login para acessar essa página.'
login_manager.login_message_category = 'warning'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth
    from app.routes.aluno import aluno
    from app.routes.coordenador import coordenador

    app.register_blueprint(auth)
    app.register_blueprint(aluno)
    app.register_blueprint(coordenador)

    # Cria tabelas se não existirem
    with app.app_context():
        db.create_all()

    return app