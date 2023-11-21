from flask import *  # Cria aplicações web
import io  # Trata BLOBS de imagens
import sqlite3  # Trabalha com o banco de dados
from flask_session import Session

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.secret_key = 'your_secret_key'


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

    cursor.execute("SELECT img_questao FROM questao WHERE num_questao = ?", (n_questao,))
    registro_img = cursor.fetchone()[0]

    cursor.close()
    conexao.close()

    if registro_img is None:
        return None
    else:
        return send_file(io.BytesIO(registro_img), mimetype='image/jpeg')


def get_dict_questoes():
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT num_questao, dif_questao FROM questao")

    reg_questoes = cursor.fetchall()

    dicts_questoes = [{'num_questao': num_questao, 'dif_questao': dif_questao}
                      for num_questao, dif_questao in reg_questoes]

    cursor.close()
    conexao.close()

    return dicts_questoes


def get_dict_questao(num_questao):
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM questao WHERE num_questao = ?", (num_questao,))

    reg_questao = cursor.fetchall()
    reg_key_questao = [coluna[0] for coluna in cursor.description]

    dict_questao = {}
    for tupla in reg_questao:
        dict_questao = dict(zip(reg_key_questao, tupla))

    cursor.close()
    conexao.close()

    return dict_questao


def get_dict_opcoes(num_questao):
    """
    Recupera as opções das questões no banco de dados
    
    Parâmetros:
    
    Retorna:
    dict: Dicionário contendo as opções das questões
    """
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM opcao WHERE fk_num_questao = ?", (num_questao,))
    reg_opcoes = cursor.fetchall()

    reg_keys_opcoes = [coluna[0] for coluna in cursor.description]

    dicts_opcoes = [dict(zip(reg_keys_opcoes, opcao)) for opcao in reg_opcoes]

    cursor.close()
    conexao.close()

    return dicts_opcoes



@app.route('/login/')
def login():
    """
    Requisição referente a página de login do site
    
    Parâmetros:


    Retorna:
    str: String da página renderizada
    """

    return render_template('login.html')


@app.route('/login/endpoint/', methods=['POST'])
def login_endpoint():
    """

    """
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    name = request.form.get('name')
    password = request.form.get('password')

    cursor.execute('SELECT nme_usuario FROM usuario WHERE nme_usuario = ? AND pwd_usuario = ?', (name, password))

    resultados = cursor.fetchone()

    if resultados is not None:
        session['username'] = name

        session['logged_in'] = True
        return redirect(url_for('index'))

    flash('Usuário ou senha incorretos!')
    return redirect(url_for('login'))


@app.route('/logout/endpoint/', methods=['POST'])
def logout_endpoint():
    """
    """
    session.clear()
    return redirect(url_for('login'))


@app.route('/registro/')
def registro():
    """
    Requisição referente a página de login do site
    
    Parâmetros:


    Retorna:
    str: String da página renderizada
    """
    return render_template('registro.html')


@app.route('/registro/endpoint/', methods=['POST'])
def registro_endpoint():
    """
    """
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    try:
        name = request.form.get('name')
        password = request.form.get('password')

        cursor.execute('INSERT INTO usuario VALUES (?, ?)', (name, password))
        cursor.close()

        flash('Usuário cadastrado com sucesso, faça o login')
        return redirect(url_for('login'))

    except sqlite3.Error:
        flash('Usuário já cadastrado!')
        return redirect(url_for('registro'))

    finally:
        if conexao:
            conexao.commit()
            conexao.close()


def resolvida(num_questao):
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT 1 FROM questao_usuario WHERE fk_num_questao = ? AND fk_nme_usuario = ?', (num_questao, session['username']))
    questaoResolvida = cursor.fetchone()

    if questaoResolvida:
        return True
    else:
        return False


@app.route('/questao/', methods=['GET'])
def questao():
    """
    Recupera as questões do banco de dados
    
    Parâmetros:

    
    Retorna:
    str: String da página renderizada com uma lista de dicionários, 
    onde cada dicionário corresponde a uma tupla da tabela
    """
    if 'logged_in' in session and session['logged_in']:

        conexao = sqlite3.connect('certificadora.db')
        cursor = conexao.cursor()

        num_questao = int(request.args.get('num_questao'))

        cursor.execute('SELECT fk_num_questao FROM questao_usuario WHERE fk_nme_usuario = ?', (session['username'],))
        resposta = cursor.fetchall()
        resolvidas = tuple(item[0] for item in set(resposta))

        query = 'SELECT dif_questao FROM questao WHERE num_questao IN ({seq})'.format(
            seq=','.join(['?' for _ in resolvidas]))
        cursor.execute(query, resolvidas)

        dif_resolvidas = tuple(item[0] + 1 for item in set(cursor.fetchall()))


        dict_questao = get_dict_questao(num_questao)
        dicts_opcoes = get_dict_opcoes(num_questao)

        if dict_questao['dif_questao'] not in dif_resolvidas + (1,):
            return redirect(url_for('questoes'))

        return render_template('questao.html', dict_questao=dict_questao, dicts_opcoes=dicts_opcoes,
                               alert=resolvida(num_questao))


    else:
        flash("Voce nao esta logado!")
        return redirect(url_for('index'))


@app.route('/questoes/')
def questoes():
    if 'logged_in' in session and session['logged_in']:
        dict_questoes = get_dict_questoes()

        return render_template('questoes.html', dict_questoes=dict_questoes)
    else:
        flash("Voce nao esta logado!")
        return redirect(url_for('index'))


@app.route('/questao/endpoint/', methods=['GET'])
def questao_endpoint():
    if 'logged_in' in session and session['logged_in']:

        conexao = sqlite3.connect("certificadora.db")
        cursor = conexao.cursor()

        num_opcao = request.args.get("opcao")

        cursor.execute('SELECT bin_opcao FROM opcao WHERE num_opcao = ?', (num_opcao,))
        resposta = cursor.fetchone()

        cursor.execute('SELECT fk_num_questao FROM opcao WHERE num_opcao=?', (num_opcao,))
        num_questao = cursor.fetchone()[0]

        cursor.execute('INSERT INTO questao_usuario (fk_nme_usuario, fk_num_questao) VALUES (?, ?)',
                       (session['username'], num_questao))

        conexao.commit()

        cursor.close()
        conexao.close()

        if resposta:
            return jsonify(resposta[0]), 200, {'Content-Type': 'application/text'}
        else:
            return jsonify(None)

    else:
        flash("Voce nao esta logado!")
        return redirect(url_for('index'))


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
