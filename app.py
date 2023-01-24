from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, app, db
import json
import jwt
from datetime import datetime, timedelta
from functools import wraps


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'token não incluido'}, 401)
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'token inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow(
        ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})



@app.route('/postagens')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['id_postagem'] = postagem.id_postagem
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        
        lista_de_postagens.append(postagem_atual)
    
    return jsonify({'lista de postagens': lista_de_postagens})


@app.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem:
        return jsonify({'Mensagem': 'Postagem não encontrada'})
    postagem_atual = {}
    postagem_atual['id_postagem'] = postagem.id_postagem
    postagem_atual['titulo'] = postagem.titulo
    postagem_atual['id_autor'] = postagem.id_autor

    return jsonify(f'Você buscou pela postagem {postagem_atual}')


@app.route('/postagens', methods=['POST'])
@token_obrigatorio
def nova_postagens(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'Mensagem': 'Nova postagem criada com sucesso'}, 200)


@app.route('/postagens/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_a_alterar = request.get_json()
    postagem_existente = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem_existente:
        return jsonify({'Mensagem': 'Não foi possivel alterar postagem'})
    try:
        postagem_existente.titulo = postagem_a_alterar['titulo']
    except:
        pass
    try:
        postagem_existente.id_autor = postagem_a_alterar['id_autor']
    except:
        pass

    db.session.commit()

    return jsonify({'Mensagem': 'Postagem alterada com sucesso'}, 200)


@app.route('/postagens/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def deletar_postagem(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem:
        return jsonify({'Mensagem': 'Não foi possivel excluir a postagem'})
    db.session.delete(postagem)
    db.session.commit()

    return jsonify({'Mensagem': 'Postagem excluida com sucesso'}, 200)


@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)
    
    return jsonify({'lista de autores': lista_de_autores})



@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_indice(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'Mensagem': 'Usuário não encontrado'})
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email

    return jsonify(f'Você buscou pelo autor {autor_atual}')



@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(
        nome=novo_autor['nome'], senha=novo_autor['senha'], email=novo_autor['email'])

    db.session.add(autor)
    db.session.commit()

    return jsonify({'Mensagem': 'Novo autor criado com sucesso'}, 200)



@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    autor_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'Mensagem': 'Não foi possivel encontrar o usuário'})
    try:
        autor.nome = autor_a_alterar['nome']
    except:
        pass
    try:
        autor.email = autor_a_alterar['email']
    except:
        pass
    try:
        autor.senha = autor_a_alterar['senha']
    except:
        pass

    db.session.commit()

    return jsonify({'Mensagem': 'Usuário alterado com sucesso'}, 200)



@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'Mensagem': 'Não foi possivel excluir o usuário'})
    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'Mensagem': 'Usuário deletado com sucesso'}, 200)



app.run(port=5000, host='localhost', debug=True)