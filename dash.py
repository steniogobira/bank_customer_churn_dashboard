import streamlit as st
import pandas as pd
import folium

#import csv

df = pd.read_csv('data_cleaned.csv')

# Page configuration

st.set_page_config(
    page_title="Customer Churn - GBank",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded")

#Side bar

with st.sidebar:
    st.image('logo.png')

    st.header("Filtros", divider='blue', help='Escolha aqui as características da pessoa cliente')

    list_age = df['Age'].sort_values(ascending=True).unique()
    select_box_age = st.selectbox('Idade',list_age)

    list_gender = df['Gender'].sort_values(ascending=True).unique()
    select_box_gender = st.selectbox('Gênero',list_gender)


#Plot
df_country_count = df[(df['Age'] == select_box_age) & (df['Gender'] == select_box_gender) ].groupby(['Geography'])[['CustomerId']].count().reset_index()
df_country_count.rename({'CustomerId': 'Total Customer'}, inplace=True, axis=1)
st.bar_chart(df_country_count, x='Geography', y='Total Customer')
