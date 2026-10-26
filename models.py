from db import db
from flask_login import UserMixin
from datetime import datetime


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id               = db.Column(db.Integer, primary_key=True)
    nome             = db.Column(db.String(30), unique=True)
    senha            = db.Column(db.String(256))
    email            = db.Column(db.String(120), nullable=True)
    bio              = db.Column(db.String(300), nullable=True)
    avatar           = db.Column(db.String(200), nullable=True)
    total_humores    = db.Column(db.Integer, default=0)
    total_interesses = db.Column(db.Integer, default=0)

   
    humores    = db.relationship('Humor',    backref='usuario', lazy=True,
                                 cascade='all, delete-orphan')
    vibes      = db.relationship('Vibe',     backref='usuario', lazy=True,
                                 cascade='all, delete-orphan')
    favoritos  = db.relationship('Favorito', backref='usuario', lazy=True,
                                 cascade='all, delete-orphan')
    momentos   = db.relationship('Momento',  backref='usuario', lazy=True,
                                 cascade='all, delete-orphan')
    rotinas    = db.relationship('Rotina',   backref='usuario', lazy=True,
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


class Momento(db.Model):

    __tablename__ = "momentos"

    id                 = db.Column(db.Integer, primary_key=True)

    usuario_id         = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    ouvindo            = db.Column(db.String(150), nullable=False)

    lendo              = db.Column(db.String(150), nullable=False)

    frase_inicio       = db.Column(db.String(100), nullable=False)

    frase_complemento  = db.Column(db.String(160), nullable=True)


    atmosfera          = db.Column(db.String(50), nullable=False)

    data = db.Column(db.DateTime, default=datetime.utcnow)

    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def pensamento_completo(self):
        base = self.frase_inicio or ""
        complemento = self.frase_complemento or ""
        return f"{base} {complemento}".strip()


class Rotina(db.Model):
    """Atividade recorrente do usuário (ex.: 'Beber água', 'Meditar').

    A rotina se repete nos dias da semana escolhidos (`dias_semana`) e pode
    ser marcada como concluída uma vez por dia (ver RotinaConclusao).
    """

    __tablename__ = "rotinas"

    id          = db.Column(db.Integer, primary_key=True)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    titulo      = db.Column(db.String(100), nullable=False)
    descricao   = db.Column(db.String(300), nullable=True)
    periodo     = db.Column(db.String(20),  nullable=False, default='qualquer')
    horario     = db.Column(db.String(5),   nullable=True)          
    dias_semana = db.Column(db.String(13),  nullable=False,
                            default='0,1,2,3,4,5,6')
    ativa       = db.Column(db.Boolean, nullable=False, default=True)
    data        = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    conclusoes = db.relationship('RotinaConclusao', backref='rotina', lazy=True,
                                 cascade='all, delete-orphan')

    def dias_lista(self):
        return [int(d) for d in (self.dias_semana or '').split(',')
                if d.strip().isdigit()]

    def agendada_para(self, dia):
        """True se a rotina se repete no dia da semana de `dia` (date)."""
        return dia.weekday() in self.dias_lista()


class RotinaConclusao(db.Model):
    """Registro de que uma rotina foi concluída em um determinado dia.
    Só pode existir um registro por rotina/dia."""

    __tablename__ = "rotina_conclusoes"
    __table_args__ = (
        db.UniqueConstraint('rotina_id', 'data_conclusao', name='uq_rotina_dia'),
    )

    id             = db.Column(db.Integer, primary_key=True)
    rotina_id      = db.Column(db.Integer, db.ForeignKey('rotinas.id'),
                               nullable=False, index=True)
    data_conclusao = db.Column(db.Date, nullable=False, index=True)
    concluido_em   = db.Column(db.DateTime, default=datetime.utcnow)
