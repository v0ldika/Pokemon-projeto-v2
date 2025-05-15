import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração do estilo dos gráficos
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['font.size'] = 12

# Carregar os dados
pokemon_df = pd.read_csv('pokeapi_pokemon.csv')

# TIPOS DE POKEMON
# Processar os tipos (que estão como strings separadas por vírgula)
types = pokemon_df['types'].str.split(', ', expand=True)
types = pd.melt(types)['value'].dropna()

# Frequência de cada tipo
type_counts = types.value_counts()

# Gráfico de barras - CORRIGIDO
plt.figure(figsize=(14, 8))
type_plot = sns.barplot(x=type_counts.index, y=type_counts.values,
                        hue=type_counts.index, palette='viridis', legend=False)
plt.title('Distribuição de Tipos de Pokémon')
plt.xlabel('Tipo')
plt.ylabel('Quantidade')
plt.xticks(rotation=45)

# Adicionar os valores nas barras
for i, v in enumerate(type_counts.values):
    type_plot.text(i, v + 2, str(v), ha='center')

plt.tight_layout()
plt.savefig('pokemon_types_distribution.png')
plt.close()  # Use close() em vez de show() para evitar o warning

# ALTURA X PESO
# Converter altura (decímetros para metros) e peso (hectogramas para kg)
pokemon_df['height_m'] = pokemon_df['height'] / 10
pokemon_df['weight_kg'] = pokemon_df['weight'] / 10

# Gráfico de dispersão com linha de regressão
plt.figure(figsize=(12, 8))
scatter = sns.regplot(x='height_m', y='weight_kg', data=pokemon_df,
                      scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
plt.title('Relação entre Altura e Peso dos Pokémon')
plt.xlabel('Altura (metros)')
plt.ylabel('Peso (kg)')

# Identificar outliers (opcional)
outliers = pokemon_df.nlargest(5, 'weight_kg')
for i, row in outliers.iterrows():
    scatter.text(row['height_m']+0.1, row['weight_kg'], row['name'],
                 horizontalalignment='left', size='medium')

plt.tight_layout()
plt.savefig('height_weight_relation.png')
plt.close()

# STATS BASICAS
# Selecionar as colunas de estatísticas
stats = ['stats_hp', 'stats_attack', 'stats_defense',
         'stats_special_attack', 'stats_special_defense', 'stats_speed']

# Criar boxplot
plt.figure(figsize=(14, 8))
melted_df = pokemon_df[stats].melt(var_name='Stat', value_name='Value')
melted_df['Stat'] = melted_df['Stat'].str.replace('stats_', '').str.replace('_', ' ').str.title()

box = sns.boxplot(x='Stat', y='Value', data=melted_df,
                 hue='Stat', palette='Set2', legend=False)
plt.title('Distribuição das Estatísticas Básicas dos Pokémon')
plt.xlabel('Estatística')
plt.ylabel('Valor')

plt.tight_layout()
plt.savefig('stats_distribution.png')
plt.close()

# EXP COM BASE NA GERACAO
# Criar categorias de geração baseadas no ID
pokemon_df['generation'] = pd.cut(pokemon_df['id'],
                                 bins=[0, 151, 251, 386, 493, 649, 721, 809, 10000],
                                 labels=['Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6', 'Gen 7', 'Gen 8+'],
                                 ordered=True)

# Gráfico de violino
plt.figure(figsize=(14, 8))
violin = sns.violinplot(x='generation', y='base_experience', data=pokemon_df,
                        hue='generation', palette='pastel', inner='quartile', legend=False)
plt.title('Distribuição de Experiência Base por Geração')
plt.xlabel('Geração')
plt.ylabel('Experiência Base')

plt.tight_layout()
plt.savefig('base_experience_by_generation.png')
plt.close()

# TOP 20 POKEMON COM MELHORES STATS
# Calcular a soma total das estatísticas
pokemon_df['total_stats'] = pokemon_df[stats].sum(axis=1)

# Pegar os top 20
top_20 = pokemon_df.nlargest(20, 'total_stats')[['name', 'total_stats'] + stats]

# Gráfico de barras horizontais - CORRIGIDO
plt.figure(figsize=(14, 10))
barh = sns.barplot(x='total_stats', y='name', data=top_20,
                  hue='name', palette='rocket', legend=False)
plt.title('Top 20 Pokémon com Maior Soma de Estatísticas')
plt.xlabel('Soma Total de Estatísticas')
plt.ylabel('Pokémon')

# Adicionar os valores
for i, v in enumerate(top_20['total_stats']):
    barh.text(v + 5, i, str(v), color='black', ha='left', va='center')

plt.tight_layout()
plt.savefig('top_20_pokemon_stats.png')
plt.close()

# CORRELACAO
# Calcular correlações
corr = pokemon_df[stats].corr()

# Mapa de calor
plt.figure(figsize=(12, 10))
mask = np.triu(np.ones_like(corr, dtype=bool))
heatmap = sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm',
                      fmt='.2f', linewidths=.5,
                      annot_kws={"size": 12}, vmin=-1, vmax=1)
plt.title('Matriz de Correlação entre Estatísticas de Pokémon')

plt.tight_layout()
plt.savefig('stats_correlation_matrix.png')
plt.close()

# PARTE INTERATIVA (Plotly)
# Carregar os dados
pokemon_df = pd.read_csv('pokeapi_pokemon.csv')

# Converter unidades
pokemon_df['height_m'] = pokemon_df['height'] / 10
pokemon_df['weight_kg'] = pokemon_df['weight'] / 10

# Criar coluna de geração baseada no ID
generation_bins = [0, 151, 251, 386, 493, 649, 721, 809, float('inf')]
generation_labels = ['Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6', 'Gen 7', 'Gen 8+']
pokemon_df['generation'] = pd.cut(pokemon_df['id'], bins=generation_bins, labels=generation_labels)

# Calcular estatística total
stats_columns = ['stats_hp', 'stats_attack', 'stats_defense',
                'stats_special_attack', 'stats_special_defense', 'stats_speed']
pokemon_df['total_stats'] = pokemon_df[stats_columns].sum(axis=1)

# Criar gráfico interativo com subplots
fig = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "scatter", "rowspan": 2}, {"type": "pie"}],
           [None, {"type": "bar"}]],
    subplot_titles=("Relação Peso vs Altura", "Distribuição por Tipo", "Média de Estatísticas por Geração"),
    vertical_spacing=0.1,
    horizontal_spacing=0.1
)

# Gráfico de dispersão principal (Peso vs Altura)
scatter = px.scatter(
    pokemon_df,
    x='height_m',
    y='weight_kg',
    color='generation',
    size='total_stats',
    hover_name='name',
    hover_data={
        'height_m': ':.1f',
        'weight_kg': ':.1f',
        'base_experience': True,
        'generation': True,
        'total_stats': True,
        'types': True
    },
    labels={
        'height_m': 'Altura (m)',
        'weight_kg': 'Peso (kg)',
        'generation': 'Geração',
        'total_stats': 'Total Stats'
    },
    title='Relação Peso vs Altura dos Pokémon'
)

for trace in scatter.data:
    fig.add_trace(trace, row=1, col=1)

# Gráfico de pizza (Distribuição por Tipo)
types = pokemon_df['types'].str.split(', ', expand=True)
types = pd.melt(types)['value'].dropna()
type_counts = types.value_counts().reset_index()
type_counts.columns = ['type', 'count']

pie = px.pie(
    type_counts,
    values='count',
    names='type',
    hole=0.4,
    title='Distribuição por Tipo'
)

fig.add_trace(pie.data[0], row=1, col=2)

# Gráfico de barras (Estatísticas por Geração)
stats_by_gen = pokemon_df.groupby('generation')[stats_columns].mean().reset_index()
stats_by_gen = pd.melt(stats_by_gen, id_vars=['generation'], value_vars=stats_columns)
stats_by_gen['variable'] = stats_by_gen['variable'].str.replace('stats_', '').str.replace('_', ' ').str.title()

bar = px.bar(
    stats_by_gen,
    x='generation',
    y='value',
    color='variable',
    barmode='group',
    labels={
        'generation': 'Geração',
        'value': 'Valor Médio',
        'variable': 'Estatística'
    },
    title='Média de Estatísticas por Geração'
)

for trace in bar.data:
    fig.add_trace(trace, row=2, col=2)

# Atualizar layout
fig.update_layout(
    height=900,
    showlegend=True,
    plot_bgcolor='rgba(240,240,240,0.8)',
    title_text="Análise Completa de Pokémon",
    hovermode='closest'
)

# Personalizar tooltips
fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br><br>" +
                  "Altura: %{x:.1f}m<br>" +
                  "Peso: %{y:.1f}kg<br>" +
                  "Exp Base: %{customdata[2]}<br>" +
                  "Geração: %{customdata[3]}<br>" +
                  "Total Stats: %{customdata[4]}<br>" +
                  "Tipos: %{customdata[5]}<extra></extra>",
    selector={'type': 'scatter'}
)

# Mostrar o gráfico
fig.show()

# Salvar como HTML interativo
fig.write_html("pokemon_interactive_plot.html")
##