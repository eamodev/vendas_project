# vendas/analysis.py
from .models import Venda
import matplotlib.pyplot as plt
from .models import Venda
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect
import pandas as pd
import os 
from django.db.models import Sum


def resumo_estatistico():
    vendas = Venda.objects.all()
    total_vendas = vendas.count()
    receita_total = sum(venda.preco_total for venda in vendas)
    produto_mais_vendido = vendas.order_by('-quantidade_vendida').first().produto
    
    return {
        'total_vendas': total_vendas,
        'receita_total': receita_total,
        'produto_mais_vendido': produto_mais_vendido,
    }

#Gráficos com matplotlib
def receita_por_produto():
    vendas = Venda.objects.values('produto').annotate(receita_total=Sum('preco_total'))
    produtos = [venda['produto'] for venda in vendas]
    receitas = [venda['receita_total'] for venda in vendas]

    plt.bar(produtos, receitas)
    plt.title("Receita por Produto")
    plt.xlabel("Produto")
    plt.ylabel("Receita")
    plt.savefig("receita_por_produto.png")

   #Gerar relatório em pdf
def gerar_relatorio():
    c = canvas.Canvas("relatorio_vendas.pdf", pagesize=letter)
    c.drawString(100, 750, "Resumo Estatístico de Vendas")
    resumo = resumo_estatistico()
    c.drawString(100, 730, f"Total de Vendas: {resumo['total_vendas']}")
    c.drawString(100, 710, f"Receita Total: {resumo['receita_total']}")
    c.drawString(100, 690, f"Produto mais Vendido: {resumo['produto_mais_vendido']}")
    c.showPage()
    c.save() 

#Gráficos
def analise_vendas(request):
    # Extraindo dados do banco de dados
    vendas_queryset = Venda.objects.all().values()
    vendas_df = pd.DataFrame(list(vendas_queryset))
    
    # Análises Básicas
    total_vendas = vendas_df['quantidade_vendida'].sum()
    total_preco = (vendas_df['quantidade_vendida'] * vendas_df['preco_unitario']).sum()

    # Vendas por Produto
    vendas_por_produto = vendas_df.groupby('produto').agg(
        total_vendido=pd.NamedAgg(column='quantidade_vendida', aggfunc='sum'),
        total_preco=pd.NamedAgg(column='quantidade_vendida', aggfunc=lambda x: (x * vendas_df.loc[x.index, 'preco_unitario']).sum())
    ).reset_index()

    # Gráfico de Vendas por Produto
    plt.figure(figsize=(10, 5))
    plt.bar(vendas_por_produto['produto'], vendas_por_produto['total_vendido'], color='blue')
    plt.title('Vendas por Produto')
    plt.xlabel('Produto')
    plt.ylabel('Total Vendido')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Salvar o gráfico
    chart_path = os.path.join('static', 'vendas_por_produto.png')
    plt.savefig(chart_path)
    plt.close()

    return render(request, 'analise_vendas.html', {
        'total_vendas': total_vendas,
        'total_preco': total_preco,
        'vendas_por_produto': vendas_por_produto.to_html(classes='table table-striped', index=False),
        'chart_path': chart_path
    })