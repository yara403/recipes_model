import pandas as pd
import re
import pandas as pd
import unicodedata

standard_measures = 'grama|gramas|kg|g|litros|litro|ml|l|oz|lbs|mg'
household_measures = 'xícaras|xícara|colheres|colher|copos|copo|potes|pote|pitadas|pitada|pacotes|pacote|envelopes|envelope|unidades|unidade|latas|lata|fatias|fatia|tabletes|tablete|saquinhos|saquinho|tbsp|tsp|cups|cup|caixas|caixa|bolas|bola'
informal_measures = 'dúzias|dúzia|pencas|penca|dentes|dente|espigas|espiga|bagas|baga|gotas|gota|ramas|rama|ramos|ramo|cachos|cacho|metades|metade|cavidades|cavidade|pedaços|pedaço'

quantity_regex = '(?P<quantity>(\d+\s+\d+\N{FRACTION SLASH}\d+|\d+\N{FRACTION SLASH}\d+|\d+(?!\s+\d+))(\.\d+|\,\d+)?)'

standard_measure_regex = fr'\b{quantity_regex}(?:\s*)(?P<measure>{standard_measures})\b'
household_measure_regex = fr'{quantity_regex}(?:\s*\w*\s*)(?P<measure>(?:{household_measures})((\s*\((chá|sopa)\))|(\s*\[(chá|sopa)\]))?)'
informal_measure_regex = fr'{quantity_regex}\s+(?P<measure>{informal_measures})\b'
unit_regex = f'\s*{quantity_regex}\s+(?!(?:de\s+)?(?:{household_measures}|{standard_measures}|{informal_measures}|cm|mm|m)(?:\s+|\,|\)))'

standard_measure_pattern = re.compile(
    fr'{standard_measure_regex}', 
    flags=re.IGNORECASE
)
household_measure_pattern = re.compile(
    fr'{household_measure_regex}',
    flags=re.IGNORECASE
)
informal_measure_pattern = re.compile(
    fr'{informal_measure_regex}',
    flags=re.IGNORECASE
)
unit_pattern = re.compile(
    fr'{unit_regex}', 
    re.IGNORECASE
)

def convert_vulgar_fraction(text):
    text = list(text)
    fractions = [(i, unicodedata.normalize("NFKC", char)) for i, char in enumerate(text) if 'VULGAR FRACTION' in unicodedata.name(char)]
    if len(fractions) > 0:
        for pos, normalized_fraction in fractions:
            text[pos] = normalized_fraction
    return ''.join(text)

def remove_verbose(text):
    adjectives = '((grand|fort|fervent|quent|firm)(es|e))|(?:(?:pequen|médi|variad|debulhad|peneirad|filtrad|morn|derretid|congelad|gelad|refrigerad|fri|amanhecid|madur|preparad|amassad|triturad|quebrad|ralad|picad|descascad|lavad|cortad|coad|fin|gross)(?:as|a|os|o))'
    instructions = 'para\s+(?:caramelizar|enrolar|pincelar|polvilhar|untar|decorar|fritar|passar|hidratar|assar|dourar|servir|prensa)|na hora'
    modes = 'bem(?:\s+\w+)*|de\s+preferência|a\s+gosto|o\s+quanto\s+baste|sem sementes|sem semente|em\s+(?:(?:cub|palit|pedac|pedaç)(?:inhos|inho|os|o)|(?:temperatura ambiente|ponto(?:\s+de)?\s+pomada|(?:(?:gota|grão|tira)(?:s)?)|callets|pasta|lata))|(?:com\s+palha)'

    adjectives_regex = fr'\b({adjectives}\,?)'
    for adj in re.finditer(adjectives_regex, text):
        text = re.sub(adj.group(1), '#', text, re.IGNORECASE)

    modes_regex = fr'(\b{modes}\,?)'
    for mode in re.finditer(modes_regex, text):
        text = re.sub(mode.group(1), '#', text, re.IGNORECASE)

    instructions_regex = fr'(\b{instructions})'
    for instruction in re.finditer(instructions_regex, text):
        text = re.sub(instruction.group(1), '#', text, re.IGNORECASE)

    text = re.sub(r'(\s+\#((\s+\d+\%?)|(\s+\w+))*)+|^(\#\s+)*', '', text, re.IGNORECASE).strip()
    
    miscellaneous_regex = '((cubos|cubo)\s+de\s+)|((tiras|tira|sobras|sobra)\s*((de|da)\s+)?)|(generos(as|os|a|o)\s+(de\s+)?)|((\s+com)?\s+cerca\s+de)$|(\s+e$)|\,$|^(de\s+)|^(da\s+)|^(do\s+)|(\s+de)$|receita\s+de\s+'
    text = re.sub(miscellaneous_regex, '', text, re.IGNORECASE).strip()

    utensils_regex = '(^(fôrm|form|canud|pincel|papel-manteiga)\w*)(\s+\w+)*'
    text = re.sub(utensils_regex, '', text, re.IGNORECASE).strip()

    items = re.sub(r'(\,\s+(?!torrad))|(\s+\be\b\s+(?!(sem|torrad|moíd)))|(\s+\bou\b\s+(?!de))', '#', text)

    if items == '':
        return []

    return items.split('#')

def clean_ingredient_description(description):
    description = re.sub(
        household_measure_pattern, 
        '', 
        re.sub(standard_measure_pattern, '', 
               re.sub(informal_measure_pattern, '', description)
        )
    ).strip()
    description = re.sub(r'^de\s+|(\s+de|\s+ou)$', '', description)
    description = re.sub(fr'\s*\((\w+\s+)*({quantity_regex})?(\s+\w*\-?\,?)*\)\s*', '', description)
    description = re.sub(fr'\s+\((cerca)?((\s+\w+)*|{household_measure_regex}|(\s+\+\s+))\s*\)', '', description)
    description = re.sub(fr'\s*\((\,\s+)?(((\w+(\-\w+)?)|(\d+\%?))\,?\.*\:?\s*)*\)', '', description)
    description = re.sub(r'(\s*\+\s*(de)?\s*)*', '', description)
    description = re.sub(r'\s*\((\s*\/\s*\d*)(\s+\w+)*\s*\)', '', description)
    description = re.sub(fr'\s*{quantity_regex}\s*(cm|mm|m)\b(\s+\w+)*', '', description)

    if re.search(unit_pattern, description):
        desc = re.sub(quantity_regex, '##', description)
        parts = re.split('##', desc)
        if parts[0] == '':
            description = [
                re.sub(
                    r'^de\s+', 
                    '', 
                    parts.pop().strip()
                )
            ]
        else:
            description = [parts[0].strip(), parts.pop().strip()]

    if type(description) != list:
        description = [description]
    
    return description

from enum import Enum
class Entity(Enum):
    STANDARD = 'MEDIDA_PADRAO'
    HOUSEHOLD = 'MEDIDA_CASEIRA'
    INFORMAL = 'MEDIDA_INFORMAL'
    UNIT = 'UNIDADE'
    FOOD = 'ALIMENTO'

def create_entities(text):
    entities = {'entities': []}

    standard_matches = standard_measure_pattern.finditer(text)
    for match in standard_matches:
        entities['entities'].append((match.start('quantity'), match.end('measure'), Entity.STANDARD.value))

    household_matches = household_measure_pattern.finditer(text)
    for match in household_matches:
        entities['entities'].append((match.start('quantity'), match.end('measure'), Entity.HOUSEHOLD.value))

    informal_matches = informal_measure_pattern.finditer(text)
    for match in informal_matches:
        entities['entities'].append((match.start('quantity'), match.end('measure'), Entity.INFORMAL.value))

    unit_matches = unit_pattern.finditer(text)
    for match in unit_matches:
        entities['entities'].append((match.start('quantity'), match.end('quantity'), Entity.UNIT.value))

    ingredient = clean_ingredient_description(text)
    ingredient_only = ''
    for part in ingredient:
        part = remove_verbose(part)
        for item in part:
            item_part_match = re.search(re.escape(item), text)
            if item_part_match:
                entities['entities'].append((item_part_match.start(), item_part_match.end(), Entity.FOOD.value))
                ingredient_only += item + " "        

    entities['entities'].sort(key=lambda x: x[0])
    return entities, ingredient_only.strip()

def get_ingredient_entities_df():
    recipes_df = pd.read_json('panelinha_dessert_recipes.json')
    recipes_df = recipes_df.drop_duplicates(subset=['name', 'link'], keep='first', ignore_index=True)

    ingredients_df = recipes_df[['name', 'ingredients']].copy()
    ingredients_df = ingredients_df.explode('ingredients').explode('ingredients')

    ingredients_df['ingredients_fractional'] = ingredients_df['ingredients'].apply(lambda x: convert_vulgar_fraction(x))
    ingredients_df['entity_food'] = ingredients_df['ingredients_fractional'].map(create_entities)
    ingredients_df['entity'] = ingredients_df['entity_food'].map(lambda entity_food: entity_food[0])
    ingredients_df['food'] = ingredients_df['entity_food'].map(lambda entity_food: entity_food[1])
    ingredients_df.drop(columns=['entity_food'], inplace=True)
    ingredients_df = fix_outliers(ingredients_df)
    return ingredients_df

def fix_outliers(ingredients_df):
    ingredients_df.loc[ingredients_df['ingredients_fractional'] == '1 panetone caseiro de 500 g', 'entity'] = ingredients_df[ingredients_df['ingredients_fractional'] == '1 panetone caseiro de 500 g'].entity.map(lambda x: {'entities': x['entities'][:-1]})
    ingredients_df.loc[ingredients_df['ingredients_fractional'] == '2 tiras finas da casca de limão', ['entity', 'food']] = {'entities': [(0, 1, 'UNIDADE'), (17, 31, 'ALIMENTO')]}, 'casca de limão'
    ingredients_df.loc[ingredients_df['ingredients'] == '¼ de xícara (chá) de banana-passa cortada em rodelas 1 cm', 'entity']  = ingredients_df[ingredients_df['ingredients'] == '¼ de xícara (chá) de banana-passa cortada em rodelas 1 cm'].entity.map(lambda x: {'entities': x['entities'][:-1]})
    ingredients_df.loc[(ingredients_df['name'] == 'Ovinhos pintados') & (ingredients_df['food'] == 'ovos brancos'), ['entity', 'food']] = {'entities': [(0, 1, 'UNIDADE')]}, ''
    ingredients_df.loc[(ingredients_df['name'] == 'Ovinhos de chocolate') & (ingredients_df['food'] == 'ovos brancos'), ['entity', 'food']] = {'entities': [(0, 1, 'UNIDADE')]}, ''
    ingredients_df.loc[ingredients_df['ingredients'] == '6 folhas bem bonitas de rosa', ['entity', 'food']] = {'entities': [(0, 1, 'UNIDADE'), (2, 8, 'ALIMENTO'), (21, 28, 'ALIMENTO')]}, 'folhas de rosa'
    ingredients_df.loc[ingredients_df['ingredients'] == '4 colheres (sopa) do recheio de sua preferência (geléia de frutas, doce de leite, goiabada cremosa)', ['entity', 'food']] = {'entities': [(0, 17, 'MEDIDA_CASEIRA'), (49, 65, 'ALIMENTO'), (67, 80, 'ALIMENTO'), (82, 98, 'ALIMENTO')]}, 'geléia de frutas, doce de leite, goiabada cremosa'
    ingredients_df.loc[ingredients_df['ingredients'] == '¾ de xícara (chá) de blueberry (ou mirtilo)', ['entity', 'food']] = {'entities': [(0, 19, 'MEDIDA_CASEIRA'), (23, 32, 'ALIMENTO'), (37, 44, 'ALIMENTO')]}, 'blueberry, mirtilo'
    ingredients_df.loc[ingredients_df['ingredients'] == 'corantes para chocolate (hipossolúveis) , nas cores: vermelho, azul e amarelo', ['entity', 'food']] = {'entities': [(0, 23, 'ALIMENTO')]}, 'corantes para chocolate'
    ingredients_df.drop(ingredients_df.query("name == 'Casca de ovos para decorar e rechear'").index, inplace=True)
    ingredients_df.loc[ingredients_df['ingredients'] == '1 xícara (chá) de castanha-de-caju torrada, sem sal (cerca de 200g)', ['entity', 'food']] = {'entities': [(0, 14, 'MEDIDA_CASEIRA'), (18, 51, 'ALIMENTO'), (62, 66, 'MEDIDA_PADRAO')]}, 'castanha-de-caju torrada, sem sal'
    ingredients_df.loc[ingredients_df['ingredients'] == '⅓ de xícara (chá) de castanha-de-caju torrada, sem sal', ['entity', 'food']] = {'entities': [(0, 19, 'MEDIDA_CASEIRA'), (23, 56, 'ALIMENTO')]}, 'castanha-de-caju torrada, sem sal'
    ingredients_df.loc[ingredients_df['ingredients'] == '2½ colheres (sopa) de óleo (ou manteiga derretida)', ['entity', 'food']] = {'entities': [(0, 20, 'MEDIDA_CASEIRA'), (24, 28, 'ALIMENTO'), (33, 41, 'ALIMENTO')]}, 'óleo manteiga'
    ingredients_df.loc[ingredients_df['ingredients'] == 'óleo (ou manteiga) para untar a frigideira', ['entity', 'food']] = {'entities': [(0, 4, 'ALIMENTO'), (9, 17, 'ALIMENTO')]}, 'óleo manteiga'
    ingredients_df.loc[ingredients_df['ingredients'] == '1½ xícara (chá) de frutas variadas picadas (melão, morango, kiwi...)', ['entity', 'food']] = {'entities': [(0, 17, 'MEDIDA_CASEIRA'), (21, 27, 'ALIMENTO'), (46, 51, 'ALIMENTO'), (53, 60, 'ALIMENTO'), (62, 66, 'ALIMENTO')]}, 'frutas melão morango kiwi'
    ingredients_df.loc[ingredients_df['ingredients'] == '1 colher (chá) de raspas de laranja ou de limão', ['entity', 'food']] = {'entities': [(0, 14, 'MEDIDA_CASEIRA'), (18, 35, 'ALIMENTO'), (42, 47, 'ALIMENTO')]}, 'raspas de laranja limão'
    ingredients_df.loc[ingredients_df['ingredients'] == '½ xícara (chá) de vinho tinto (ou 1 xícara (chá) de vinho Marsala)', ['entity', 'food']] = {'entities': [(0, 16, 'MEDIDA_CASEIRA'), (20, 31, 'ALIMENTO'), (36, 50, 'MEDIDA_CASEIRA'), (54, 67, 'ALIMENTO')]}, 'vinho tinto vinho Marsala'
    ingredients_df.loc[ingredients_df['ingredients'] == '2½ xícaras (chá) de fruta vermelha (morango, framboesa e amora - cerca de 350 g)', ['entity', 'food']] = {'entities': [(0, 18, 'MEDIDA_CASEIRA'), (22, 36, 'ALIMENTO'), (38, 45, 'ALIMENTO'), (47, 56, 'ALIMENTO'), (59, 64, 'ALIMENTO'), (76, 81, 'MEDIDA_PADRAO')]}, 'fruta vermelha morango framboesa amora'
    ingredients_df.loc[ingredients_df['ingredients'] == 'óleo (ou manteiga) para untar a assadeira', ['entity', 'food']] = {'entities': [(0, 4, 'ALIMENTO'), (9, 17, 'ALIMENTO')]}, 'óleo manteiga'
    ingredients_df.loc[ingredients_df['ingredients'] == '¼ de xícara (chá) de café coado, água ou o licor de sua preferência', ['entity', 'food']] = {'entities': [(0, 19, 'MEDIDA_CASEIRA'), (23, 27, 'ALIMENTO'), (35, 39, 'ALIMENTO'), (45, 50, 'ALIMENTO')]}, 'café água licor'
    ingredients_df.loc[ingredients_df['ingredients'] == '1 xícara (chá) de gotas de chocolate ou chocolate cortado em cubinhos (cerca de 150 g)', ['entity', 'food']] = {'entities': [(0, 14, 'MEDIDA_CASEIRA'), (18, 36, 'ALIMENTO'), (40, 49, 'ALIMENTO'), (80, 85, 'MEDIDA_PADRAO')]}, 'gotas de chocolate chocolate'
    ingredients_df.loc[ingredients_df['ingredients'] == '2½ xícaras (chá) de frutas vermelhas congeladas (cerca de 350g de morango, framboesa e amora)', ['entity', 'food']] = {'entities': [(0, 18, 'MEDIDA_CASEIRA'), (22, 38, 'ALIMENTO'), (60, 64, 'MEDIDA_PADRAO'), (68, 75, 'ALIMENTO'), (77, 86, 'ALIMENTO'), (89, 94, 'ALIMENTO')]}, 'frutas vermelhas morango framboesa amora'
    ingredients_df.loc[ingredients_df['ingredients'].str.contains(fr'\b{quantity_regex}\s+carambola\b'), ['entity', 'food']] = {'entities': [(0, 1, 'UNIDADE'), (2, 11, 'ALIMENTO')]}, 'carambola'
    ingredients_df.loc[ingredients_df['ingredients'].str.contains(fr'\b{quantity_regex}\s+carambolas'), ['entity', 'food']] = {'entities': [(0, 1, 'UNIDADE'), (2, 12, 'ALIMENTO')]}, 'carambolas'    
    
    return ingredients_df

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