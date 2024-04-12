import streamlit as st
import pandas as pd
import plotly.express as px
import millify 
import altair as alt

#import csv

df = pd.read_csv('data_cleaned.csv')

# Page configuration

st.set_page_config(
    page_title="Customeres - GBank",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded")

#Side bar (Filters)

def make_filters(df,selected_age_range,selected_gender,selected_status_customer,selected_country):
    age_filter = (df['Age'].isin(selected_age_range))
    gender_filter = df['Gender'].isin(selected_gender)
    status_filter = df['IsActiveMember'].isin(selected_status_customer)
    country_filter = df['Geography'].isin(selected_country)
    return ((age_filter) & (gender_filter)  & (status_filter) & (country_filter))

with st.sidebar:
    st.image('logo.png')
    st.header("Filtros", divider='blue', help='Por favor, selecione abaixo as características dos clientes cujos dados serão apresentados.')
    
    #Select_filters
    #Age
    list_age = df['Age'].sort_values(ascending=True).unique()
    list_age = list_age.tolist()
    selecte_slide_age = st.slider('Idade', value=[list_age[0],list_age[-1]], help=f'Inclua idades entre {list_age[0]} e {list_age[-1]} anos', min_value=list_age[0], max_value=list_age[-1])
    selected_age_range = range(selecte_slide_age[0],(selecte_slide_age[-1] + 1))
    
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

filters = make_filters(df,selected_age_range,selected_gender,selected_status_customer,selected_country)

try:
    #Layout
    col = st.columns((0.50, 1, 0.8), gap='large')

    #collumn 1
    with col[0]:
        
        #Total Customers e Saldo Médio dos Clientes
        total_customer = df[filters]['CustomerId'].count()
        mean_balance = round(df[filters]['Balance'].mean(), 2)
   
        if (total_customer != 0) and (mean_balance > 0 or mean_balance <= 0):
            st.metric('Total de Clientes', millify.millify(total_customer, 2), help='Total aproximado de clientes registrados na base de dados')
            st.metric('Média de Saldo em Conta',f'U$ {millify.millify(mean_balance,2)}', help= 'Média geral do saldo disponível em conta')

        #plot bar
        df_country_count = df[filters].groupby(['Geography'])[['CustomerId']].count().reset_index()
        df_country_count.rename({'CustomerId': 'Clientes',
                                'Geography': 'Pais'
                                }, inplace=True, axis=1)
        if (len(selected_gender) > 0) and (len(selected_country) > 0):
            bar = px.bar(df_country_count, title='Clientes por Paises', x='Pais', y='Clientes',text_auto='.2s')
            bar.update_layout(xaxis_title='', yaxis_title='',xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
            bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(bar,use_container_width=True)
    
        #Plot pie_costumer_card
        total_customer_nofilters = df['CustomerId'].count()
        total_hasCard = df[filters & (df['HasCrCard'] == 1)]['CustomerId'].count()
        percen_hascard = round((total_hasCard/total_customer_nofilters)*100)
        percen_nohascard = round(100 - percen_hascard)

        data = {
        "Categoria": ["Sim", "Não"],
        "Porcentagem": [percen_hascard, percen_nohascard]
        }
        data_sorted = data.copy()
        data_sorted['Porcentagem'] = sorted(data_sorted['Porcentagem'], reverse=True)
        df_donut = pd.DataFrame(data_sorted)

        pie_age_card = px.pie(data, title= "Clientes com Cartão de Crédito" ,values='Porcentagem', names='Categoria', hole=0.8,)
        pie_age_card.update_traces(textinfo='percent', textfont_size=50, 
                            textposition='inside')
        st.plotly_chart(pie_age_card,use_container_width=True)

    #collumn 2
    with col[1]:

        #Age vs Product
        df_age_product = df[filters].groupby('Age')[['NumOfProducts']].mean().reset_index()
        df_age_product.rename({'Age': 'Idade',
                                'NumOfProducts': 'Média Produtos Adiquiridos'
                                }, inplace=True, axis=1)
        
        #Age vs Média Score
        df_age_score = df[filters].groupby('Age')[['CreditScore']].mean().reset_index()
        df_age_score.rename({'Age': 'Idade',
                                'CreditScore': 'Média de Score'
                                }, inplace=True, axis=1)
        
        if selecte_slide_age[0] == selecte_slide_age[1]:

            #plot bar unique age Products
            if (len(selected_gender) > 0) and (len(selected_country) > 0):
                st.markdown(f'#### Média de Produtos Adiquiridos pelos clientes na idade de {selecte_slide_age[0]} anos')
                st.metric('',round(df_age_product['Média Produtos Adiquiridos'],2))

            #plot bar unique age Score
            if (len(selected_gender) > 0) and (len(selected_country) > 0):
                st.markdown(f'#### Média Score dos clientes na idade de {selecte_slide_age[0]} anos')
                st.metric('',round(df_age_score['Média de Score'],2))

        else:
            #plot line Products
            line = px.line(df_age_product,title='Idade vs Média Produtos Adiquiridos', x='Idade', y='Média Produtos Adiquiridos')
            line.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))

            st.plotly_chart(line,use_container_width=True)
            #plot line Scor
            line2 = px.line(df_age_score,title='Idade vs Média Score', x='Idade', y='Média de Score')
            line2.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
            st.plotly_chart(line2,use_container_width=True)
    #collumn 3
    with col[2]:
    
        def make_ranking_score(ascending):
            df_score = df[filters][['Surname', 'Age', 'CreditScore']].sort_values(by=['CreditScore','Surname'], ascending=ascending).reset_index(drop=True)
            df_score.rename({'Surname': 'Nome',
                        'CreditScore': 'Score',
                        'Age': 'Idade'}, axis=1, inplace=True)
            indx = [i for i in range(1,(len(df_score)+1))]
            df_score.index = indx
            df_plot= st.dataframe(df_score.head(10),use_container_width=True, 
                    column_config={
                    "Nome":  st.column_config.Column(
                        "Nome", 
                        width= "small"
                        ),
                    "Idade":  st.column_config.Column(
                        "Idade", 
                        width= "small"
                        ),
                    "Score": st.column_config.ProgressColumn(
                        "Score",
                        format='%d',
                        min_value=0,
                        max_value=1000,
                        )
                    }
                    )
            return df_plot
        
        st.markdown('### Top 10 Melhores Scores')
        make_ranking_score(False)

        st.markdown('### Top 10 Piores Scores')
        make_ranking_score(True)

except Exception as e:
    st.title('Opa! Parece que há algo de errado 🚨')
    st.write(f"Erro: {e}")
    if len(selected_gender) == 0:
        st.subheader("Selecione ao menos um Gênero")
    elif len(selected_country) == 0:
        st.subheader("Selecione ao menos um País")
