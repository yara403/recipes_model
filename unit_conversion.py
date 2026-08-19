import pandas as pd
import spacy
import pt_core_news_sm
import re
import pandas as pd
import unicodedata

nlp = spacy.load('pt_core_news_sm')

def convert_vulgar_fraction(text):
    text = list(text)
    fractions = [(i, unicodedata.normalize("NFKC", char)) for i, char in enumerate(text) if 'VULGAR FRACTION' in unicodedata.name(char)]
    if len(fractions) > 0:
        for pos, normalized_fraction in fractions:
            text[pos] = normalized_fraction
    return ''.join(text)

recipes_df = pd.read_json('panelinha_dessert_recipes.json')
recipes_df = recipes_df.drop_duplicates(subset=['name', 'link'], keep='first', ignore_index=True)

ingredients_df = recipes_df[['name', 'ingredients']].copy()
ingredients_df = ingredients_df.explode('ingredients').explode('ingredients')
ingredients_df['ingredients_fractional'] = ingredients_df['ingredients'].apply(lambda x: convert_vulgar_fraction(x))

standard_measures = 'grama|gramas|kg|g|ml|l|oz|lbs|mg'
household_measures = 'xícaras|xícara|colheres|colher|copos|copo|pitadas|pitada|pacotes|pacote|envelopes|envelope|unidades|unidade|latas|lata|pedaços|pedaço|fatias|fatia|tbsp|tsp|cups|cup|caixas|caixa'

quantity_regex = '(?P<quantity>(\d+\s+\d+\N{FRACTION SLASH}\d+|\d+\N{FRACTION SLASH}\d+|\d+(?!\s+\d+))(\.\d+|\,\d+)?)'

standard_measure_regex = fr'\b{quantity_regex}(?:\s*)(?P<mesure>{standard_measures})\b'
household_measure_regex = fr'{quantity_regex}(?:\s*\w*\s*)(?P<mesure>(?:{household_measures})((\s*\((chá|sopa)\))|(\s*\[(chá|sopa)\]))?)'
unit_regex = f'\s*{quantity_regex}\s+(?!(?:de\s+)?(?:{household_measures}|{standard_measures}|cm|mm|m)(?:\s+|\)))'

standard_measure_pattern = re.compile(
    fr'{standard_measure_regex}', 
    flags=re.IGNORECASE
)
household_measure_pattern = re.compile(
    fr'{household_measure_regex}',
    flags=re.IGNORECASE
)
unit_pattern = re.compile(
    fr'{unit_regex}', 
    re.IGNORECASE
)

def create_entities(text):
    entities = {'entities': []}

    standard_matches = standard_measure_pattern.finditer(text)
    for match in standard_matches:
        entities['entities'].append((match.start('quantity'), match.end('mesure'), 'MEDIDA_PADRAO'))

    household_matches = household_measure_pattern.finditer(text)
    for match in household_matches:
        entities['entities'].append((match.start('quantity'), match.end('mesure'), 'MEDIDA_CASEIRA'))

    unit_matches = unit_pattern.finditer(text)
    for match in unit_matches:
        entities['entities'].append((match.start('quantity'), match.end('quantity'), 'UNIDADE'))

    entities['entities'].sort(key=lambda x: x[0])
    return entities

ingredients_df['entities'] = ingredients_df['ingredients_fractional'].apply(create_entities)

print(ingredients_df.info())
#Unidades de medida padrão

#medida/grandeza de massa: Kg
#medida de capacidade (volume): L
#comprimento: m
#medida de tempo: s
#temperatura termodinâmica: K

#UNIDADES DE MEDIDA CASEIRA

#ANVISA
# Xícara de chá (200 cm3 ou ml)
# Copo (200 cm3 ou ml)
# Colher de sopa (10 cm3 ou ml)
# Colher de chá (5 cm3 ou ml)
# Prato raso (22 cm de diâmetro)
# Prato fundo (250 cm3 ou ml)

#PANELINHA
# 1 xícara (chá) = 240 ml
# 1 colher (sopa) = 15 ml
# 1 colher (chá) = 5 ml

#ALIMENTOS
#ESPECIARÍAS
#TEMPEROS