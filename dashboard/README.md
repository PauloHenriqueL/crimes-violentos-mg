# 📊 Execução do Painel Interativo (Streamlit)

[cite_start]Esta pasta contém a aplicação web desenvolvida em **Streamlit** para visualização interativa do modelo relacional e das consultas estatísticas sobre Crimes Violentos em MG (2025-2026)[cite: 8, 18].

A aplicação foi isolada nesta subpasta para manter a integridade estrutural do repositório acadêmico principal.

---

## 🚀 Como Rodar Localmente no Windows

Siga os passos abaixo a partir do seu terminal de preferência (CMD ou PowerShell).

### 1. Navegar até a pasta do Dashboard
Abra o terminal na raiz do projeto e mude para o diretório da aplicação:
```cmd
cd dashboard

### 2. Criar e Ativar o Ambiente Virtual (env)
Para garantir o isolamento das dependências desta interface:

Criar o ambiente (caso ainda não o tenha feito nesta subpasta):
python -m venv env

Ativar no CMD:
env\Scripts\activate.bat

Ativar no PowerShell:
.\env\Scripts\Activate.ps1

(Você saberá que funcionou quando o prefixo (env) aparecer no início do prompt).

### 3. Instalar os Requisitos
Com o ambiente ativado, instale as bibliotecas necessárias listadas no manifesto:

pip install -r requirements.txt

## 4. Executar o Aplicativo
Inicie o servidor de desenvolvimento local:
streamlit run app.py

O navegador abrirá automaticamente em http://localhost:8501.
