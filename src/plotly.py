import plotly.graph_objects as go

# Datos de ejemplo
x = [1, 2, 3, 4, 5]
y = [4, 6, 5, 8, 2]

# Creación del gráfico de dispersión
grafico = go.Scatter(
    x=x,
    y=y,
    mode='markers',
    name='Datos de ejemplo'
)

# Diseño del layout del gráfico
layout = go.Layout(
    title='Gráfica de dispersión con Plotly',
    xaxis=dict(title='Eje X'),
    yaxis=dict(title='Eje Y')
)

# Visualización del gráfico
fig = go.Figure(data=grafico, layout=layout)
fig.show()
