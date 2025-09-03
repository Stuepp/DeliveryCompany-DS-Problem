import pandas as pd
from datetime import datetime
import plotly.express as px
import streamlit as st
from PIL import Image
from haversine import haversine
import folium
from streamlit_folium import folium_static

df = pd.read_csv('../train.csv')

df1 = df.copy()

# cleaning rows
cols = df1.columns
cols = cols.tolist()
for c in cols:
    rows = (df1[c] != 'NaN ')
    df1 = df1.loc[rows, :].copy()

# changing types
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
df1['multiple_deliveries'] = df1['Delivery_person_Age'].astype(int)
# Time_Orderd should be change from 'o' to time
# Time_Order_picked should be change from 'o' to time

# removing space at the end of strinf from cols Type_of_vehicle, Festival
df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.rstrip()
df1['Festival'] = df1['Festival'].str.rstrip()
df1['Road_traffic_density'] = df1['Road_traffic_density'].str.rstrip()
df1['Type_of_order'] = df1['Type_of_order'].str.rstrip()

df1['Time_taken(min)'] = df1['Time_taken(min)'].str.strip('(min)')
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

print(df1.head())


st.header('Marketplace - Visão Entregadores')

# Barra Lateral

image_path = 'film.png'
image = Image.open(image_path)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fatest Delivery in Town')
st.sidebar.markdown('---')
st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.header(data_slider)


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('---')
st.sidebar.markdown('### Powered by Comidade DS')

# Filtros de data

selected_rows = df1['Order_Date'] < data_slider
df1 = df1.loc[selected_rows, :]

selected_rows = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[selected_rows, :]

# laytout

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.title('Métricas Gerais')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #st.title('Maior idade')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric(label='Maior idade:', value=maior_idade)
        with col2:
            #st.title('Menor idade')
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric(label='Menor idade:', value=menor_idade)
        with col3:
            #st.title('Melhor condição de veículos')
            melhor_condicao_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric(label='Melhor condição', value=melhor_condicao_veiculo)
        with col4:
            #st.title('Pior condição de veículos')
            pior_condicao_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric(label='Pior condição', value=pior_condicao_veiculo)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Avaliações medias por entregador')
            df_avg_ratings_per_deliver = (
                df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                .groupby('Delivery_person_ID')
                .mean()
                .reset_index()
            )
            st.dataframe(df_avg_ratings_per_deliver)
        with col2:
            st.subheader('Avaliação média por trânsito')
            df_avg_rating_by_traffic = (
                df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                .groupby('Road_traffic_density')
                .agg({ 'Delivery_person_Ratings' : ['mean','std']})
            )
            st.dataframe(df_avg_rating_by_traffic)
            
            st.subheader('Avaliação por clima')
            df_avg_std_rating_by_weather = (
                df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                .groupby('Weatherconditions')
                .agg({ 'Delivery_person_Ratings' : ['mean','std'] })
            )
            st.dataframe(df_avg_std_rating_by_weather)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Top entregadores mais rápidos')
            df2 = (
                df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                .groupby(['City','Delivery_person_ID'])
                .mean()
                .sort_values(['City','Time_taken(min)'], ascending=True)
                .reset_index()
            )
            
            df_result = pd.DataFrame()
            cities = df2['City'].unique().tolist()
            for city in cities:
                df_aux = df2.loc[df2['City'] == city, :].head(10)
                df_result = pd.concat([df_result, df_aux])
            df_result.reset_index(drop=True)
            st.dataframe(df_result)
            
        with col2:
            st.subheader('Top entregadores mais lentos')
            df2 = (
                df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                .groupby(['City','Delivery_person_ID'])
                .mean()
                .sort_values(['City','Time_taken(min)'], ascending=False)
                .reset_index()
            )

            df_result = pd.DataFrame()
            cities = df2['City'].unique().tolist()
            for city in cities:
                df_aux = df2.loc[df2['City'] == city, :].head(10)
                df_result = pd.concat([df_result, df_aux])
            df_result.reset_index(drop=True)
            st.dataframe(df_result)
            

















