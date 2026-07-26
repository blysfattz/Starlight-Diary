from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
import os
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-virtual-life-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

from models import Usuario, Humor, Vibe, Favorito

lm = LoginManager(app)
lm.login_view = 'login'

with app.app_context():
    db.create_all()

@lm.user_loader
def user_loader(id):
    return db.session.get(Usuario, int(id))


@app.route('/')
def inicial():
    return render_template('inicio.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    nome  = request.form.get("nomeForm", "").strip()
    senha = request.form.get("senhaForm", "")
    user  = db.session.query(Usuario).filter_by(nome=nome).first()
    if not user or not check_password_hash(user.senha, senha):
        return render_template('login.html', erro='Nome ou senha incorretos.')
    login_user(user)
    return redirect(url_for('profile'))

@app.route('/registrar', methods=['POST', 'GET'])
def registrar():
    if request.method == "GET":
        return render_template('registrar.html')
    nome     = request.form.get("nomeForm", "").strip()
    senha    = request.form.get("senhaForm", "")
    confirma = request.form.get("confirmaForm", "")
    pergunta = request.form.get("perguntaForm", "").strip()
    resposta = request.form.get("respostaForm", "").strip().lower()
    erros    = {}

    if not nome:
        erros['erro_nome'] = 'O nome é obrigatório.'
    elif db.session.query(Usuario).filter_by(nome=nome).first():
        erros['erro_nome'] = 'Este nome de usuário já está em uso.'

    if not senha:
        erros['erro_senha'] = 'A senha é obrigatória.'
    elif len(senha) < 6:
        erros['erro_senha'] = 'A senha deve ter no mínimo 6 caracteres.'
    elif not re.search(r'[A-Z]', senha):
        erros['erro_senha'] = 'A senha deve ter pelo menos uma letra maiúscula.'
    elif not re.search(r'[a-z]', senha):
        erros['erro_senha'] = 'A senha deve ter pelo menos uma letra minúscula.'
    elif not re.search(r'[^a-zA-Z0-9]', senha):
        erros['erro_senha'] = 'A senha deve ter pelo menos um caractere especial.'

    if senha and confirma and senha != confirma:
        erros['erro_confirma'] = 'As senhas não coincidem.'

    if not pergunta:
        erros['erro_pergunta'] = 'A pergunta secreta é obrigatória.'

    if not resposta:
        erros['erro_resposta'] = 'A resposta secreta é obrigatória.'

    if erros:
        return render_template('registrar.html', nome_digitado=nome,
                               pergunta_digitada=pergunta, **erros)

    novo_usuario = Usuario(
        nome=nome,
        senha=generate_password_hash(senha),
        pergunta_secreta=pergunta,
        resposta_secreta=generate_password_hash(resposta)
    )
    db.session.add(novo_usuario)
    db.session.commit()
    login_user(novo_usuario)
    return redirect(url_for("profile"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('inicial'))


@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'GET':
        return render_template('recuperar.html')
    nome = request.form.get("nomeForm", "").strip()
    user = db.session.query(Usuario).filter_by(nome=nome).first()
    if not user:
        return render_template('recuperar.html', erro='Usuário não encontrado.')
    return render_template('responder_pergunta.html',
                           nome=nome,
                           pergunta=user.pergunta_secreta)

@app.route('/recuperar/verificar', methods=['POST'])
def verificar_resposta():
    nome     = request.form.get("nomeForm", "").strip()
    resposta = request.form.get("respostaForm", "").strip().lower()
    user     = db.session.query(Usuario).filter_by(nome=nome).first()
    if not user or not check_password_hash(user.resposta_secreta, resposta):
        return render_template('responder_pergunta.html',
                               nome=nome,
                               pergunta=user.pergunta_secreta,
                               erro='Resposta incorreta.')
    return render_template('nova_senha.html', nome=nome)

@app.route('/recuperar/nova_senha', methods=['POST'])
def nova_senha():
    nome     = request.form.get("nomeForm", "").strip()
    senha    = request.form.get("senhaForm", "")
    confirma = request.form.get("confirmaForm", "")
    erros    = {}

    if not senha:
        erros['erro_senha'] = 'A senha é obrigatória.'
    elif len(senha) < 6:
        erros['erro_senha'] = 'A senha deve ter no mínimo 6 caracteres.'
    elif not re.search(r'[A-Z]', senha):
        erros['erro_senha'] = 'A senha deve ter pelo menos uma letra maiúscula.'
    elif not re.search(r'[a-z]', senha):
        erros['erro_senha'] = 'A senha deve ter pelo menos uma letra minúscula.'
    elif not re.search(r'[^a-zA-Z0-9]', senha):
        erros['erro_senha'] = 'A senha deve ter pelo menos um caractere especial.'

    if senha and confirma and senha != confirma:
        erros['erro_confirma'] = 'As senhas não coincidem.'

    if erros:
        return render_template('nova_senha.html', nome=nome, **erros)

    user = db.session.query(Usuario).filter_by(nome=nome).first()
    user.senha = generate_password_hash(senha)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/alterar_senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    if request.method == 'GET':
        return render_template('alterar_senha.html')

    senha_atual = request.form.get("senhaAtualForm", "")
    senha_nova  = request.form.get("senhaForm", "")
    confirma    = request.form.get("confirmaForm", "")
    erros       = {}

    if not check_password_hash(current_user.senha, senha_atual):
        erros['erro_atual'] = 'Senha atual incorreta.'

    if not senha_nova:
        erros['erro_senha'] = 'A nova senha é obrigatória.'
    elif len(senha_nova) < 6:
        erros['erro_senha'] = 'A senha deve ter no mínimo 6 caracteres.'
    elif not re.search(r'[A-Z]', senha_nova):
        erros['erro_senha'] = 'A senha deve ter pelo menos uma letra maiúscula.'
    elif not re.search(r'[a-z]', senha_nova):
        erros['erro_senha'] = 'A senha deve ter pelo menos uma letra minúscula.'
    elif not re.search(r'[^a-zA-Z0-9]', senha_nova):
        erros['erro_senha'] = 'A senha deve ter pelo menos um caractere especial.'

    if senha_nova and confirma and senha_nova != confirma:
        erros['erro_confirma'] = 'As senhas não coincidem.'

    if erros:
        return render_template('alterar_senha.html', **erros)

    current_user.senha = generate_password_hash(senha_nova)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", usuario=current_user)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    current_user.nome = request.form.get("nome", current_user.nome).strip()
    current_user.bio  = request.form.get("bio", "").strip()

    arquivo = request.files.get("avatar")
    if arquivo and arquivo.filename:
        nome_arquivo = secure_filename(arquivo.filename)
        arquivo.save(os.path.join(UPLOAD_FOLDER, nome_arquivo))
        current_user.avatar = nome_arquivo

    db.session.commit()
    return redirect(url_for('profile'))


TIPOS_HUMOR = ['feliz', 'triste', 'ansioso', 'calmo', 'animado',
               'cansado', 'frustrado', 'grato']

@app.route('/humor', methods=['GET', 'POST'])
@login_required
def humor():
    if request.method == 'GET':
        historico = (db.session.query(Humor)
                     .filter_by(usuario_id=current_user.id)
                     .order_by(Humor.data.desc())
                     .limit(10)
                     .all())
        return render_template('humor.html', tipos=TIPOS_HUMOR, historico=historico)

    tipo = request.form.get("tipo", "").strip().lower()
    nota = request.form.get("nota", "").strip()

    if tipo not in TIPOS_HUMOR:
        historico = (db.session.query(Humor)
                     .filter_by(usuario_id=current_user.id)
                     .order_by(Humor.data.desc())
                     .limit(10)
                     .all())
        return render_template('humor.html', tipos=TIPOS_HUMOR, historico=historico,
                               erro='Selecione um tipo de humor válido.')

    db.session.add(Humor(
        usuario_id=current_user.id,
        tipo=tipo,
        nota=nota if nota else None
    ))
    current_user.total_humores = (current_user.total_humores or 0) + 1
    db.session.commit()
    return redirect(url_for('humor'))


@app.route('/humor/historico')
@login_required
def humor_historico():
    registros = (db.session.query(Humor)
                 .filter_by(usuario_id=current_user.id)
                 .order_by(Humor.data.desc())
                 .all())
    return render_template('humor_historico.html', registros=registros)


@app.route('/humor/<int:humor_id>', methods=['DELETE'])
@login_required
def deletar_humor(humor_id):
    registro = db.session.get(Humor, humor_id)
    if not registro or registro.usuario_id != current_user.id:
        return jsonify({'erro': 'Registro não encontrado.'}), 404
    db.session.delete(registro)
    current_user.total_humores = max(0, (current_user.total_humores or 1) - 1)
    db.session.commit()
    return jsonify({'mensagem': 'Humor removido com sucesso.'}), 200



CATEGORIAS_VIBE = ['música', 'leitura', 'série', 'jogo', 'cinema',
                   'arte', 'esporte', 'culinária', 'tecnologia', 'outro']

@app.route('/vibe', methods=['GET', 'POST'])
@login_required
def vibe():
    if request.method == 'GET':
        historico = (db.session.query(Vibe)
                     .filter_by(usuario_id=current_user.id)
                     .order_by(Vibe.data.desc())
                     .limit(10)
                     .all())
        return render_template('vibe.html', categorias=CATEGORIAS_VIBE, historico=historico)

    descricao = request.form.get("descricao", "").strip()
    categoria = request.form.get("categoria", "outro").strip().lower()

    historico = (db.session.query(Vibe)
                 .filter_by(usuario_id=current_user.id)
                 .order_by(Vibe.data.desc())
                 .limit(10)
                 .all())

    if not descricao:
        return render_template('vibe.html', categorias=CATEGORIAS_VIBE, historico=historico,
                               erro='A descrição da vibe é obrigatória.')

    if len(descricao) > 200:
        return render_template('vibe.html', categorias=CATEGORIAS_VIBE, historico=historico,
                               erro='A descrição deve ter no máximo 200 caracteres.')

    if categoria not in CATEGORIAS_VIBE:
        categoria = 'outro'

    db.session.add(Vibe(
        usuario_id=current_user.id,
        descricao=descricao,
        categoria=categoria
    ))
    current_user.total_interesses = (current_user.total_interesses or 0) + 1
    db.session.commit()
    return redirect(url_for('vibe'))


@app.route('/vibe/historico')
@login_required
def vibe_historico():
    registros = (db.session.query(Vibe)
                 .filter_by(usuario_id=current_user.id)
                 .order_by(Vibe.data.desc())
                 .all())
    return render_template('vibe_historico.html', registros=registros)


@app.route('/vibe/<int:vibe_id>', methods=['DELETE'])
@login_required
def deletar_vibe(vibe_id):
    registro = db.session.get(Vibe, vibe_id)
    if not registro or registro.usuario_id != current_user.id:
        return jsonify({'erro': 'Registro não encontrado.'}), 404
    db.session.delete(registro)
    current_user.total_interesses = max(0, (current_user.total_interesses or 1) - 1)
    db.session.commit()
    return jsonify({'mensagem': 'Vibe removida com sucesso.'}), 200



CATEGORIAS_FAVORITO = ['música', 'série', 'filme', 'livro', 'jogo',
                       'lugar', 'pessoa', 'outro']

@app.route('/favoritos', methods=['GET', 'POST'])
@login_required
def favoritos():
    """Lista todos os favoritos e permite adicionar um novo."""
    # Filtro opcional por categoria via query string: /favoritos?categoria=série
    categoria_filtro = request.args.get('categoria', '').strip().lower()

    if request.method == 'POST':
        titulo    = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "outro").strip().lower()
        descricao = request.form.get("descricao", "").strip()
        url       = request.form.get("url", "").strip()

        erros = {}

        if not titulo:
            erros['erro_titulo'] = 'O título é obrigatório.'
        elif len(titulo) > 150:
            erros['erro_titulo'] = 'O título deve ter no máximo 150 caracteres.'

        if categoria not in CATEGORIAS_FAVORITO:
            categoria = 'outro'

        if url and not re.match(r'^https?://', url):
            erros['erro_url'] = 'A URL deve começar com http:// ou https://'

        if erros:
            lista = _buscar_favoritos(current_user.id, categoria_filtro)
            return render_template('favoritos.html',
                                   favoritos=lista,
                                   categorias=CATEGORIAS_FAVORITO,
                                   categoria_filtro=categoria_filtro,
                                   **erros)

        db.session.add(Favorito(
            usuario_id=current_user.id,
            titulo=titulo,
            categoria=categoria,
            descricao=descricao if descricao else None,
            url=url if url else None
        ))
        db.session.commit()
        return redirect(url_for('favoritos'))

    lista = _buscar_favoritos(current_user.id, categoria_filtro)
    return render_template('favoritos.html',
                           favoritos=lista,
                           categorias=CATEGORIAS_FAVORITO,
                           categoria_filtro=categoria_filtro)


def _buscar_favoritos(usuario_id, categoria_filtro=''):
    """Helper: retorna favoritos do usuário, com filtro opcional por categoria."""
    query = (db.session.query(Favorito)
             .filter_by(usuario_id=usuario_id)
             .order_by(Favorito.data.desc()))
    if categoria_filtro and categoria_filtro in CATEGORIAS_FAVORITO:
        query = query.filter_by(categoria=categoria_filtro)
    return query.all()


@app.route('/favoritos/<int:fav_id>', methods=['GET', 'POST'])
@login_required
def editar_favorito(fav_id):
    """Exibe e processa a edição de um favorito existente."""
    fav = db.session.get(Favorito, fav_id)
    if not fav or fav.usuario_id != current_user.id:
        return redirect(url_for('favoritos'))

    if request.method == 'GET':
        return render_template('favorito_editar.html',
                               fav=fav,
                               categorias=CATEGORIAS_FAVORITO)

    titulo    = request.form.get("titulo", "").strip()
    categoria = request.form.get("categoria", fav.categoria).strip().lower()
    descricao = request.form.get("descricao", "").strip()
    url       = request.form.get("url", "").strip()
    erros     = {}

    if not titulo:
        erros['erro_titulo'] = 'O título é obrigatório.'
    elif len(titulo) > 150:
        erros['erro_titulo'] = 'O título deve ter no máximo 150 caracteres.'

    if categoria not in CATEGORIAS_FAVORITO:
        categoria = fav.categoria

    if url and not re.match(r'^https?://', url):
        erros['erro_url'] = 'A URL deve começar com http:// ou https://'

    if erros:
        return render_template('favorito_editar.html',
                               fav=fav,
                               categorias=CATEGORIAS_FAVORITO,
                               **erros)

    fav.titulo    = titulo
    fav.categoria = categoria
    fav.descricao = descricao if descricao else None
    fav.url       = url if url else None
    db.session.commit()
    return redirect(url_for('favoritos'))


@app.route('/favoritos/<int:fav_id>/deletar', methods=['POST'])
@login_required
def deletar_favorito(fav_id):
    """Remove um favorito via form POST (compatível com HTML puro)."""
    fav = db.session.get(Favorito, fav_id)
    if fav and fav.usuario_id == current_user.id:
        db.session.delete(fav)
        db.session.commit()
    return redirect(url_for('favoritos'))


@app.route('/favoritos/<int:fav_id>', methods=['DELETE'])
@login_required
def deletar_favorito_ajax(fav_id):
    """Remove um favorito via DELETE (para uso com fetch/AJAX)."""
    fav = db.session.get(Favorito, fav_id)
    if not fav or fav.usuario_id != current_user.id:
        return jsonify({'erro': 'Favorito não encontrado.'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'mensagem': 'Favorito removido com sucesso.'}), 200


if __name__ == '__main__':
    app.run(debug=True)