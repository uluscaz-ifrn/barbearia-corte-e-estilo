import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "barbearia.db")

def get_db_connection():
    """Retorna uma conexão ativa com o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados e insere dados padrão caso estejam vazias."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabela de Clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Tabela de Profissionais (Barbeiros)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profissionais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        especialidade TEXT NOT NULL,
        telefone TEXT
    );
    """)

    # 3. Tabela de Serviços
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        duracao_min INTEGER NOT NULL
    );
    """)

    # 4. Tabela de Agendamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        profissional_id INTEGER NOT NULL,
        servico_id INTEGER NOT NULL,
        data_agendamento TEXT NOT NULL,
        hora_agendamento TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Agendado',
        observacoes TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
        FOREIGN KEY (profissional_id) REFERENCES profissionais (id) ON DELETE CASCADE,
        FOREIGN KEY (servico_id) REFERENCES servicos (id) ON DELETE CASCADE
    );
    """)

    # Inserção de dados iniciais para teste (Seeds) caso não existam
    cursor.execute("SELECT COUNT(*) as count FROM profissionais;")
    if cursor.fetchone()["count"] == 0:
        cursor.executemany("""
            INSERT INTO profissionais (nome, especialidade, telefone) 
            VALUES (?, ?, ?);
        """, [
            ("Carlos Silva", "Barbeiro Master - Cortes Clássicos", "(11) 98765-4321"),
            ("Marcos Santos", "Especialista em Degradê e Barba", "(11) 99876-5432")
        ])

    cursor.execute("SELECT COUNT(*) as count FROM servicos;")
    if cursor.fetchone()["count"] == 0:
        cursor.executemany("""
            INSERT INTO servicos (nome, preco, duracao_min) 
            VALUES (?, ?, ?);
        """, [
            ("Corte Masculino Clássico", 45.00, 30),
            ("Barba Completa com Toalha Quente", 35.00, 30),
            ("Combo: Cabelo + Barba", 70.00, 50),
            ("Acabamento / Pezinho", 20.00, 15)
        ])

    cursor.execute("SELECT COUNT(*) as count FROM clientes;")
    if cursor.fetchone()["count"] == 0:
        cursor.executemany("""
            INSERT INTO clientes (nome, telefone, email) 
            VALUES (?, ?, ?);
        """, [
            ("Lucas Oliveira", "(11) 97777-1111", "lucas@email.com"),
            ("Gabriel Souza", "(11) 98888-2222", "gabriel@email.com")
        ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados SQLite 'barbearia.db' inicializado com sucesso!")
