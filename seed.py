from app import create_app, db, bcrypt
from app.models import Usuario

app = create_app()

with app.app_context():
    senha = bcrypt.generate_password_hash('123456').decode('utf-8')
    coord = Usuario(
        nome='Coordenador Teste',
        tipo='coordenador',
        matricula='COORD001',
        senha=senha
    )
    db.session.add(coord)
    db.session.commit()
    print('Coordenador criado com sucesso!')