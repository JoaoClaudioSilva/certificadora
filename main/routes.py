from flask import *  # Cria aplicações web

import database
from flask_session.__init__ import Session

app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.secret_key = 'your_secret_key'


@app.route('/imagens/imagem_<int:n_questao>')
def imagem(n_questao):
    """
    Recupera a imagem BLOB no banco de dados referente a questão, se houver
    
    Parâmetros:
    n_questao (int): O número da questão (num_questao) no banco de dados
    
    Retorna:
    Response ou None: Um objeto Flask contendo a imagem JPEG, ou None, caso não haja imagem
    """

    return database.get_imagem(n_questao)


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
    return database.get_login()


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
    return database.get_registro_endpoint()


@app.route('/questoes/')
def questoes():
    if 'logged_in' in session and session['logged_in']:
        dict_questoes = database.get_dict_questoes()

        return render_template('questoes.html', dict_questoes=dict_questoes)
    else:
        flash("Voce nao esta logado!")
        return redirect(url_for('index'))


@app.route('/questao/endpoint/', methods=['GET'])
def questao_endpoint():
    return database.get_questao_endpoint()


@app.route('/')
def index():
    """
    Requisição referente a página inicial do site
    
    Parâmetros:

    
    Retorna:
    str: String da página renderizada
    """
    return render_template('index.html')


@app.route('/questao/', methods=['GET'])
def questao():
    return database.get_questao()


@app.route('/perfil/', methods=['GET'])
def perfil():
    return database.get_perfil()
