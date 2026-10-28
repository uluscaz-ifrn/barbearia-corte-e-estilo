import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "barbearia-projeto-integrado-secret-key"

# Inicializa o banco de dados na inicialização do servidor
init_db()

@app.route("/")
def index():
    """Tela 1: Painel Geral e Agenda do Dia."""
    data_filtro = request.args.get("data", date.today().strftime("%Y-%m-%d"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Consulta relacionando Agendamentos com Clientes, Profissionais e Serviços
    cursor.execute("""
        SELECT 
            a.id,
            a.data_agendamento,
            a.hora_agendamento,
            a.status,
            a.observacoes,
            c.nome AS cliente_nome,
            c.telefone AS cliente_telefone,
            p.nome AS profissional_nome,
            s.nome AS servico_nome,
            s.preco AS servico_preco,
            s.duracao_min AS servico_duracao
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN profissionais p ON a.profissional_id = p.id
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.data_agendamento = ?
        ORDER BY a.hora_agendamento ASC
    """, (data_filtro,))
    agendamentos = cursor.fetchall()
    
    # Métricas do dia para o painel
    total_agendamentos = len(agendamentos)
    total_ativos = sum(1 for a in agendamentos if a["status"] != "Cancelado")
    faturamento_previsto = sum(a["servico_preco"] for a in agendamentos if a["status"] != "Cancelado")
    
    conn.close()
    
    return render_template(
        "index.html", 
        agendamentos=agendamentos, 
        data_filtro=data_filtro,
        total_agendamentos=total_agendamentos,
        total_ativos=total_ativos,
        faturamento_previsto=faturamento_previsto
    )

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    """Tela 2 / Funcionalidade 1: Cadastro e Listagem de Clientes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip()
        
        # Validação de obrigatoriedade
        if not nome or not telefone:
            flash("Erro: Os campos Nome e Telefone são obrigatórios!", "danger")
            conn.close()
            return redirect(url_for("clientes"))
        
        try:
            cursor.execute("""
                INSERT INTO clientes (nome, telefone, email) 
                VALUES (?, ?, ?)
            """, (nome, telefone, email))
            conn.commit()
            flash(f"Cliente '{nome}' cadastrado com sucesso!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao cadastrar cliente: {str(e)}", "danger")
        finally:
            conn.close()
            
        return redirect(url_for("clientes"))
        
    cursor.execute("SELECT * FROM clientes ORDER BY nome ASC")
    lista_clientes = cursor.fetchall()
    conn.close()
    
    return render_template("clientes.html", clientes=lista_clientes)

@app.route("/agendamentos/novo", methods=["GET", "POST"])
def novo_agendamento():
    """Tela 3 / Funcionalidade 2: Novo Agendamento com Verificação de Conflito de Horário."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        profissional_id = request.form.get("profissional_id")
        servico_id = request.form.get("servico_id")
        data_agendamento = request.form.get("data_agendamento")
        hora_agendamento = request.form.get("hora_agendamento")
        observacoes = request.form.get("observacoes", "").strip()
        
        # Validação de campos obrigatórios
        if not all([cliente_id, profissional_id, servico_id, data_agendamento, hora_agendamento]):
            flash("Erro: Todos os campos obrigatórios devem ser preenchidos!", "danger")
            conn.close()
            return redirect(url_for("novo_agendamento"))
            
        # Regra de Negócio: Verificar conflito de agenda do profissional no mesmo dia e horário
        cursor.execute("""
            SELECT id FROM agendamentos 
            WHERE profissional_id = ? 
              AND data_agendamento = ? 
              AND hora_agendamento = ? 
              AND status != 'Cancelado'
        """, (profissional_id, data_agendamento, hora_agendamento))
        
        conflito = cursor.fetchone()
        if conflito:
            flash("Conflito de Horário: Este profissional já possui um agendamento marcado para esta data e horário!", "warning")
            conn.close()
            return redirect(url_for("novo_agendamento"))
            
        # Insere o agendamento no banco
        try:
            cursor.execute("""
                INSERT INTO agendamentos (cliente_id, profissional_id, servico_id, data_agendamento, hora_agendamento, observacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cliente_id, profissional_id, servico_id, data_agendamento, hora_agendamento, observacoes))
            conn.commit()
            flash("Agendamento cadastrado com sucesso!", "success")
            conn.close()
            return redirect(url_for("index", data=data_agendamento))
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao registrar agendamento: {str(e)}", "danger")
            conn.close()
            return redirect(url_for("novo_agendamento"))
            
    # GET: Carrega dados para os selects da interface
    cursor.execute("SELECT id, nome, telefone FROM clientes ORDER BY nome ASC")
    clientes_list = cursor.fetchall()
    
    cursor.execute("SELECT id, nome, especialidade FROM profissionais ORDER BY nome ASC")
    profissionais_list = cursor.fetchall()
    
    cursor.execute("SELECT id, nome, preco, duracao_min FROM servicos ORDER BY nome ASC")
    servicos_list = cursor.fetchall()
    
    hoje = date.today().strftime("%Y-%m-%d")
    conn.close()
    
    return render_template(
        "novo_agendamento.html", 
        clientes=clientes_list,
        profissionais=profissionais_list,
        servicos=servicos_list,
        hoje=hoje
    )

@app.route("/agendamentos/cancelar/<int:id>", methods=["POST"])
def cancelar_agendamento(id):
    """Cancela um agendamento existente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT data_agendamento FROM agendamentos WHERE id = ?", (id,))
    item = cursor.fetchone()
    data_retorno = item["data_agendamento"] if item else date.today().strftime("%Y-%m-%d")
    
    cursor.execute("UPDATE agendamentos SET status = 'Cancelado' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    flash("Agendamento cancelado com sucesso!", "info")
    return redirect(url_for("index", data=data_retorno))

@app.route("/servicos", methods=["GET", "POST"])
def servicos():
    """Tela 4: Catálogo e Gerenciamento de Serviços."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco = request.form.get("preco", "").strip()
        duracao_min = request.form.get("duracao_min", "").strip()
        
        if not nome or not preco or not duracao_min:
            flash("Preencha todos os campos do serviço!", "danger")
            conn.close()
            return redirect(url_for("servicos"))
            
        try:
            cursor.execute("""
                INSERT INTO servicos (nome, preco, duracao_min)
                VALUES (?, ?, ?)
            """, (nome, float(preco.replace(",", ".")), int(duracao_min)))
            conn.commit()
            flash(f"Serviço '{nome}' adicionado com sucesso!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao cadastrar serviço: {str(e)}", "danger")
        finally:
            conn.close()
            
        return redirect(url_for("servicos"))
        
    cursor.execute("SELECT * FROM servicos ORDER BY preco ASC")
    lista_servicos = cursor.fetchall()
    conn.close()
    
    return render_template("servicos.html", servicos=lista_servicos)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
