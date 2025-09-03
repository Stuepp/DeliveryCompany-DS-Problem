import pandas as pd
from datetime import datetime
import plotly.express as px
import streamlit as st
from PIL import Image
from haversine import haversine
import folium
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go

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
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','--','--'])


with tab1:
    with st.container():
        st.markdown('# Métricas Gerais')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')

        with col1:
            st.markdown('### Entregadores únicos')
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
        with col2:
            st.markdown('### Distância média')
            
            cols = ['Delivery_location_latitude','Delivery_location_longitude',
                    'Restaurant_latitude','Restaurant_longitude']
            df1['distance'] = df1.loc[:, cols].apply(
                lambda x:
                haversine(
                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                ), axis=1
            )
            avg_distance = np.round( df1['distance'].mean(), 2)
            col2.metric('Distância média:', avg_distance)
        with col3:
            st.markdown('### Tempo médio c/ Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2 )

            col3.metric('Tempo médio c/ Festival', df_aux)
            
        with col4:
            st.markdown('### O desvio padrão de Entrega médio c/ Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2 )

            col4.metric('STD da Entrega c/ Festival', df_aux)
        with col5:
            st.markdown('### Tempo médio s/ Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2 )

            col5.metric('Tempo médio s/ Festival', df_aux)
        with col6:
            st.markdown('### STD da Entrega s/ Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2 )

            col6.metric('STD da Entrega s/ Festival', df_aux)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('### Tempo Médio de entrega por cidade')
            df_aux = (
                df1.loc[:, ['City','Time_taken(min)']]
                .groupby('City')
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time','std_time']

            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    name='Control',
                    x=df_aux['City'],
                    y=df_aux['avg_time'],
                    error_y=dict(type='data', array=df_aux['std_time'])
                )
            )
            fig.update_layout(barmode='group')

            st.plotly_chart(fig)
        with col2:
            st.markdown('### Distribuição da Distância')
            df_aux = (
                df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                .groupby(['City', 'Type_of_order'])
                .agg({'Time_taken(min)' : ['mean','std']})
            )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            
            st.dataframe(df_aux)
        

    with st.container():
        st.markdown("""---""")
        st.markdown('# Distribuição do Tempo')

        col1, col2 = st.columns(2)
        with col1:
            df1['distance'] = (
            df1.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude',
                        'Restaurant_latitude','Restaurant_longitude']]
            .apply(
                lambda x:
                haversine(
                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                ), axis=1
            )
        )

            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

            fig = go.Figure(data=[
                go.Pie(labels=avg_distance['City'],
                        values=avg_distance['distance'],
                        pull=[0,0.1,0])
            ])
            st.plotly_chart(fig)
        
        with col2:
            df_aux = (
                df1.loc[:, ['City', 'Time_taken(min)','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time','std_time']

            df_aux = df_aux.reset_index()

            fig = px.sunburst(
                df_aux, path=['City','Road_traffic_density'], values='avg_time',
                color='std_time', color_continuous_scale='RdBu',
                color_continuous_midpoint=np.average(df_aux['std_time'])
            )

            st.plotly_chart(fig)          



