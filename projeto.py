# importanto framewokrs e bibliotecas
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


# importando banco de dados  - dataframe
df = pd.read_csv('../train.csv')

df1 = df.copy()


# limepza do banco de dados - dataframe

# limpando as linhas
cols = df1.columns
cols_list = cols.tolist()
for c in cols_list:
    rows = (df1[c] != 'NaN ')
    df1 = df1.loc[rows, :].copy()

# removendo o espaço no final da string
cols_to_strip = ['Type_of_vehicle', 'Festival', 'Road_traffic_density', 'Type_of_order','Time_taken(min)']

for c in cols_to_strip:
    df1[c] = df1[c].str.rstrip()

df1['Time_taken(min)'] = df1['Time_taken(min)'].str.strip('(min)')

# alterando os tipos
cols_to_int = ['Delivery_person_Age', 'multiple_deliveries','Time_taken(min)']
cols_to_float = ['Delivery_person_Ratings']
cols_to_datetime = ['Order_Date']

for c in cols_to_int:
    df1[c] = df1[c].astype(int)

for c in cols_to_float:
    df1[c] = df1[c].astype(float)

for c in cols_to_datetime:
    df1[c] = pd.to_datetime(df1[c], format='%d-%m-%Y')


# verificação do estado do dataframe
# print(df1.head())

# Construção do Dashboard

st.header('')

# barra lateral

image_path = 'film.png'
image = Image.open(image_path)

st.sidebar.markdown('# Ficticious Company')
st.sidebar.markdown('## Fatest Delivery in Town')
st.sidebar.markdown('---')
st.sidebar.markdown('## Seleciona uma data limite')
data_slider = st.sidebar.slider(
    'Até qual data?',
    value = datetime(2022, 4, 6),
    min_value = datetime(2022, 2, 11),
    max_value= datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

#st.header(data_slider)

# barra lateral - filtros de data

# layout

tab1, tab2, tab3 = st.tabs(['Visão da Empresa','Visão dos Restaurantes','Visão dos Entregadores'])

with tab1:
    st.markdown('# Visão da Empresa')

    # Mapa mostrando a posição dos restaurnates e dos locais de entrega dos pedidos
    with st.container():
        st.markdown('# Mapa do País')
        st.markdown('## Restaurante x Entrega')
        df_aux = (
            df1.loc[
            :, ['City','Road_traffic_density',
            'Delivery_location_latitude','Delivery_location_longitude',
            'Restaurant_latitude','Restaurant_longitude']]
            .groupby(['City', 'Road_traffic_density'])
            .median()
            .reset_index()
            )
        map = folium.Map()

        icon_delivery_img = './entregador.png'
        icon_delivery = folium.CustomIcon(
            icon_delivery_img,
            icon_size=(30,30)
        )
        icon_restaurant_img = './food-restaurant.png'
        icon_restaurant = folium.CustomIcon(
            icon_restaurant_img,
            icon_size=(30,30)
        )

        for index, location_info in df_aux.iterrows():
            folium.Marker(
                [location_info['Delivery_location_latitude'],
                location_info['Delivery_location_longitude']],
                icon=icon_delivery,
                popup=location_info[['City','Road_traffic_density']]
            ).add_to(map)
        
        for index, location_info in df_aux.iterrows():
            folium.Marker(
                [location_info['Restaurant_latitude'],
                location_info['Restaurant_longitude']],
                icon=icon_restaurant,
                popup=location_info[['City','Road_traffic_density']]
            ).add_to(map)
        folium_static(map, width=1024, height=600)

    with st.container():
        tab1_1, tab1_2 = st.tabs(['Visão Gerencial', 'Visão Tática'])

        with tab1_1:
            with st.container():
                # Métrica de Pedidos
                col1, col2 = st.columns(2)
                with col1:
                    # Distribuição dos pedidos por cidade
                    # Total x Crescimmento | Barra x Linha
                    st.markdown('### Volume de pedidos por cidade')
                    with st.container():
                        # Total
                        st.markdown('#### Total')
                        df_aux = (df1.loc[
                                  :, ['ID', 'City']]
                                  .groupby('City')
                                  .count()
                                  .reset_index()
                        )
                        fig = px.bar(df_aux, x='City', y='ID', labels={'ID':"Num of Orders"})
                        st.plotly_chart(fig, use_container=True)
                    with st.container():
                        st.markdown('### Crescimento semanal')

                        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')                      
                        df_aux = (df1.loc[
                                  :, ['ID', 'City', 'week_of_year']]
                                  .groupby(['City', 'week_of_year'])
                                  .count()
                                  .reset_index()
                                 )
                        fig = px.line(df_aux, x="week_of_year", y="ID", color='City', labels={'ID':'Num of Orders'})
                        st.plotly_chart(fig, use_container=True)
                with col2:
                    pass
        with tab1_2:
            with st.container():
                st.markdown('# Pedidos por semana')

                df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
                df_aux = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()

                fig = px.line(df_aux, x='week_of_year', y='ID', labels={'ID':'Num of Orders', 'week_of_year':'Week'})
                st.plotly_chart(fig, use_container=True)

                st.markdown('# Pedidos por entregador por semana')

                df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
                df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

                df_aux = pd.merge(df_aux1, df_aux2, how='inner', on='week_of_year')
                df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

                fig = px.line(df_aux, x='week_of_year', y='order_by_deliver', labels={'order_by_deliver':'Num of Orders by Deliver', 'week_of_year':'Week'})
                st.plotly_chart(fig, use_container=True)

with tab2:
    with st.container():
        st.markdown('# Visão dos Restaurantes')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')

        with col1:
            st.markdown('### Entregadores únicos')
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
        with col2:
            st.markdown('### Distância média')

            cols = ['Delivery_location_latitude','Delivery_location_longitude',
                   'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1.loc[:, cols].apply(
                lambda x:
                haversine(
                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                ), axis=1
            )
            avg_distance = np.round(df1['distance'].mean(), 2)
            col2.metric('Mean Distance', avg_distance)
        with col3:
            st.markdown('### Tempo médio c/ Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)':['mean','std']})
            )
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)

            col3.metric('Tempo médio c/ Festival', df_aux)

        with col4:
            st.markdown('### O desvio padrão de Entrega médio c/ Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean','std']})
            )
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)

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

with tab3:
    with st.container():
        st.markdown('# Visão dos Entregadores')

        st.markdown('# Métricas Gerais')
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
        st.markdown('# Avaliações')

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






