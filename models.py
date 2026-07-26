from db import db
from flask_login import UserMixin
from datetime import datetime


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

    # relacionamentos
    humores    = db.relationship('Humor',    backref='usuario', lazy=True,
                                 cascade='all, delete-orphan')
    vibes      = db.relationship('Vibe',     backref='usuario', lazy=True,
                                 cascade='all, delete-orphan')
    favoritos  = db.relationship('Favorito', backref='usuario', lazy=True,
                                 cascade='all, delete-orphan')

    def percentual_perfil(self):
        campos = [self.nome, self.email, self.bio, self.avatar]
        preenchidos = sum(1 for c in campos if c)
        return int((preenchidos / len(campos)) * 100)



class Humor(db.Model):
    __tablename__ = "humores"
    id         = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo       = db.Column(db.String(50), nullable=False)
    nota       = db.Column(db.String(400), nullable=True)
    data       = db.Column(db.DateTime, default=datetime.utcnow)


class Vibe(db.Model):
    __tablename__ = "vibes"
    id         = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    descricao  = db.Column(db.String(200), nullable=False)
    categoria  = db.Column(db.String(50), nullable=True)
    data       = db.Column(db.DateTime, default=datetime.utcnow)



class Favorito(db.Model):
    __tablename__ = "favoritos"
    id         = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    titulo     = db.Column(db.String(150), nullable=False)
    categoria  = db.Column(db.String(50),  nullable=False, default='outro')
    descricao  = db.Column(db.String(400), nullable=True)
    url        = db.Column(db.String(500), nullable=True)
    data       = db.Column(db.DateTime, default=datetime.utcnow)