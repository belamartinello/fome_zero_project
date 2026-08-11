# Libraries

import pandas as pd
import numpy as np
import inflection
import folium
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
from folium.plugins import MarkerCluster

st.set_page_config(page_title='Countries', page_icon='🌎', layout='wide')

# ---------------------------------------------
# Funções
# ---------------------------------------------

def clean_code(df):
    """ Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
    """
    
    # 1. Remoção dos dados NaN
    df = df.dropna()
    
    # 2. Mudança do tipo da coluna de dados
    df['Cuisines'] = df['Cuisines'].astype(str)
    
    # 3. Remoção dos espaços das variáveis de texto
    df['Cuisines'] = df['Cuisines'].str.split(',').str[0]
    
    return df

# Country ID to Name Mapping

COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America"
}

# Function to get country name from ID
def country_name(country_id):
    return COUNTRIES[country_id]

# Exchange Rates dictionary to convert the average cost for two to USD
exchange_rates = {
    'Dollar($)': 1.0,
    'Botswana Pula(P)': 13.77,
    'Brazilian Real(R$)': 5.14,
    'Emirati Diram(AED)': 3.67,
    'Indian Rupees(Rs.)': 95.60,
    'Indonesian Rupiah(IDR)': 18082.00,
    'NewZealand($)': 1.73,
    'Pounds(£)': 0.75,
    'Qatari Rial(QR)': 3.64,
    'Rand(R)': 16.70,
    'Sri Lankan Rupee(LKR)': 336.01,
    'Turkish Lira(TL)': 47.39
}

# Function to convert the average cost for two to USD
def convert_to_usd(row):
    currency = row['Currency']
    avg_cost_for_two = row['Average Cost for two']
    if currency in exchange_rates:
        return avg_cost_for_two / exchange_rates[currency]
    else:
        return np.nan

def create_price_type(price_range):
    if price_range == 1:
        return 'cheap'
    elif price_range == 2:
        return 'normal'
    elif price_range == 3:
        return 'expensive'
    else:
        return 'gourmet'

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred"
}

def color_name(color_code):
    return COLORS[color_code]

def rename_columns(df):
    df1 = df.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df1.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new

    return df1

# --------------------------------- Inicio da Estrutura Logica do Código -------------------------------------------------------------------
# -----------------
# Import dataset
# -----------------
df = pd.read_csv('data/zomato.csv')

# -----------------
# Data Cleaning
# -----------------
df1 = clean_code(df)

# Apply the function to the DataFrame
df1['Country Name'] = df1['Country Code'].apply(country_name)
# Apply the conversion function to the DataFrame
df1['Average Cost for two (USD)'] = df1.apply(convert_to_usd, axis=1)
# Apply color_name function to the Dataframe
df1['color_name'] = df1['Rating color'].apply(color_name)

# =============================================
# Barra Lateral
# =============================================
image_path = 'alvo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Fome Zero')

st.sidebar.markdown('## Filtro')
countries_options = st.sidebar.multiselect(
    'Escolha os Países que Deseja Visualizar os Restaurantes',
    ['India', 'Australia', 'Brazil', 'Canada', 'Indonesia', 'New Zeland', 'Philippines', 'Qatar', 'Singapure', 'South Africa', 'Sri Lanka', 'Turkey', 'United Arab Emirates', 'England', 'United States of America'],
    default=['Brazil', 'Australia', 'Canada', 'England', 'Qatar', 'South Africa', 'United Arab Emirates', 'United States of America']
)

# Countries filter
linhas_selecionadas = df1['Country Name'].isin(countries_options)
df1 = df1.loc[linhas_selecionadas, :]

# =============================================
# Layout no Streamlit
# =============================================
st.markdown('# 🌎 Visão Países')

with st.container():
    st.markdown('**Quantidade de Restaurantes Registrados por País**')
    df_aux = df1.loc[ :, ['Country Name', 'Restaurant ID']].groupby('Country Name').nunique().reset_index().sort_values(by='Restaurant ID', ascending=False)
    fig = px.bar(df_aux, x = 'Country Name', y = 'Restaurant ID', text = 'Restaurant ID', labels = {'Country Name': 'Paises', 'Restaurant ID': 'Quantidade de Restaurantes'})
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.markdown('**Quantidade de Cidades Registradas por País**')
    df_aux = df1.loc[ :, ['City', 'Country Name']].groupby('Country Name').nunique().reset_index().sort_values(by='City', ascending=False)
    fig = px.bar(df_aux, x = 'Country Name', y = 'City', text = 'City', labels = {'Country Name': 'Países', 'City': 'Quantidade de Cidades'})
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('**Média de Avaliações feitas por País**')
        df_aux = df1.loc[ :, ['Country Name', 'Votes']].groupby('Country Name').mean().reset_index().sort_values(by='Votes', ascending=False).round(2)  
        fig = px.bar(df_aux, x = 'Country Name', y = 'Votes', text = 'Votes', labels = {'Country Name': 'Países', 'Votes': 'Média de Avaliações'})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('**Média de Preço de um prato para duas pessoas por País (US$)**')
        df_aux = df1.loc[ :, ['Country Name', 'Average Cost for two (USD)']].groupby('Country Name').mean().reset_index().sort_values(by='Average Cost for two (USD)', ascending=False).round(2)
        fig = px.bar(df_aux, x = df_aux['Country Name'], y = 'Average Cost for two (USD)', text = 'Average Cost for two (USD)', labels = {'Country Name': 'Países', 'Average Cost for two (USD)': 'Custo Médio para Dois'})
        st.plotly_chart(fig, use_container_width=True)
