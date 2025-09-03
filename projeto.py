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


# streamlit page
st.set_page_config(layout="wide")
st.title("Food Delivery Dataset - DS problem")

# importando banco de dados  - dataframe
df = pd.read_csv('train.csv')

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

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

# makes some operarions stop working... -> it says cuz of type, but its believed to be cuz of null resultsx
#city_options = st.sidebar.multiselect(
#    'Which cities',
#    ['Metropolitian', 'Urban', 'Semi-Urban'],
#    default=['Metropolitian', 'Urban', 'Semi-Urban']
#)

selected_rows = df1['Order_Date'] < data_slider
df1 = df1.loc[selected_rows, :]

selected_rows = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[selected_rows, :]

#selected_rows = df1['City'].isin(city_options)
#df1 = df1.loc[selected_rows, :]


#st.header(data_slider)

# barra lateral - filtros de data

# layout

tab1, tab2, tab3 = st.tabs(['Company Vision','Restaurant View',"Deliverers' View"])

with tab1:
    st.markdown('# Company Vision')

    # Mapa mostrando a posição dos restaurnates e dos locais de entrega dos pedidos
    with st.container():
        st.markdown('# Country Map')
        st.markdown('## Restaurant x Delivery')
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

        st.markdown('## The average distance to restaurants and delivery locations')
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 
            'Delivery_location_latitude', 'Delivery_location_longitude']

        # Supondo que 'df1' é seu DataFrame principal
        # O cálculo da distância deve ser feito em 'df1', não em 'df_aux'
        df1['distance'] = df1.loc[:, cols].apply(
            lambda x: haversine(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
            ), axis=1
        )

        # Calcula a média da nova coluna em 'df1'
        avg_distance = df1['distance'].mean()

        # Exibe a média formatada como uma métrica
        st.metric(label="Avarange distance (KM)", value=f"{avg_distance:.2f}")

    with st.container():
        tab1_1, tab1_2 = st.tabs(['Management Vision', 'Tactical Vision'])

        with tab1_1:
            with st.container():
                # Métrica de Pedidos
                col1, col2 = st.columns(2)
                with col1:
                    # Distribuição dos pedidos por cidade
                    # Total x Crescimmento | Barra x Linha
                    st.markdown('### Order volume by city')
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
                        st.markdown('### Weekly growth')

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
                    with st.container():
                        st.markdown('### Quantity of orders by day')

                        df_aux = df1.loc[:, ['ID','Order_Date']].groupby('Order_Date').count().reset_index()
                        fig = px.bar(df_aux, x='Order_Date',y='ID', labels={'ID':'Num of Orders','Order_Date':'Order Date'})
                        st.plotly_chart(fig, use_container=True)

                    with st.container():
                        st.markdown('### Quantity of Orders by Day and City')

                        # Group by both 'Order_Date' and 'City'
                        df_aux = (df1.loc[:, ['ID', 'Order_Date', 'City']]
                                  .groupby(['Order_Date', 'City'])
                                  .count()
                                  .reset_index()
                                 )

                        # Create the bar chart using the 'color' parameter for the city
                        fig = px.bar(df_aux, x='Order_Date', y='ID', 
                                     color='City', # This creates a different color bar for each city
                                     barmode='group', # This groups bars for the same date side-by-side
                                     labels={'ID': 'Number of Orders', 'Order_Date': 'Order Date'},
                                     color_discrete_sequence=px.colors.qualitative.Vivid
                                    )
                        st.plotly_chart(fig, use_container=True)

        with tab1_2:
            with st.container():
                st.markdown('# Orders per week')

                df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
                df_aux = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()

                fig = px.line(df_aux, x='week_of_year', y='ID', labels={'ID':'Num of Orders', 'week_of_year':'Week'})
                st.plotly_chart(fig, use_container=True)

                st.markdown('# Orders per delivery person per week')

                df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
                df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

                df_aux = pd.merge(df_aux1, df_aux2, how='inner', on='week_of_year')
                df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

                fig = px.line(df_aux, x='week_of_year', y='order_by_deliver', labels={'order_by_deliver':'Num of Orders by Deliver', 'week_of_year':'Week'})
                st.plotly_chart(fig, use_container=True)

with tab2:
    with st.container():
        st.markdown('# Restaurant View')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')

        with col1:
            st.markdown('### Unique couriers')
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Unique couriers', delivery_unique)
        with col2:
            st.markdown('### Average distance')

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
            col2.metric('Mean distance', avg_distance)
        with col3:
            st.markdown('### Average time with Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)':['mean','std']})
            )
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)

            col3.metric('Average time with Festival', df_aux)

        with col4:
            st.markdown('### The Standard Deviation of Average Delivery with Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean','std']})
            )
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)

            col4.metric('Delivery STD with Festival', df_aux)
        with col5:
            st.markdown('### Average time without Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2 )

            col5.metric('Average time without Festival', df_aux)
        with col6:
            st.markdown('### Delivery STD without Festival')

            df_aux = (
                df1.loc[:, ['Time_taken(min)','Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)' : ['mean', 'std']})
            )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2 )

            col6.metric('Delivery STD without Festival', df_aux)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('### Average delivery time by city')
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
            st.markdown('### Distance Distribution')
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

            #fig = go.Figure(data=[
            #    go.Pie(labels=avg_distance['City'],
            #            values=avg_distance['distance'],
            #            pull=[0,0.1,0])
            #])
            
            st.markdown('## Average distance of Restaurant to Delivery location')
            #st.plotly_chart(fig)
            fig = px.bar(avg_distance, 
                 x='City', 
                 y='distance',
                 text='distance',  # Adiciona o valor da distância como texto na barra
                 #title='Average distance of Restaurant to Delivery location',
                 labels={'distance': 'Distância Média (KM)', 'City': 'Cidade'})
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('## Time Distribution')
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
                labels={'std_time':'STD Time'},
                color_continuous_midpoint=np.average(df_aux['std_time'])
            )

            st.plotly_chart(fig)

with tab3:
    with st.container():
        st.markdown("# Deliverers' View")

        st.markdown('# General Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #st.title('Maior idade')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric(label='Older delivery man:', value=maior_idade)
        with col2:
            #st.title('Menor idade')
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric(label='Youngest delivery man:', value=menor_idade)
        with col3:
            #st.title('Melhor condição de veículos')
            melhor_condicao_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric(label='Best vehicle condition', value=melhor_condicao_veiculo)
        with col4:
            #st.title('Pior condição de veículos')
            pior_condicao_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric(label='Worst vehicle condition', value=pior_condicao_veiculo)

    with st.container():
        st.markdown("""---""")
        st.markdown('# Reviews')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Average ratings per delivery person')
            df_avg_ratings_per_deliver = (
                df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                .groupby('Delivery_person_ID')
                .mean()
                .reset_index()
            )
            st.dataframe(df_avg_ratings_per_deliver)
        with col2:
            st.subheader('Average rating per transit')
            df_avg_rating_by_traffic = (
                df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                .groupby('Road_traffic_density')
                .agg({ 'Delivery_person_Ratings' : ['mean','std']})
            )
            st.dataframe(df_avg_rating_by_traffic)
            
            st.subheader('Assessment by weather')
            df_avg_std_rating_by_weather = (
                df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                .groupby('Weatherconditions')
                .agg({ 'Delivery_person_Ratings' : ['mean','std'] })
            )
            st.dataframe(df_avg_std_rating_by_weather)


    with st.container():
        st.markdown("""---""")
        st.title('Delivery speed')
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Top fastest delivery people')
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
            st.subheader('Top slowest delivery people')
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






