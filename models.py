from db import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id               = db.Column(db.Integer, primary_key=True)
    nome             = db.Column(db.String(30), unique=True)
    senha            = db.Column(db.String(256))
    pergunta_secreta = db.Column(db.String(200))
    resposta_secreta = db.Column(db.String(200))
    email            = db.Column(db.String(120), nullable=True)
    bio              = db.Column(db.String(300), nullable=True)
    avatar           = db.Column(db.String(200), nullable=True)
    total_humores    = db.Column(db.Integer, default=0)
    total_interesses = db.Column(db.Integer, default=0)

    def percentual_perfil(self):
        campos = [self.nome, self.email, self.bio, self.avatar]
        preenchidos = sum(1 for c in campos if c)
        return int((preenchidos / len(campos)) * 100)