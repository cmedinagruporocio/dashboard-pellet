import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
dataset = pd.read_csv('datos_pellet.csv', parse_dates=['Semana'])

# Crear columnas auxiliares
dataset['Mes'] = dataset['Semana'].dt.strftime('%m')          # Para filtro
dataset['MesAbrev'] = dataset['Semana'].dt.strftime('%b')     # Para eje superior

# Filtros interactivos
st.sidebar.title("Filtros")

anios = sorted(dataset['Anio'].dropna().unique(), reverse=True)
tipos = sorted(dataset['TipoAlimento'].dropna().unique())
meses = sorted(dataset['Mes'].unique())


# Filtrar datos
df_filtrado = dataset[
    dataset['Anio'].isin(anio_sel) &
    dataset['TipoAlimento'].isin(tipo_sel) &
    dataset['Mes'].isin(mes_sel)
]

# Validar que haya datos
if df_filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# Función de promedio ponderado
def promedio_ponderado(df, valor_col, peso_col):
    total_peso = df[peso_col].sum()
    if total_peso == 0:
        return 0
    return (df[valor_col] * df[peso_col]).sum() / total_peso

# Agrupar por semana
agrupado = df_filtrado.groupby(['Semana', 'SemanaNum', 'Anio']).apply(
    lambda df: pd.Series({
        'kwh_prensa': promedio_ponderado(df, 'kwh_prensa', 'ton'),
        'porc_prensa': promedio_ponderado(df, 'porc_prensa', 'ton'),
        'Rendimiento': promedio_ponderado(df, 'Rendimiento', 'ton')
    })
).reset_index()

# Escalar Rendimiento
min_kwh, max_kwh = agrupado['kwh_prensa'].min(), agrupado['kwh_prensa'].max()
min_rend, max_rend = agrupado['Rendimiento'].min(), agrupado['Rendimiento'].max()

def escalar(col, min_val, max_val):
    if max_val == min_val:
        return col
    return (col - min_val) / (max_val - min_val) * (max_kwh - min_kwh) + min_kwh

rend_esc = escalar(agrupado['Rendimiento'], min_rend, max_rend)
agrupado['MesAbrev'] = agrupado['Semana'].dt.strftime('%b')

# Crear gráfico
fig, ax1 = plt.subplots(figsize=(14, 7))
line1, = ax1.plot(agrupado['Semana'], agrupado['kwh_prensa'], color='blue', linestyle='--', label='kW/h Prensa')
line2, = ax1.plot(agrupado['Semana'], rend_esc, color='black', linewidth=2.5, label='Rendimiento Planta Pellet')
ax1.set_ylabel('kW/h Prensa', fontweight='bold')
ax1.tick_params(axis='y', labelcolor='black')

# Eje derecho: % prensa
ax2 = ax1.twinx()
line3, = ax2.plot(agrupado['Semana'], agrupado['porc_prensa'], color='green', linestyle='--', label='Porcentaje Prensa')
ax2.set_ylabel('Porcentaje Prensa', fontweight='bold', color='black')
ax2.tick_params(axis='y', colors='black', labelsize=9)

# Etiquetas
for i, fila in agrupado.iterrows():
    ax1.text(fila['Semana'], fila['kwh_prensa'] + 0.1, f"{fila['kwh_prensa']:.1f}", color='blue', fontsize=7, ha='center')
    ax1.text(fila['Semana'], rend_esc[i] + 0.1, f"{fila['Rendimiento']:.1f}", color='black', fontsize=7, ha='center')
    ax2.text(fila['Semana'], fila['porc_prensa'] + 0.5, f"{fila['porc_prensa']:.1f}", color='green', fontsize=7, ha='center')

# Eje inferior: SemanaNum
ax1.set_xticks(agrupado['Semana'])
ax1.set_xticklabels(agrupado['SemanaNum'], rotation=45)

# Eje superior: Mes abreviado
ax_top = ax1.secondary_xaxis('top')
ax_top.set_xticks(agrupado['Semana'])
ax_top.set_xticklabels(agrupado['MesAbrev'], fontsize=8)

# Leyenda y título
lines = [line1, line2, line3]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc='upper left')
plt.title("kW/h Prensa vs Rendimiento vs Porcentaje Uso Prensa por Semana", pad=25, fontweight='bold')

# Mostrar gráfico
st.pyplot(fig)

