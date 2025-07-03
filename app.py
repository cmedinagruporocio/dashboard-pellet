import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("datos_pellet.csv")
df['Semana'] = pd.to_datetime(df['Semana'])
df = df.sort_values('Semana')

min_kwh, max_kwh = df['kwh_prensa'].min(), df['kwh_prensa'].max()
min_rend, max_rend = df['Rendimiento'].min(), df['Rendimiento'].max()

def escalar(col, min_val, max_val):
    if max_val == min_val:
        return col
    return (col - min_val) / (max_val - min_val) * (max_kwh - min_kwh) + min_kwh

rend_esc = escalar(df['Rendimiento'], min_rend, max_rend)

st.title("Dashboard Planta Pellet")
st.subheader("kWh Prensa, % Prensa y Rendimiento por Semana")

fig, ax1 = plt.subplots(figsize=(14, 7))

line1, = ax1.plot(df['Semana'], df['kwh_prensa'], color='blue', linestyle='--', label='kWh prensa')
line2, = ax1.plot(df['Semana'], rend_esc, color='black', linewidth=2, label='Rendimiento Planta Pellet')
ax1.set_ylabel("kWh prensa / Rendimiento Planta Pellet", color='black')
ax1.tick_params(axis='y', labelcolor='black')

ax2 = ax1.twinx()
line3, = ax2.plot(df['Semana'], df['porc_prensa'], color='green', linestyle='--', label='% prensa')
ax2.set_ylabel("% prensa", color='green')
ax2.tick_params(axis='y', colors='black', labelsize=9)

for i, fila in df.iterrows():
    ax1.text(fila['Semana'], fila['kwh_prensa'] + 0.2, f"{fila['kwh_prensa']:.1f}", fontsize=7, ha='center', color='blue')
    ax1.text(fila['Semana'], rend_esc[i] + 0.2, f"{fila['Rendimiento']:.1f}", fontsize=7, ha='center', color='black')
    ax2.text(fila['Semana'], fila['porc_prensa'] + 0.5, f"{fila['porc_prensa']:.1f}", fontsize=7, ha='center', color='green')

ax1.set_xticks(df['Semana'])
ax1.set_xticklabels(df['SemanaNum'], rotation=45)

ax_top = ax1.secondary_xaxis('top')
ax_top.set_xticks(df['Semana'])
ax_top.set_xticklabels(df['Semana'].dt.strftime('%m-%y'))

lines = [line1, line2, line3]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc='upper left')

plt.title("kWh Prensa y Rendimiento vs Porcentaje Uso Prensa por Semana", pad=20, fontweight='bold')
plt.grid(True)
fig.tight_layout()
st.pyplot(fig)
