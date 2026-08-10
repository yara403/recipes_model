import pandas as pd
import spacy
import pt_core_news_sm
import re
import pandas as pd
import unicodedata

nlp = spacy.load('pt_core_news_sm')

recipes_df = pd.read_json('panelinha_dessert_recipes.json')
recipes_df = recipes_df.drop_duplicates(subset=['name', 'link'], keep='first', ignore_index=True)

ingredients_df = recipes_df[['name', 'ingredients']].copy()
ingredients_df = ingredients_df.explode('ingredients').explode('ingredients')

def convert_vulgar_fraction(text):
    text = list(text)
    fractions = [(i, unicodedata.normalize("NFKC", char)) for i, char in enumerate(text) if 'VULGAR FRACTION' in unicodedata.name(char)]
    if len(fractions) > 0:
        for pos, normalized_fraction in fractions:
            text[pos] = normalized_fraction
    return ''.join(text)

ingredients_df['ingredients_fractional'] = ingredients_df['ingredients'].apply(lambda x: convert_vulgar_fraction(x))

quantity_regex = '(?P<quantity>(\d+(?:\s*\d+)?(?:(?:\.|\,|\N{FRACTION SLASH})\d*)?))'
household_measures = 'xícaras|xícara|colheres|colher|copos|copo|pitadas|pitada|pacotes|pacote|envelopes|envelope|unidades|unidade|latas|lata|pedaços|pedaço|fatias|fatia|tbsp|tsp|cups|cup|caixas|caixa'
household_measure_regex = fr'(?P<mesure>(?:{household_measures})((?:\s*\((?:chá|sopa)\))|(?:\s*\[(?:chá|sopa)\]))?)'
standard_measures = 'grama|gramas|kg|g|ml|l|oz|lbs|mg'
standard_measure_regex = fr'(?P<mesure>{standard_measures})'
unit_regex = f'\s*(?P<quantity>\d+(?:\N{FRACTION SLASH}\d+)?\s+)(?!(?:de\s+)?(?:{household_measures}|{standard_measures}|cm|mm|m)(?:\s+|\)))'

standard_measure_pattern = re.compile(
    fr'\b{quantity_regex}(?:\s*){standard_measure_regex}\b', 
    flags=re.IGNORECASE
)
household_measure_pattern = re.compile(
    fr'\b{quantity_regex}(?:\s*\w*\s*){household_measure_regex}\s*(?:\+\s*)?\b',
    flags=re.IGNORECASE
)
more_household_patterns = re.compile(
    fr'(?:\s*\+\s*{quantity_regex}(?:\s*\w*\s*){household_measure_regex})+',
    flags=re.IGNORECASE
)
unit_pattern = re.compile(fr'{unit_regex}', re.IGNORECASE)

def create_entities(text):
    entities = {'entities': []}

    standard_match = standard_measure_pattern.search(text)
    if standard_match:
        entities['entities'].append((standard_match.start('quantity'), standard_match.end('mesure'), 'MEDIDA_PADRAO'))

    household_match = household_measure_pattern.search(text)
    if household_match:
        entities['entities'].append((household_match.start('quantity'), household_match.end('mesure'), 'MEDIDA_CASEIRA'))

    more_household_matches = more_household_patterns.search(text)
    if more_household_matches:
        entities['entities'].append((more_household_matches.start('quantity'), more_household_matches.end('mesure'), 'MEDIDA_CASEIRA'))

    unit_match = unit_pattern.search(text)
    if unit_match:
        entities['entities'].append((unit_match.start('quantity'), unit_match.end('quantity'), 'UNIDADE'))

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