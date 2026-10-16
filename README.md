# Model recipes project

Este é um projeto voltado a criação de um modelo de machine learning para predição de testes sensoriais de receitas culinárias adaptadas aos limites de gordura saturada, açúcares adicionados e sódio estabelecidos pela ANVISA.

Um web scraping, implementado com a biblioteca BeautifulSoup, integra a primeira parte deste projeto. Receitas culinárias de doces do site [panelinha.com.br](https://panelinha.com.br) foram utilizadas como fonte para extração dos dados que compõem o banco de dados de treinamento deste projeto.

A segunda parte, composta por um modelo de Reconhecimento de Entidades Nomeadas (NER), identifica alimentos e medidas de peso/volume comuns nas descrições de receitas culinárias. Reconhecer estas entidades é imprescindível ao cálculo da composição nutricional das receitas.

O banco de dados e a identificação de entidades pode ser acessada através da página [recipesmodel.streamlit.app](https://recipesmodel.streamlit.app). Teste e depois me conte sobre sua experiência/dúvidas, caso tenha interesse.
<img width="300" height="525" alt="modelrecipes-page_mobile" src="https://github.com/user-attachments/assets/0d180ce5-02c4-41fc-86b4-6083e141ce50" />

***

This project is intended to gather dessert recipes from web sites specialised in cooking and store information like ingredients, nutrients and classification regarding the amount of saturated fat, increased sugars, and sodium of each desserts into a dataset.

A web scraper, implemented using the BeautifulSoup library, forms the first part of this project. Dessert recipes from the [panelinha.com.br](https://panelinha.com.br) website were used as the source for extracting the data that makes up this project's training database.

The second part, consisting of a Named Entity Recognition (NER) model, identifies foods and common weight/volume measurements in cooking recipe descriptions. Recognizing these entities is essential for calculating the recipes' nutritional composition.

The database and entity identification can be accessed through the [recipesmodel.streamlit.app](https://recipesmodel.streamlit.app). Test it out and feel free to share your experience or ask any questions if you're interested!
