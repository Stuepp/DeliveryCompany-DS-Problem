# DeliveryCompany-DS-Problem
Dataset: https://www.kaggle.com/datasets/gauravmalik26/food-delivery-dataset?select=train.csv
## The Problem:
(EN)

A food delivery company is looking to unlock insights from its service data. Your challenge is to take the raw dataset and transform it into a powerful, intuitive dashboard. This tool will be crucial for visualizing performance and guiding the company's strategic decisions.

(PT-BR)

Uma empresa de food delivery busca extrair insights valiosos de seus dados de serviço. Seu desafio é transformar o conjunto de dados brutos em um dashboard poderoso e intuitivo. Esta ferramenta será crucial para visualizar a performance e orientar as decisões estratégicas da empresa.

# Project Stages

## 1. Cleaning the data

  The first stage of this project was to understand what data was inside the dataset, its types, how could be transformed and cleaned.
  For example, it was noticed how some columns were obj and should be strings or ints, floats..
  Also some columns, had empty spaces at the end of theirs fields, like the "Road_traffic_density" column.

  The cleaninf of data then was sattled like the following:

  ```python
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
  ```

## 2. Understand what the company wants to see and other views

## 3. What can be seen with this dataset

## 4. The Dashboard

## Conclusion
