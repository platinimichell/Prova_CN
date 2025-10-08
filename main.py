from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuração do banco de dados (Azure)
db_config = {
    'host': 'server-bd-cn1.mysql.database.azure.com',
    'user': 'useradmin',
    'password': 'admin@123',
    'database': 'michell_db'
}

# Função para conectar ao banco de dados
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Página inicial com listagem de veículos
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM veiculos')
    veiculos = cursor.fetchall()
    conn.close()
    return render_template('index.html', veiculos=veiculos)

# Página de cadastro de veículos
@app.route('/adicionar_veiculo', methods=['GET', 'POST'])
def adicionar_veiculo():
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        placa = request.form['placa']
        preco = request.form['preco']
        disponibilidade = 'disponivel' in request.form

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO veiculos (marca, modelo, ano, placa, preco, disponibilidade) VALUES (%s, %s, %s, %s, %s, %s)',
                       (marca, modelo, ano, placa, preco, disponibilidade))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('adicionar_veiculo.html')

# Página de edição de veículos
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_veiculo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM veiculos WHERE id = %s', (id,))
    veiculo = cursor.fetchone()

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        placa = request.form['placa']
        preco = request.form['preco']
        disponibilidade = 'disponivel' in request.form

        cursor.execute('UPDATE veiculos SET marca = %s, modelo = %s, ano = %s, placa = %s, preco = %s, disponibilidade = %s WHERE id = %s',
                       (marca, modelo, ano, placa, preco, disponibilidade, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('editar_veiculo.html', veiculo=veiculo)

# Página de exclusão de veículos
@app.route('/excluir/<int:id>', methods=['GET'])
def excluir_veiculo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM veiculos WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# Rota para listar todos os clientes
@app.route('/clientes')
def listar_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)


# Rota para cadastrar um novo cliente
@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clientes (nome, email, telefone, endereco) VALUES (%s, %s, %s, %s)', 
                       (nome, email, telefone, endereco))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_clientes'))
    return render_template('adicionar_cliente.html')

# Rota para editar as informações de um cliente
@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
    cliente = cursor.fetchone()
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        
        cursor.execute('UPDATE clientes SET nome = %s, email = %s, telefone = %s, endereco = %s WHERE id = %s',
                       (nome, email, telefone, endereco, id))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_clientes'))
    
    conn.close()
    return render_template('editar_cliente.html', cliente=cliente)

# Rota para excluir um cliente
@app.route('/excluir_cliente/<int:id>', methods=['POST'])
def excluir_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('listar_clientes'))

# Rota para visualizar o histórico de locações de um cliente
@app.route('/historico_locacoes/<int:id>')
def historico_locacoes(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT l.data_inicio, l.data_fim, v.marca, v.modelo
                      FROM historico_locacoes l
                      JOIN veiculos v ON l.veiculo_id = v.id
                      WHERE l.cliente_id = %s''', (id,))
    locacoes = cursor.fetchall()
    conn.close()
    return render_template('historico_locacoes.html', locacoes=locacoes)


@app.route('/adicionar_locacao', methods=['GET', 'POST'])
def adicionar_locacao():
    if request.method == 'GET':
        # Buscar todos os veículos e clientes para o formulário
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM veiculos')
        veiculos = cursor.fetchall()
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()
        conn.close()
        return render_template('adicionar_locacao.html', veiculos=veiculos, clientes=clientes)

    # Se for uma requisição POST (formulário enviado)
    veiculo_id = request.form['veiculo_id']
    cliente_id = request.form['cliente_id']
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']
    valor = request.form['valor']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO locacoes (veiculo_id, cliente_id, data_inicio, data_fim, valor) VALUES (%s, %s, %s, %s, %s)',
                   (veiculo_id, cliente_id, data_inicio, data_fim, valor))
    conn.commit()
    conn.close()

    return redirect('/locacoes')

@app.route('/locacoes')
def locacoes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT locacoes.id, veiculos.modelo, clientes.nome, locacoes.data_inicio, locacoes.data_fim, locacoes.valor FROM locacoes '
                   'JOIN veiculos ON locacoes.veiculo_id = veiculos.id '
                   'JOIN clientes ON locacoes.cliente_id = clientes.id')
    locacoes = cursor.fetchall()
    conn.close()
    return render_template('locacoes.html', locacoes=locacoes)


@app.route('/editar_locacao/<int:id>', methods=['GET', 'POST'])
def editar_locacao(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM locacoes WHERE id = %s', (id,))
        locacao = cursor.fetchone()
        cursor.execute('SELECT * FROM veiculos')
        veiculos = cursor.fetchall()
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()
        conn.close()
        return render_template('editar_locacao.html', locacao=locacao, veiculos=veiculos, clientes=clientes)

    # Se for POST (formulário enviado)
    veiculo_id = request.form['veiculo_id']
    cliente_id = request.form['cliente_id']
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']
    valor = request.form['valor']

    cursor.execute('UPDATE locacoes SET veiculo_id = %s, cliente_id = %s, data_inicio = %s, data_fim = %s, valor = %s WHERE id = %s',
                   (veiculo_id, cliente_id, data_inicio, data_fim, valor, id))
    conn.commit()
    conn.close()

    return redirect('/locacoes')

@app.route('/excluir_locacao/<int:id>', methods=['POST'])
def excluir_locacao(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM locacoes WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect('/locacoes')



if __name__ == '__main__':
    app.run(debug=True)