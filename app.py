from flask import Flask, render_template, send_file, request # Cria aplicações web
import io                                                    # Trata BLOBS de imagens
import sqlite3                                               # Trabalha com o banco de dados


app = Flask(__name__)


@app.route('/imagens/imagem_<int:n_questao>')
def get_imagem(n_questao):
    """
    Recupera a imagem BLOB no banco de dados referente a questão, se houver
    
    Parâmetros:
    n_questao (int): O número da questão (num_questao) no banco de dados
    
    Retorna:
    Response ou None: Um objeto Flask contendo a imagem JPEG, ou None, caso não haja imagem
    """
    
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT img_questao FROM questao WHERE num_questao=?", (n_questao,))
    registro_img = cursor.fetchone()[0]

    cursor.close()
    conexao.close()

    if registro_img is None:
        return None
    else:
        return send_file(io.BytesIO(registro_img), mimetype='image/jpeg')



def get_dicts_questoes(ordem):
    """
    Recupera as questões no banco de dados, ordenadas pelo argumento do URL da página
    
    Parâmetros:
    ordem: Ordem em que o conteúdo deve ser mostrado (nível de dificuldade crescente ou decrescente)
    
    Retorna:
    dict: Dicionário contendo as questões ordenadas da forma que foi solicitada
    """


    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM questao")
    registro_questoes = cursor.fetchall()

    registro_keys_questoes = [coluna[0] for coluna in cursor.description]

    dicionarios_questoes = []


    for tupla in registro_questoes:
        dicionarios_questoes.append(dict(zip(registro_keys_questoes, tupla)))

    dicionarios_questoes = []
    


    for tupla in registro_questoes:
        dicionarios_questoes.append(dict(zip(registro_keys_questoes, tupla)))

    if(ordem == 'asc'):
        dicionarios_questoes = sorted(dicionarios_questoes, key=lambda questao: questao['dif_questao'])    

    if(ordem == 'desc'):
        dicionarios_questoes = sorted(dicionarios_questoes, key=lambda questao: questao['dif_questao'], reverse=True)    
    
    cursor.close()
    conexao.close()
    
    return dicionarios_questoes



def get_dict_opcoes():
    """
    Recupera as opções das questões no banco de dados
    
    Parâmetros:
    
    Retorna:
    dict: Dicionário contendo as opções das questões
    """
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM opcao")
    registro_opcoes = cursor.fetchall()

    registro_keys_opcoes = [coluna[0] for coluna in cursor.description]

    dicionario_opcoes = []

    for tupla in registro_opcoes:
        dicionario_opcoes.append(dict(zip(registro_keys_opcoes, tupla)))


    for tupla in registro_opcoes:
        dicionario_opcoes.append(dict(zip(registro_opcoes, tupla)))
    
    cursor.close()
    conexao.close()
    
    return dicionario_opcoes



@app.route('/questoes/')
def get_questoes():
    """
    Recupera as questões do banco de dados
    
    Parâmetros:

    
    Retorna:
    str: String da página renderizada com uma lista de dicionários, 
    onde cada dicionário corresponde a uma tupla da tabela
    """

    ordem = request.args.get('ord')


    dicionarios_questoes = get_dicts_questoes(ordem)
    dicionario_opcoes = get_dict_opcoes()

    
    # Retorna a página renderizada com a lista de dicionários
    return render_template('questoes.html', dicionarios_questoes=dicionarios_questoes,
                                            dicionario_opcoes=dicionario_opcoes)


@app.route('/')
def index():
    """
    Requisição referente a página inicial do site
    
    Parâmetros:

    
    Retorna:
    str: String da página renderizada
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

