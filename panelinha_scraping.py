import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = 'https://panelinha.com.br/categoria/doces'
RECIPES_JSON_PATH = 'panelinha_dessert_recipes.json'
CLEANED_RECIPES_JSON_PATH = 'panelinha_dessert_recipes_cleaned.json'

def get_html(url):
    response = requests.get(url)
    if response.encoding == 'ISO-8859-1':
        response.encoding = 'UTF-8'
    html = response.text
    return BeautifulSoup(html, 'html.parser')

def get_number_of_pages():
    main_page = get_html(BASE_URL)
    pagination_links = main_page.find_all('a', class_='ais-Pagination-link')
    last_page_link = pagination_links.pop().get('href')
    number_of_pages = int(last_page_link.split('/').pop())
    return number_of_pages

def get_all_recipes() -> list:
    recipe_list = []
    for i in range(get_number_of_pages()):
        url = BASE_URL+f'/pagina/{i+1}'
        html_page = get_html(url)
        recipes = html_page.find_all('div', class_='f fc mod')
        for recipe in recipes:
            link = requests.compat.urljoin(BASE_URL, recipe.find('a').get('href'))
            full_recipe = {
                'name': str(recipe.find('h6').text.strip()),
                'category': 'doces',
                'link': link,
                'img': recipe.find('img').get('src')
            }
            recipe_page = get_html(link)
            full_recipe['description'] = get_description(recipe_page)
            full_recipe['ingredients'] = get_ingredients(recipe_page)
            
            author, time, serves = get_technical_specifications(recipe_page)
            full_recipe['author'] = author
            full_recipe['time'] = time
            full_recipe['serves'] = serves
            
            full_recipe['steps'] = get_steps(recipe_page)
            full_recipe['nutrients'] = {}
            recipe_list.append(full_recipe)
    return recipe_list

def get_description(recipe_page) -> str:
    recipe_description = recipe_page.find('div', id='recipe_header')
    return recipe_description.find('p').text.strip()

def get_ingredients(recipe_page) -> list:
    ingredient_sections = recipe_page.find_all('h5', string=re.compile('ingredientes', re.IGNORECASE))
    ingredients = []
    for section in ingredient_sections:
        ingredients_ul = section.find_next_sibling()
        ingredients.append([li.text.strip() for li in ingredients_ul.children if li.text.strip() != ''])
        
    return ingredients

def get_technical_specifications(recipe_page):
    stats_section = recipe_page.find('dl', class_='stats')
    values = stats_section.find_all('dd')
    return (x.text.strip() for x in values)

def get_steps(recipe_page) -> list:
    steps_sctions = recipe_page.find_all('h5', string=re.compile('modo de preparo', re.IGNORECASE))
    steps = []
    for section in steps_sctions:
        parent_section = section.find_parent('div').find_parent('div')
        steps_li = parent_section.find_all('li')
        steps.append([li.text.strip() for li in steps_li])
        
    return steps

def main():
    recipes = get_all_recipes()
    with open(RECIPES_JSON_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(recipes, indent=2))

if __name__ == "__main__":
    main()