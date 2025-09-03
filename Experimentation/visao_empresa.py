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


st.header('Marketplace - Visão Cliente')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        st.markdown('# Orders by Day')
        cols = ['ID', 'Order_Date']
        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)

        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                # Distribuição dos pedidos por tipo de tráfego
                st.markdown('# Distribuição dos pedidos por tráfego')
                df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

                df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
                df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

                fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
                st.plotly_chart(fig, use_cointainer=True)
            with col2:
                # Comparação do volume de pedidos por cidade e tipo de tráfego.
                st.markdown('# Volume de pedidos por cidade e tráfego')

                df_aux = df1.loc[:, ['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
                df_aux = df_aux.loc[df_aux['City'] !='NaN', :]
                df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', : ]

                fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
                st.plotly_chart(fig, use_container=True)
with tab2:
    with st.container():
        st.markdown('# Pedidos por semana')

        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container=True)

        st.markdown('# Pedidos por entregador por semana')

        df_aux1 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

        df_aux = pd.merge(df_aux1, df_aux2, how='inner', on='week_of_year')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart(fig, use_container=True)
with tab3:

    st.markdown('# Country Map')
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude','Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker(
            [location_info['Delivery_location_latitude'],
            location_info['Delivery_location_longitude']],
            popup=location_info[ ['City', 'Road_traffic_density'] ]
        ).add_to(map)
    folium_static(map, width=1024, height=600)


