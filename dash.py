import streamlit as st
import pandas as pd

#import csv

df = pd.read_csv('data_cleaned.csv')

# Page configuration

st.set_page_config(
    page_title="Customer Churn - GBank",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded")

with st.echo():
    st.write('This code will be printed')

#Side bar

with st.sidebar:
    st.image('logo.png')

    st.header("Filtros", divider='blue', help='Escolha aqui as características da pessoa cliente')

    list_age = df['Age'].sort_values(ascending=True).unique()
    select_box_age = st.selectbox('Idade',list_age)

    list_gender = df['Gender'].sort_values(ascending=True).unique()
    select_box_age = st.selectbox('Gênero',list_gender)