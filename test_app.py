"""
Script de Testes Automatizados para Evidência do Projeto Integrado
Cobre os 5 casos de teste obrigatórios (CT01 a CT05)
"""
import unittest
from datetime import date
from app import app
from database import get_db_connection, init_db

class BarbeariaSystemTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        init_db()

    def test_ct01_cadastro_cliente_dados_validos(self):
        """CT01: Cadastro de cliente com dados válidos."""
        payload = {
            "nome": "Fernando Souza Teste",
            "telefone": "(11) 91234-5678",
            "email": "fernando.teste@email.com"
        }
        response = self.client.post("/clientes", data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("cadastrado com sucesso", response.get_data(as_text=True))
        
        # Verifica no banco de dados SQLite
        conn = get_db_connection()
        cliente = conn.execute("SELECT * FROM clientes WHERE nome = ?", ("Fernando Souza Teste",)).fetchone()
        conn.close()
        self.assertIsNotNone(cliente)
        print("\n[OK] CT01 - Cadastro de cliente válido realizado com persistência no banco SQLite.")

    def test_ct02_cadastro_cliente_dados_invalidos(self):
        """CT02: Cadastro de cliente sem preencher nome ou telefone."""
        payload = {
            "nome": "",  # Vazio propositalmente
            "telefone": "",
            "email": "invalido@email.com"
        }
        response = self.client.post("/clientes", data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Os campos Nome e Telefone são obrigatórios", response.get_data(as_text=True))
        print("[OK] CT02 - Validação de campos obrigatórios impediu cadastro inconsistente.")

    def test_ct03_agendamento_dados_validos(self):
        """CT03: Agendamento com dados válidos em horário livre."""
        conn = get_db_connection()
        cliente = conn.execute("SELECT id FROM clientes LIMIT 1").fetchone()
        prof = conn.execute("SELECT id FROM profissionais LIMIT 1").fetchone()
        serv = conn.execute("SELECT id FROM servicos LIMIT 1").fetchone()
        conn.close()

        data_teste = "2026-11-15"
        hora_teste = "14:00"

        payload = {
            "cliente_id": cliente["id"],
            "profissional_id": prof["id"],
            "servico_id": serv["id"],
            "data_agendamento": data_teste,
            "hora_agendamento": hora_teste,
            "observacoes": "Teste de agendamento válido"
        }
        response = self.client.post("/agendamentos/novo", data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Agendamento cadastrado com sucesso", response.get_data(as_text=True))
        print("[OK] CT03 - Agendamento registrado com sucesso e associado ao banco de dados.")

    def test_ct04_conflito_de_horario(self):
        """CT04: Tentativa de agendar mesmo profissional no mesmo dia e horário já ocupado."""
        conn = get_db_connection()
        cliente = conn.execute("SELECT id FROM clientes LIMIT 1").fetchone()
        prof = conn.execute("SELECT id FROM profissionais LIMIT 1").fetchone()
        serv = conn.execute("SELECT id FROM servicos LIMIT 1").fetchone()
        conn.close()

        data_teste = "2026-11-20"
        hora_teste = "10:00"

        # Primeiro agendamento (ocupa o horário)
        self.client.post("/agendamentos/novo", data={
            "cliente_id": cliente["id"],
            "profissional_id": prof["id"],
            "servico_id": serv["id"],
            "data_agendamento": data_teste,
            "hora_agendamento": hora_teste,
            "observacoes": "Primeiro agendamento"
        }, follow_redirects=True)

        # Segundo agendamento tentando marcar o mesmo profissional no mesmo dia e hora
        response = self.client.post("/agendamentos/novo", data={
            "cliente_id": cliente["id"],
            "profissional_id": prof["id"],
            "servico_id": serv["id"],
            "data_agendamento": data_teste,
            "hora_agendamento": hora_teste,
            "observacoes": "Tentativa conflitante"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Conflito de Horário", response.get_data(as_text=True))
        print("[OK] CT04 - Sistema identificou conflito de agenda e impediu duplicidade com sucesso.")

    def test_ct05_consulta_agenda_por_data(self):
        """CT05: Consulta e filtro de agendamentos por data."""
        data_filtro = "2026-11-15"
        response = self.client.get(f"/?data={data_filtro}")
        self.assertEqual(response.status_code, 200)
        texto = response.get_data(as_text=True)
        self.assertIn("Painel de Agendamentos", texto)
        self.assertIn(data_filtro, texto)
        print("[OK] CT05 - Consulta filtrada de agendamentos por data funcionando perfeitamente.")

if __name__ == "__main__":
    unittest.main()
