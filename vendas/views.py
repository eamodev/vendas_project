import csv
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from .forms import UploadCSVForm
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS
from .models import Venda
from django.db.models import Sum, Count
from collections import Counter
from django.core.paginator import Paginator


# Função para renderizar a página inicial
def home_view(request):
    return render(request, 'home.html')

# Função de upload e análise do CSV
def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                try:
                    # Ler o arquivo CSV
                    df = pd.read_csv(uploaded_file)
                    required_columns = ['quantidade_vendida', 'produto', 'data', 'preco_unitario']
                    for column in required_columns:
                        if column not in df.columns:
                            form.add_error(None, f"O arquivo CSV deve conter a coluna '{column}'.")
                            return render(request, 'upload_csv.html', {'form': form})

                    # Calcular preco_total
                    df['preco_total'] = df['quantidade_vendida'] * df['preco_unitario']

                    # Armazenar os dados necessários em sessão para uso posterior
                    request.session['tabela_vendas'] = df.to_dict(orient='records')
                    
                    # Convertendo valores para tipos padrão do Python
                    request.session['total_vendas'] = int(df['quantidade_vendida'].sum())  # Convertendo para int
                    request.session['receita_total'] = float(df['preco_total'].sum())  # Convertendo para float
                    request.session['produto_mais_vendido'] = df.groupby('produto')['quantidade_vendida'].sum().idxmax()

                    # Redireciona para a página de listagem
                    return redirect('listagem')

                except Exception as e:
                    form.add_error(None, f"Ocorreu um erro: {str(e)}")
                    return render(request, 'upload_csv.html', {'form': form})
    else:
        form = UploadCSVForm()
    return render(request, 'upload_csv.html', {'form': form})

# Função para gerar gráfico de receita por produto
def grafico_receita_por_produto(df):
    receita_por_produto = df.groupby('produto')['preco_total'].sum().reset_index()
    plt.figure(figsize=(8, 3))
    plt.bar(receita_por_produto['produto'], receita_por_produto['preco_total'], color='skyblue')
    plt.xlabel('Produto')
    plt.ylabel('Receita Total')
    plt.title('Receita Total por Produto')
    plt.xticks(rotation=0, fontsize=8)

    # Salvando o gráfico em memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Função para gerar gráfico de evolução das vendas
def grafico_evolucao_vendas(df):
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    vendas_por_data = df.groupby('data')['quantidade_vendida'].sum().reset_index()

    plt.figure(figsize=(8, 3))
    plt.plot(vendas_por_data['data'], vendas_por_data['quantidade_vendida'], marker='o', color='skyblue')
    plt.xlabel('Data')
    plt.ylabel('Quantidade Vendida')
    plt.title('Evolução das Vendas ao Longo do Tempo')
    plt.xticks(rotation=0, fontsize=8)

    # Salvando o gráfico em memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Função para exibir a listagem de vendas
def listagem(request):
    # Verifica se há dados da tabela de vendas na sessão
    tabela_vendas = request.session.get('tabela_vendas', [])
    
    # Se a tabela estiver vazia, redireciona para a página de upload
    #if not tabela_vendas:
        #return redirect('upload_csv')

    return render(request, 'listagem.html', {'tabela_vendas': tabela_vendas})

def listagem(request):
    # Obter todas as vendas inicialmente
    vendas = Venda.objects.all()

    # Filtragem por intervalo de datas
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    produto = request.GET.get('produto')

    if data_inicial and data_final:
        vendas = vendas.filter(data__range=[data_inicial, data_final])

    if produto:
        vendas = vendas.filter(produto__icontains=produto)

    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'data')  # 'data' ou 'valor_total'
    if ordenacao == 'valor_total':
        vendas = vendas.order_by('-preco_total')  # Ordem decrescente
    else:
        vendas = vendas.order_by('data')  # Ordem crescente

    # Paginação
    paginator = Paginator(vendas, 20)  # Exibir 20 vendas por página
    page_number = request.GET.get('page')
    vendas_paginated = paginator.get_page(page_number)

    context = {
        'vendas': vendas_paginated,
        'data_inicial': data_inicial,
        'data_final': data_final,
        'produto': produto,
        'ordenacao': ordenacao,
        'paginator': paginator
    }
    
    return render(request, 'listagem.html', context)

def analise_vendas(request):
    # Resumo estatístico
    total_vendas = Venda.objects.count()  # Total de vendas
    receita_total = Venda.objects.aggregate(Sum('preco_total'))['preco_total__sum'] or 0  # Receita total

    # Produto mais vendido
    produto_mais_vendido = (
        Venda.objects.values('produto')
        .annotate(total_vendido=Sum('quantidade_vendida'))
        .order_by('-total_vendido')
    ).first()

    if produto_mais_vendido:
        produto_mais_vendido_nome = produto_mais_vendido['produto']
        quantidade_vendida = produto_mais_vendido['total_vendido']
    else:
        produto_mais_vendido_nome = None
        quantidade_vendida = 0

    context = {
        'total_vendas': total_vendas,
        'receita_total': receita_total,
        'produto_mais_vendido_nome': produto_mais_vendido_nome,
        'quantidade_vendida': quantidade_vendida,
    }

    return render(request, 'analise_vendas.html', context)

# Função para gerar gráfico de vendas
def grafico_vendas(request):
    if 'tabela_vendas' in request.session:
        df = pd.DataFrame(request.session['tabela_vendas'])
        grafico_receita = grafico_receita_por_produto(df)
        evolucao = grafico_evolucao_vendas(df)

        context = {
            'grafico_receita': grafico_receita,
            'evolucao': evolucao,
            'total_vendas': request.session.get('total_vendas'),
            'receita_total': request.session.get('receita_total'),
            'produto_mais_vendido': request.session.get('produto_mais_vendido'),
        }
        return render(request, 'grafico_vendas.html', context)
    else:
        # Se não houver dados, redireciona para o upload_csv
        return render(request, 'upload_csv.html', {'form': UploadCSVForm()})


# Função para exportar o relatório em PDF
def exportar_pdf(request):
    vendas = Venda.objects.all()  # Pega todas as vendas

    # Calcular total de vendas e receita total
    total_vendas = vendas.count()
    receita_total = sum(venda.preco_total for venda in vendas)  # Certifique-se de que 'preco_total' é um campo válido do modelo

    # Calcular produto mais vendido
    produtos_vendidos = [venda.produto for venda in vendas]  # Aqui estamos assumindo que 'produto' é um campo do modelo
    contagem_produtos = Counter(produtos_vendidos)
    produto_mais_vendido = contagem_produtos.most_common(1)[0][0] if contagem_produtos else 'N/A'

    # Converter o QuerySet para um DataFrame do Pandas
    df = pd.DataFrame(list(vendas.values()))

    # Gráficos
    grafico_receita = grafico_receita_por_produto(df)  # Usando o DataFrame
    evolucao_vendas = grafico_evolucao_vendas(df)  # Usando o DataFrame

    # Criar o contexto para o template PDF
    context = {
        'total_vendas': total_vendas,
        'receita_total': receita_total,
        'produto_mais_vendido': produto_mais_vendido,
        'grafico_receita': grafico_receita,
        'evolucao_vendas': evolucao_vendas,
    }

    # Passando request para a função render_to_pdf
    pdf = render_to_pdf(request, 'relatorio_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_vendas.pdf"'
        return response
    return redirect('home')

def grafico_receita_por_produto(df):
    receita_por_produto = df.groupby('produto')['preco_total'].sum().reset_index()
    plt.figure(figsize=(10, 5))
    plt.bar(receita_por_produto['produto'], receita_por_produto['preco_total'], color='skyblue')
    plt.xlabel('Produto')
    plt.ylabel('Receita Total')
    plt.title('Receita Total por Produto')
    plt.xticks(rotation=0, fontsize=8)

    # Salvando o gráfico em memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def grafico_evolucao_vendas(df):
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    vendas_por_data = df.groupby('data')['quantidade_vendida'].sum().reset_index()

    plt.figure(figsize=(10, 5))
    plt.plot(vendas_por_data['data'], vendas_por_data['quantidade_vendida'], marker='o', color='skyblue')
    plt.xlabel('Data')
    plt.ylabel('Quantidade Vendida')
    plt.title('Evolução das Vendas ao Longo do Tempo')

    # Salvando o gráfico em memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Função para renderizar PDF
def render_to_pdf(request, template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    
    # Definindo os estilos para o PDF
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[CSS(string='@page { size: A4 landscape; margin: 1cm; }')]
    )
    return pdf