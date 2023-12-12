from flask import *
import sqlite3 
import io  


def get_imagem(n_questao: int):
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
    """
    Recupera as questões armazenadas no banco de dados em um dict

    Parâmetros:

    Retorna:
    list[dict]: Um objeto dict contendo as questões
    """

    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT num_questao, dif_questao FROM questao")

    reg_questoes = cursor.fetchall()

    dicts_questoes = [{'num_questao': num_questao, 'dif_questao': dif_questao}
                      for num_questao, dif_questao in reg_questoes]

    cursor.close()
    conexao.close()

    return dicts_questoes


def get_dict_questao(num_questao: int):
    """
    Recupera uma questão específica armazenada no banco de dados em um dict

    Parâmetros:
    num_questao (int): Número da questão

    Retorna:
    dict: Um objeto dict contendo a questão
    """
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


def get_dict_opcoes(num_questao: int):
    """
    Recupera as opções das questões no banco de dados de uma questão específica
    
    Parâmetros:
    num_questao (int): Número da questão para ser encontrada as opções

    Retorna:
    list[dict]: Dicionário contendo as opções das questões
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


def resolvida(num_questao):
    """
    Testa se a questão já foi resolvida anteriormente pelo usuário

    Parâmetros:
    num_questao (int): Número da questão para ser testada se já foi resolvida

    Retorna:
    bool: True sejá foi resolvida e False caso contrário
    """

    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    cursor.execute('SELECT 1 FROM questao_usuario WHERE fk_num_questao = ? AND fk_nme_usuario = ?',
                   (num_questao, session['username']))
    questao_resolvida = cursor.fetchone()

    if questao_resolvida:
        return True
    else:
        return False


def get_login():
    """
    Realiza o login do usuário com usuário e senha, se existir no banco de dados

    Parâmetros:

    Retorna:
    Response: Redirect para a página correspondente (volta a login se não existir ou index se existir o login)
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


def get_registro_endpoint():
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    try:
        name = request.form.get('name')
        print(name)
        password = request.form.get('password')
        print(password)

        cursor.execute('INSERT INTO usuario (nme_usuario, pwd_usuario) VALUES (?, ?)', (name, password))
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


def get_questao_endpoint():
    if 'logged_in' in session and session['logged_in']:
        conexao = sqlite3.connect('certificadora.db')
        cursor = conexao.cursor()

        num_opcao = request.args.get("opcao")

        cursor.execute('SELECT bin_opcao, fk_num_questao FROM opcao WHERE num_opcao = ?', (num_opcao,))
        resposta, num_questao = cursor.fetchone()

        cursor.execute('SELECT 1 FROM questao_usuario WHERE fk_num_questao = ? AND fk_nme_usuario = ?',
                       (num_questao, session['username']))
        questao_resolvida = cursor.fetchone()

        dict_questao = get_dict_questao(num_questao)
        pts_ganhos = 0


        if resposta == 1:
            if not questao_resolvida:
                pts_ganhos = 100 if dict_questao['dif_questao'] == 1 else 250 if dict_questao['dif_questao'] == 2 else 500

            else:
                pts_ganhos = 50 if dict_questao['dif_questao'] == 1 else 125 if dict_questao['dif_questao'] == 2 else 250
        
            cursor.execute(
                'INSERT INTO questao_usuario (fk_nme_usuario, fk_num_questao, pts_questao_usuario) VALUES (?, ?, ?)',
                (session['username'], num_questao, pts_ganhos))

            cursor.execute('UPDATE usuario SET pts_usuario = pts_usuario + ? WHERE nme_usuario = ?',
                (pts_ganhos, session['username']))

        conexao.commit()

        cursor.close()
        conexao.close()

        return jsonify(resposta), 200, {'Content-Type': 'application/text'}

    else:
        flash("Você não está logado!")
        return redirect(url_for('index'))






def get_questao():
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

        cursor.close()
        conexao.close()

        return render_template('questao.html', dict_questao=dict_questao, dicts_opcoes=dicts_opcoes,
                               alert=resolvida(num_questao))

    else:
        flash("Voce nao esta logado!")
        return redirect(url_for('index'))


def get_perfil():
    conexao = sqlite3.connect('certificadora.db')
    cursor = conexao.cursor()

    subquery_result = cursor.execute('SELECT fk_num_questao FROM questao_usuario WHERE fk_nme_usuario = ?',
                                     (session['username'],)).fetchall()

    num_questao_values = [result[0] for result in subquery_result]

    cursor.execute('SELECT num_questao, pts_questao FROM questao WHERE num_questao IN ({})'
                   .format(', '.join('?' for _ in num_questao_values)), num_questao_values)

    resolvidas = cursor.fetchall()

    cursor.close()
    conexao.close()

    pontos = 0

    if 'logged_in' in session and session['logged_in']:
        conexao = sqlite3.connect('certificadora.db')
        cursor = conexao.cursor()

        cursor.execute('SELECT pts_usuario FROM usuario WHERE nme_usuario = ?', (session['username'],))
        pontos = cursor.fetchone()[0]

        cursor.close()
        conexao.close()

    return render_template('perfil.html', resolvidas=resolvidas, pontos=pontos, username=session['username'])
