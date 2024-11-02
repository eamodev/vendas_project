# Projeto para processo seletivo - INFATEC

Este projeto Django permite o upload de arquivos CSV contendo dados de vendas, realiza análises sobre as mesmas e gera gráficos e relatórios em PDF.

## Pré-requisitos

Antes de começar, verifique se você tem os seguintes requisitos instalados:

- Python 3 +
- Django
- Pandas
- Matplotlib
- WeasyPrint
- Outros pacotes mencionados no `requirements.txt`

## Instalação

1. **Clone o repositório:**

   git clone https://github.com/eamodev/vendas_project
   cd endereco_do_repositorio

2. **Crie um ambiente virtual:**

python -m venv venv
venv\Scripts\activate     # Para Windows

3. **Instale as dependências:**
pip install -r requirements.txt

4. **Configure o banco de dados:**
python manage.py migrate


## Execução
5. **Inicie o servidor de desenvolvimento Django:**
python manage.py runserver

6. **Acesse a aplicação web:**
Abra seu navegador e vá para o endereço http://127.0.0.1:8000/.



#### Instruções de Uso
- Upload de CSV: Vá para a página inicial e use o formulário para fazer o upload de um arquivo CSV com as colunas quantidade_vendida, produto, data, e preco_unitario.
- Análise de Vendas: Após o upload, você será redirecionado para uma página que apresenta os dados das vendas, gráficos e análises.
- Exportar Relatório em PDF: Você pode exportar um relatório em PDF que contém um resumo das vendas, gráficos e outras informações relevantes.



#### Estrutura geral do projeto
views.py: Contém as funções que gerenciam a lógica de upload, análise e visualização dos dados.
urls.py: Define as rotas da aplicação.
models.py: Define o modelo de dados para armazenar informações sobre vendas.
templates/: Contém os arquivos HTML usados para renderizar as páginas.
static/: Pasta para arquivos estáticos.
