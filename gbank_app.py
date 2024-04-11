import streamlit as st
import pandas as pd
import plotly.express as px
import millify 

#import csv

df = pd.read_csv('data_cleaned.csv')

# Page configuration

st.set_page_config(
    page_title="Customer Churn - GBank",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded")

#Side bar (Filters)

with st.sidebar:
    st.image('logo.png')

    st.header("Filtros", divider='blue', help='Por favor, selecione as características dos clientes cujos dados serão apresentados.')

    #Age
    list_age = df['Age'].sort_values(ascending=True).unique()
    list_age = list_age.tolist()
    selecte_slide_age = st.slider('Idade', value=[list_age[0],list_age[-1]], help=f'Inclua idades entre {list_age[0]} e {list_age[-1]} anos')
    selected_age_range = range(selecte_slide_age[0],selecte_slide_age[-1])
    
    #Gender
    list_gender = df['Gender'].sort_values(ascending=True).unique()
    selected_gender = st.multiselect('Gênero',list_gender, default=list_gender, help='Selecione ao menos um gênero da lista')

    #Status
    selected_status_customer = st.selectbox('Status do Cliente', ['Todos','Ativo','Inativo'], help='O campo status indica se o cliente está ativo ou inativo no banco')
    if selected_status_customer == 'Todos':
        selected_status_customer = [0,1]
    elif selected_status_customer == 'Ativo':
        selected_status_customer = [1]
    else: selected_status_customer = [0]

    #Country
    list_country = df['Geography'].sort_values(ascending=True).unique()
    selected_country = st.multiselect('Pais',list_country, default=list_country, help='Selecione ao menos um pais da lista')

filters = ((df['Geography'].isin(selected_country)) & (df['Age'].isin(selected_age_range))  & (df['Gender'].isin(selected_gender)) & (df['IsActiveMember'].isin(selected_status_customer)))

try:
    #Layout
    col = st.columns((0.50, 1, 0.7), gap='large')

    #collumn 1

    with col[0]:
        
        #Total Customers e Saldo Médio dos Clientes


        total_customer = df[filters]['CustomerId'].count()
        mean_balance = round(df[filters]['Balance'].mean(), 2)
   
        if (total_customer != 0) and (mean_balance > 0 or mean_balance <= 0):
            st.metric('Total de Clientes', millify.millify(total_customer))
            st.metric('Média de Saldo em Conta',f'U$ {mean_balance}')

        #plot bar
        df_country_count = df[filters].groupby(['Geography'])[['CustomerId']].count().reset_index()
        df_country_count.rename({'CustomerId': 'Clientes',
                                'Geography': 'Pais'
                                }, inplace=True, axis=1)
        if (len(selected_gender) > 0) and (len(selected_country) > 0) and ((df['Age'].isin(selected_age_range).any()) == True ):
            bar = px.bar(df_country_count, title='Clientes por Paises', x='Pais', y='Clientes')

        st.plotly_chart(bar,use_container_width=True)
    
        #Plot pie_age_card
        total_hasCard = df[filters & (df['HasCrCard'] == 1)]['CustomerId'].count()
        percen_hascard = round((total_hasCard/total_customer)*100)
        percen_nohascard = round(100 - percen_hascard)

        data = {
        "Categoria": ["Sim", "Não"],
        "Porcentagem": [percen_hascard, percen_nohascard]
        }
        data_sorted = data.copy()
        data_sorted['Porcentagem'] = sorted(data_sorted['Porcentagem'], reverse=True)

        pie_age_card = px.pie(data, title= "Clientes com Cartão de Crédito" ,values='Porcentagem', names='Categoria', hole=0.8,)
        pie_age_card.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=20,
                            marker=dict(line=dict(color='#000000', width=2)), 
                            textposition='inside')
        st.plotly_chart(pie_age_card,use_container_width=True)




    with col[1]:

        #plot line
        df_age_product = df[filters].groupby('Age')[['NumOfProducts']].sum().reset_index()
        df_age_product.rename({'Age': 'Idade',
                                'NumOfProducts': 'Número de Produtos'
                                }, inplace=True, axis=1)
        

        line = px.line(df_age_product,title='Idade vs Produtos Adquiridos', x='Idade', y='Número de Produtos')
        st.plotly_chart(line,use_container_width=True)

        #plot line 2
        df_age_score = df[filters].groupby('Age')[['CreditScore']].sum().reset_index()
        df_age_score.rename({'Age': 'Idade',
                                'CreditScore': 'Score'
                                }, inplace=True, axis=1)
        
        line = px.line(df_age_score,title='Idade vs Produtos Adquiridos', x='Idade', y='Score')
        st.plotly_chart(line,use_container_width=True)

    with col[2]:
        
        st.markdown('### Top 10 Melhores Scores')
        df_score = df[filters][['Surname', 'CreditScore']].sort_values(by=['CreditScore','Surname'], ascending=False).head(10).reset_index(drop=True)
        df_score.rename({'Surname': 'Nome',
                        'CreditScore': 'Score'}, axis=1, inplace=True)
        top_10 = [i for i in range(1,11)]
        df_score.index = top_10
        st.dataframe(
            df_score,use_container_width=True, 
            column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                format='%d',
                min_value=0,
                max_value=1000,
            )
        }
        )

        st.markdown('### Top 10 Piores Scores')
        df_score = df[filters][['Surname', 'CreditScore']].sort_values(by=['CreditScore','Surname'], ascending=True).head(10).reset_index(drop=True)
        df_score.rename({'Surname': 'Nome',
                        'CreditScore': 'Score'}, axis=1, inplace=True)
        top_10 = [i for i in range(1,11)]
        df_score.index = top_10
        st.dataframe(
            df_score,use_container_width=True, 
            column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                format='%d',
                min_value=0,
                max_value=1000,
            )
        }
        )
except:

    st.title('Opa! Pareceu que há algo de errado 🚨')

    if (df['Age'].isin(selected_age_range).any()) == False:
       st.subheader(f"""
                    Não existe dados para o range de idade. 
                    Por favor, selecione um intervalo que inclua idades entre {list_age[0]} e {list_age[-1]} anos"""
                    )
    elif (len(selected_age_range) == 0):
       st.subheader(" Selecione um range de idade válido")
    elif len(selected_gender) == 0:
       st.subheader("Selecione ao menos um Gênero")
    elif len(selected_country) == 0:
        st.subheader("Selecione ao menos um Pais")
