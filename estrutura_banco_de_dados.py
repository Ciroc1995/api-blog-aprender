from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'UFUDFDJFNDJ223#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:w3EndTvvEJQQPLuQm7Bp@containers-us-west-138.railway.app:6936/railway'

db = SQLAlchemy(app)
db:SQLAlchemy

class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')

def inicializar_banco():
    with app.app_context():
        db.drop_all()
        db.create_all()

        autor = Autor(nome='cicero', email='cicero.cordeiro1995@gmail.com', senha='1234567', admin=True)

        db.session.add(autor)
        db.session.commit()

if __name__ == '__main__':
    inicializar_banco()