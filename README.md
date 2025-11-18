# 📈 pnl-cripto

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge&logo=docker)
![Health Check](https://img.shields.io/badge/Health%20Check-Enabled-brightgreen?style=for-the-badge)
<!-- ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/pnl-cripto/main.yml?branch=main&style=for-the-badge) -->

## 📝 Descrição do Projeto

O `pnl-cripto` é uma aplicação Python desenvolvida para auxiliar no acompanhamento e cálculo de Ganhos e Perdas (P&L - Profit and Loss) relacionados a investimentos em criptomoedas. A aplicação é conteinerizada utilizando Docker, garantindo um ambiente de execução consistente e fácil de configurar.

Este projeto visa fornecer uma ferramenta simples e eficiente para gerenciar suas operações e ter uma visão clara do desempenho de seus ativos digitais.

## 🚀 Funcionalidades

- **Cálculo de P&L:** Ferramentas para calcular o lucro ou prejuízo de suas operações.
- **API RESTful:** Exposição de endpoints para interação programática (assumindo que `app.py` implementa uma API).
- **Conteinerização Docker:** Fácil implantação e portabilidade.
- **Health Check Integrado:** Monitoramento automático da saúde da aplicação via Docker.
- **Dependências Gerenciadas:** Utilização de `requirements.txt` para controle de pacotes Python.

## 🛠️ Tecnologias Utilizadas

- **Python 3.9:** Linguagem de programação principal.
- **Flask/FastAPI (ou similar):** Framework web para a API (assumido pelo `app.py` e porta 5000).
- **Docker:** Para conteinerização da aplicação.
- **`pip`:** Gerenciador de pacotes Python.
- **`curl`:** Ferramenta utilizada no health check.

## ⚙️ Como Começar

Siga estas instruções para configurar e executar o projeto localmente.

### Pré-requisitos

Certifique-se de ter o Docker instalado em sua máquina:

- Docker Desktop

### Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/michelwanderson/pnl-cripto
    cd pnl-cripto
    ```

2.  **Construa a imagem Docker:**
    ```bash
    docker build -t pnl-cripto:latest .
    ```

3.  **Execute o contêiner Docker:**
    ```bash
    docker run -p 5000:5000 pnl-cripto:latest
    ```

    A aplicação estará disponível em `http://localhost:5000`.

## 🩺 Health Check

O Dockerfile inclui um `HEALTHCHECK` que verifica a disponibilidade da aplicação. Você pode monitorar o status de saúde do contêiner usando comandos Docker:

```bash
docker ps
```

A coluna `STATUS` mostrará `(healthy)` ou `(unhealthy)` após o período de inicialização.

O health check tenta acessar a rota `/health` na porta `5000` do contêiner. Certifique-se de que seu `app.py` tenha um endpoint `/health` que retorne um status 200 OK.

Exemplo de como o endpoint `/health` pode ser implementado em `app.py` (usando Flask):

```python
# app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# ... outras rotas da sua aplicação

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🤝 Contribuição

Contribuições são bem-vindas! Se você tiver sugestões, melhorias ou encontrar bugs, por favor, abra uma `issue` ou envie um `pull request`.

1.  Faça um fork do projeto.
2.  Crie uma nova branch (`git checkout -b feature/AmazingFeature`).
3.  Faça suas alterações e commit (`git commit -m 'Add some AmazingFeature'`).
4.  Envie para a branch original (`git push origin feature/AmazingFeature`).
5.  Abra um Pull Request.

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## ✉️ Contato

MichelWanderson  - wanderson.michel.cs@gmail.com

Link do Projeto: https://github.com/michelwanderson/pnl-cripto
