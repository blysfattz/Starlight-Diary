from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
import os
from werkzeug.utils import secure_filename
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-virtual-life-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

from models import Usuario, Humor, Vibe, Favorito, Momento

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
    email = request.form.get("emailForm", "").strip().lower()
    senha = request.form.get("senhaForm", "")

    user = db.session.query(Usuario).filter_by(email=email).first()

    if not user or not check_password_hash(user.senha, senha):
        return render_template(
            'login.html',
            erro='E-mail ou senha incorretos.'
        )

    login_user(user)

    return redirect(url_for('profile'))



@app.route('/registrar', methods=['POST', 'GET'])
def registrar():
    if request.method == "GET":
        return render_template('registrar.html')

    email = request.form.get("emailForm", "").strip().lower()
    nome = request.form.get("nomeForm", "").strip()
    senha = request.form.get("senhaForm", "")
    confirma = request.form.get("confirmaForm", "")

    erros = {}

    # VALIDAÇÃO DO E-MAIL
    if not email:
        erros['erro_email'] = 'O e-mail é obrigatório.'
    elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        erros['erro_email'] = 'Digite um e-mail válido.'
    elif db.session.query(Usuario).filter_by(email=email).first():
        erros['erro_email'] = 'Este e-mail já está cadastrado.'

    # VALIDAÇÃO DO NOME
    if not nome:
        erros['erro_nome'] = 'O nome é obrigatório.'
    elif db.session.query(Usuario).filter_by(nome=nome).first():
        erros['erro_nome'] = 'Este nome de usuário já está em uso.'

    # VALIDAÇÃO DA SENHA
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

    # CONFIRMAÇÃO
    if not confirma:
        erros['erro_confirma'] = 'Confirme sua senha.'
    elif senha != confirma:
        erros['erro_confirma'] = 'As senhas não coincidem.'

    if erros:
        return render_template(
            'registrar.html',
            email_digitado=email,
            nome_digitado=nome,
            **erros
        )

    novo_usuario = Usuario(
        email=email,
        nome=nome,
        senha=generate_password_hash(senha)
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

    email = request.form.get("emailForm", "").strip().lower()

    user = db.session.query(Usuario).filter_by(email=email).first()

    if not user:
        return render_template(
            'recuperar.html',
            erro='E-mail não encontrado.'
        )

    return render_template(
        'nova_senha.html',
        email=email
    )


@app.route('/recuperar/nova_senha', methods=['POST'])
def nova_senha():

    email = request.form.get("emailForm", "").strip().lower()

    senha = request.form.get("senhaForm", "")
    confirma = request.form.get("confirmaForm", "")

    erros = {}

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

    if not confirma:
        erros['erro_confirma'] = 'Confirme sua senha.'

    elif senha != confirma:
        erros['erro_confirma'] = 'As senhas não coincidem.'

    if erros:
        return render_template(
            'nova_senha.html',
            email=email,
            **erros
        )

    user = db.session.query(Usuario).filter_by(email=email).first()

    if not user:
        return render_template(
            'recuperar.html',
            erro='E-mail não encontrado.'
        )

    user.senha = generate_password_hash(senha)

    db.session.commit()

    return redirect(url_for('login'))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", usuario=current_user,
                           **_contexto_momento(current_user.id))

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


TIPOS_HUMOR = ['feliz', 'triste', 'ansioso', 'calma', 'animado',
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



FRASES_MOMENTO = [
    "Minha mente está em...",
    "Ultimamente tenho pensado em...",
    "Meu coração está voltado para...",
    "Estou tentando entender...",
    "Estou aprendendo sobre...",
    "Não consigo parar de pensar em...",
    "Neste momento, quero...",
    "Tenho vontade de...",
]
ATMOSFERAS_MOMENTO = [
    "Noite tranquila",
    "Dia aconchegante",
    "Dia introspectivo",
    "Momento especial",
    "Em paz",
    "Cheio de energia",
]

NAO_LENDO = "Não estou lendo nada no momento"


def _humor_atual(usuario_id):
    """Retorna o registro de Humor mais recente do usuário (ou None)."""
    return (db.session.query(Humor)
            .filter_by(usuario_id=usuario_id)
            .order_by(Humor.data.desc())
            .first())


def _momento_atual(usuario_id):
    """Retorna o Momento mais recente do usuário (ou None se ainda não
    existir nenhum registro — HU13/CA01)."""
    return (db.session.query(Momento)
            .filter_by(usuario_id=usuario_id)
            .order_by(Momento.data.desc())
            .first())


def _favoritos_por_categoria(usuario_id, categoria):
    """Interesses (Favoritos) do usuário numa categoria específica, usados
    para alimentar os seletores de artista/livro do momento (HU04/HU05)."""
    return (db.session.query(Favorito)
            .filter_by(usuario_id=usuario_id, categoria=categoria)
            .order_by(Favorito.titulo.asc())
            .all())


def _tempo_relativo(data):
    """Formata a data de um momento como texto dinâmico:
    'Atualizado agora', 'Atualizado há 8 minutos', 'Atualizado há 2 horas',
    'Atualizado ontem, às 21:34' ou 'Atualizado em 23/08, às 14:32'."""
    if not data:
        return None

    agora = datetime.utcnow()
    diferenca = agora - data
    segundos = diferenca.total_seconds()

    if segundos < 60:
        return "Atualizado agora"
    if segundos < 3600:
        minutos = int(segundos // 60)
        return f"Atualizado há {minutos} minuto{'s' if minutos != 1 else ''}"
    if segundos < 86400 and data.date() == agora.date():
        horas = int(segundos // 3600)
        return f"Atualizado há {horas} hora{'s' if horas != 1 else ''}"
    if data.date() == (agora - timedelta(days=1)).date():
        return f"Atualizado ontem, às {data.strftime('%H:%M')}"
    return f"Atualizado em {data.strftime('%d/%m')}, às {data.strftime('%H:%M')}"


def _contexto_momento(usuario_id):
    momento_atual = _momento_atual(usuario_id)
    humor_atual = _humor_atual(usuario_id)

    return {
        "momento_atual": momento_atual,

        "momento_atualizado_em": (
            _tempo_relativo(momento_atual.atualizado_em)
            if momento_atual else None
        ),

        "sentindo": humor_atual.tipo if humor_atual else None,

        "artistas_cadastrados": _favoritos_por_categoria(
            usuario_id, "música"
        ),

        "livros_cadastrados": _favoritos_por_categoria(
            usuario_id, "livro"
        ),

        "frases_momento": FRASES_MOMENTO,

        "atmosferas_momento": ATMOSFERAS_MOMENTO,

        "nao_lendo": NAO_LENDO,
    }

@app.route('/momentos', methods=['GET', 'POST'])
@login_required
def momentos():

    momento = _momento_atual(current_user.id)

    if request.method == 'POST':

        ouvindo = request.form.get("ouvindo", "").strip()
        lendo = request.form.get("lendo", "").strip()
        frase_inicio = request.form.get("frase_inicio", "").strip()
        frase_complemento = request.form.get("frase_complemento", "").strip()
        atmosfera = request.form.get("atmosfera", "").strip()

        erros = {}

        if not ouvindo:
            erros['erro_ouvindo'] = 'Informe o que você está ouvindo.'
        elif len(ouvindo) > 150:
            erros['erro_ouvindo'] = 'O nome do artista deve ter no máximo 150 caracteres.'

        if not lendo:
            lendo = NAO_LENDO

        if frase_inicio not in FRASES_MOMENTO:
            erros['erro_frase'] = 'Selecione uma forma válida de iniciar sua frase.'

        if len(frase_complemento) > 120:
            erros['erro_complemento'] = 'A frase deve ter no máximo 120 caracteres.'

        if atmosfera not in ATMOSFERAS_MOMENTO:
            erros['erro_atmosfera'] = 'Selecione uma atmosfera válida.'

        if erros:
            return render_template(
                "momentos.html",
                momento_atual=momento,
                **_contexto_momento(current_user.id),
                **erros
            )

        novo_momento = Momento(
            usuario_id=current_user.id,
            ouvindo=ouvindo,
            lendo=lendo,
            frase_inicio=frase_inicio,
            frase_complemento=frase_complemento if frase_complemento else None,
            atmosfera=atmosfera
        )

        db.session.add(novo_momento)
        db.session.commit()

        return redirect(url_for('profile'))

    return render_template(
        "momentos.html",
        **_contexto_momento(current_user.id)
    )

@app.route('/momentos/editar', methods=['GET', 'POST'])
@login_required
def editar_momento():

    momento = _momento_atual(current_user.id)

    # Se ainda não existe momento, não há nada para editar
    if not momento:
        return redirect(url_for('momentos'))

    # ABRIR FORMULÁRIO
    if request.method == 'GET':

        return render_template(
            'momento_editar.html',
            momento=momento,
            **_contexto_momento(current_user.id)
        )

    # RECEBER DADOS DO FORMULÁRIO

    ouvindo = request.form.get("ouvindo", "").strip()
    lendo = request.form.get("lendo", "").strip()
    frase_inicio = request.form.get("frase_inicio", "").strip()
    frase_complemento = request.form.get("frase_complemento", "").strip()
    atmosfera = request.form.get("atmosfera", "").strip()

    erros = {}

    if not ouvindo:
        erros['erro_ouvindo'] = 'Informe o que você está ouvindo.'

    elif len(ouvindo) > 150:
        erros['erro_ouvindo'] = (
            'O nome do artista deve ter no máximo 150 caracteres.'
        )

    if not lendo:
        lendo = NAO_LENDO

    elif len(lendo) > 150:
        erros['erro_lendo'] = (
            'O título deve ter no máximo 150 caracteres.'
        )

    if frase_inicio not in FRASES_MOMENTO:
        erros['erro_frase'] = (
            'Selecione uma forma válida de iniciar sua frase.'
        )

    if len(frase_complemento) > 120:
        erros['erro_complemento'] = (
            'A frase deve ter no máximo 120 caracteres.'
        )

    if atmosfera not in ATMOSFERAS_MOMENTO:
        erros['erro_atmosfera'] = (
            'Selecione uma atmosfera válida.'
        )

    # SE TIVER ERRO, VOLTA PARA O FORMULÁRIO
    if erros:

        return render_template(
            'momento_editar.html',
            momento=momento,
            **_contexto_momento(current_user.id),
            **erros
        )

    # ATUALIZA O MOMENTO EXISTENTE

    momento.ouvindo = ouvindo
    momento.lendo = lendo
    momento.frase_inicio = frase_inicio
    momento.frase_complemento = (
        frase_complemento if frase_complemento else None
    )
    momento.atmosfera = atmosfera

    db.session.commit()

    return redirect(url_for('profile'))
@app.route('/momento/historico')
@login_required
def momento_historico():
    """Histórico completo dos momentos do usuário, com filtros de
    período ('todos', 'este_mes', 'ultimos_meses'), usado pela página de
    recapitulação ('Recapitule aqui os seus momentos')."""
    filtro = request.args.get('filtro', 'todos').strip().lower()

    query = db.session.query(Momento).filter_by(usuario_id=current_user.id)

    agora = datetime.utcnow()
    if filtro == 'este_mes':
        inicio_do_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(Momento.data >= inicio_do_mes)
    elif filtro == 'ultimos_meses':
        limite = agora - timedelta(days=90)
        query = query.filter(Momento.data >= limite)
    else:
        filtro = 'todos'

    registros = query.order_by(Momento.data.desc()).all()

    for registro in registros:
        humor_na_epoca = (db.session.query(Humor)
                          .filter(Humor.usuario_id == current_user.id,
                                  Humor.data <= registro.data)
                          .order_by(Humor.data.desc())
                          .first())
        registro.sentindo = humor_na_epoca.tipo if humor_na_epoca else None

    return render_template('momento_historico.html', registros=registros, filtro=filtro)


if __name__ == '__main__':
    app.run(debug=True)
