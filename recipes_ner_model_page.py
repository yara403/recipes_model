import spacy
import streamlit as st
from spacy_streamlit import visualize_ner
import pandas as pd
from pathlib import Path
import re
import unicodedata
from panelinha_scraping import CLEANED_RECIPES_JSON_PATH as RECIPES_PATH
import recipes_ner_model

st.set_page_config(
    page_title="NER para Receitas Culinarárias",
    page_icon="content/img/salad-64.png",
    layout="wide",
)

st.title("Modelo de Reconhecimento de Entidades Nomeadas para Receitas Culinarárias (em Português 🇧🇷)", icon='🥘')

model_path = Path(recipes_ner_model.PATH_TO_MODEL)
if not model_path.exists():
    recipes_ner_model.main()

recipes_ner_model = spacy.load(model_path)
labels = list(recipes_ner_model.get_pipe("ner").labels)
colors = {
    'MEDIDA_PADRAO': "#F16BE0", 
    'MEDIDA_CASEIRA': "#A6CAF3", 
    'MEDIDA_INFORMAL': '#98FB98', 
    'UNIDADE': "#FAC9D0", 
    'ALIMENTO': "#FCEA85"
    }
options = {"ents": labels, "colors": colors}

with st.form(key='ner_form', enter_to_submit=False):
    text = st.text_area(
        'Insira os ingredientes da receita (apenas a quantidade e o alimento):',
        on_change='ignore',
        placeholder='🥚 Exemplo🥛🥄\n1⁄2 xícara (chá) de açúcar\n1 colher (sopa) de mel\n50 g de manteiga'
        )
    bt_clicked = st.form_submit_button('Enviar')

if text and bt_clicked:
    text = unicodedata.normalize('NFKC', text)
    doc = recipes_ner_model(text)
    visualize_ner(
        doc, 
        labels=labels, 
        displacy_options=options,
        title="O modelo identificou as seguintes entidades na receita:"
        )

st.subheader("Explore mais o nosso banco de dados de receitas:", icon="🍲")
recipes_raw_df = pd.read_json(RECIPES_PATH)

def ingredient_search():
    recipes_selected_df = recipes_raw_df[['name', 'description', 'time', 'serves','ingredients', 'steps', 'link']]
    search_term = st.text_input('Pesquisar por ingrediente:', type='search', live=True, placeholder='Buscar receitas por ingrediente', icon='🍊')
    if search_term:
        recipes_selected_df = recipes_selected_df[
            recipes_selected_df['ingredients']
            .apply(lambda parts: any(re.match(rf'.*\b{search_term}.*', ingredient, re.IGNORECASE) is not None for ingredient in [item for part in parts for item in part]))
            ]
    return recipes_selected_df

recipes_selected = ingredient_search()

preparation_time_available = recipes_raw_df['time'].unique()
time_selected = st.multiselect('Tempo de preparo:', preparation_time_available, placeholder='⏰ Escolha o tempo de preparo', help='Filtrar receitas pelo tempo de preparo')#⏳
if time_selected:
    recipes_selected = recipes_selected.loc[
        recipes_selected['time'].isin(time_selected)
        ]

recipes_raw_df['total_ingredients'] = recipes_raw_df['ingredients'].map(lambda parts: sum(len(part) for part in parts))
total_ingredients_available = sorted(recipes_raw_df['total_ingredients'].unique())
total_ingredients_selected = st.multiselect('Quantidade de ingredientes:', total_ingredients_available, select_all=False, placeholder='🛒 Escolha a quantidade de ingredientes', help='Filtrar receitas pela quantidade total de ingredientes')
if total_ingredients_selected:
    recipes_selected = recipes_selected.loc[
        recipes_raw_df['total_ingredients'].isin(total_ingredients_selected)
        ]

recipes_raw_df['total_steps'] = recipes_raw_df['steps'].map(lambda parts: sum(len(part) for part in parts))
total_steps_available = sorted(recipes_raw_df['total_steps'].unique())
total_steps_selected = st.multiselect('Quantidade de etapas:', total_steps_available, select_all=False, placeholder='📋 Escolha a quantidade de etapas', help='Filtrar receitas pela quantidade total de etapas de preparo') #📃
if total_steps_selected:
    recipes_selected = recipes_selected.loc[
        recipes_raw_df['total_steps'].isin(total_steps_selected)
        ]

st.subheader(f"{len(recipes_selected)} receitas:", divider="gray", icon="👩‍🍳")
st.dataframe(recipes_selected, hide_index=True)