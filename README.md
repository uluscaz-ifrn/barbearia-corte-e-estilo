# Sistema de Agendamento para Barbearia - Projeto Integrado Individual (ADS)

Este projeto foi desenvolvido como entregável do **Projeto Integrado Interdisciplinar** do curso de **Análise e Desenvolvimento de Sistemas (ADS)**.

Trata-se de uma aplicação web completa desenvolvida com **Python**, framework **Flask** e banco de dados relacional **SQLite**, com interface responsiva construída em **Bootstrap 5**.

---

## Funcionalidades Implementadas

1. **Agenda do Dia & Painel de Controle (Dashboard):**
   - Visualização dos horários marcados por data.
   - Filtro de agenda em tempo real por data selecionada.
   - Resumo com métricas diárias: total de agendamentos, clientes confirmados e previsão de faturamento.
   - Ação de cancelamento de agendamentos.

2. **Cadastro e Gestão de Clientes (Funcionalidade 1):**
   - Cadastro de novos clientes com validação de campos obrigatórios (nome e telefone).
   - Listagem completa dos clientes cadastrados e data de registro.

3. **Novo Agendamento com Conflito de Horário (Funcionalidade 2):**
   - Agendamento de atendimentos associando cliente, profissional (barbeiro), serviço, data e horário.
   - **Regra de Negócio Crítica:** Validação que impede agendamentos simultâneos para o mesmo profissional na mesma data e horário.

4. **Catálogo de Serviços:**
   - Cadastro e listagem de serviços oferecidos com respectivo preço e tempo de duração.

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.12
- **Framework Web:** Flask 3.1.0
- **Banco de Dados:** SQLite 3
- **Frontend / UI:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons
- **Controle de Versão:** Git

---

## Como Executar o Projeto

### 1. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 2. Inicializar o Banco de Dados (Opcional, pois é criado automaticamente)
```bash
python database.py
```

### 3. Executar o Servidor Flask
```bash
python app.py
```
Acesse no seu navegador: `http://127.0.0.1:5000`

---

## Como Executar os Casos de Teste (Fase 5)

Para validar automaticamente os 5 casos de teste previstos na especificação do projeto acadêmico:
```bash
python test_app.py
```

Resultados cobertos:
- **CT01:** Cadastro de cliente com dados válidos.
- **CT02:** Validação e bloqueio de cadastro com campos obrigatórios em branco.
- **CT03:** Registro de agendamento em horário vago com persistência relacional.
- **CT04:** Validação de conflito de horário impedindo agendamento duplicado para o mesmo profissional.
- **CT05:** Consulta e filtro de agendamentos por data.
