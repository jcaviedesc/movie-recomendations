from typing import Union
from fastapi import FastAPI
from urllib.parse import unquote
import pandas as pd
# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel
#Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

app = FastAPI()


@app.get("/")
def read_root():
    return "Hola Bienvendios a mi movies api"
# cargamos el dataset
movies_df = pd.read_csv("movies_dataset_processed.csv")

@app.get("/peliculas_idioma/{idioma}")
def peliculas_idioma(idioma: str):
    pelis_por_idioma = movies_df[movies_df['spoken_languages_name'].apply(lambda x: idioma in x)]
    print(pelis_por_idioma)
    
    return {'message': f'{len(pelis_por_idioma)} cantidad de películas fueron estrenadas en {idioma}'}

@app.get("/peliculas_duracion/{pelicula}")
def peliculas_duracion(pelicula: str):
    pelicula_row = movies_df[movies_df["title"] == pelicula]
    duracion = pelicula_row["runtime"].iloc[0]
    year = pelicula_row["year"].iloc[0]

    return {'pelicula': pelicula, 'duracion': float(duracion), 'year': int(year)}

@app.get("/franquicia/{franquicia}")
def franquicia(franquicia: str ):
    pelicula = movies_df[movies_df["belongs_to_collection_name"] == franquicia]
    ganancia = pelicula['revenue'].sum()
    promedio = pelicula['revenue'].mean()

    return f'La franquicia {franquicia} posee {pelicula.shape[0]} peliculas, una ganancia total de {ganancia} y una ganancia promedio de {promedio}'

@app.get("/pais/{pais}")
def peliculas_pais(pais: str ):
    pelis_por_pais = movies_df[movies_df['production_countries_name'].apply(lambda x: pais in x)]

    return f'Se produjeron {pelis_por_pais.shape[0]} películas en el país {pais}'
    
    
@app.get("/productora/{productora}")
def productoras_exitosas(productora: str):
    pelis_por_productora = movies_df[movies_df['production_companies_name'].apply(lambda x: productora in x)]
    revenue = pelis_por_productora['revenue'].sum()

    return f'La productora "{productora}" ha tenido un revenue de {revenue}'

@app.get("/director/{nombre_director}")
def get_director(nombre_director: str):
    '''
    Se ingresa el nombre de un director que se encuentre dentro de un dataset debiendo devolver el éxito 
    del mismo medido a través del retorno. Además, deberá devolver el nombre de cada película con la fecha 
    de lanzamiento, retorno individual, costo y ganancia de la misma, en formato lista.
    '''
    pelis_por_director = movies_df[movies_df['director'] == nombre_director]
    revenue = pelis_por_director['revenue'].sum()
    filter_data = pelis_por_director[['title','release_date','revenue','budget','return_of_investment']]
    # Convertir el DataFrame a una lista de objetos
    lista_pelis = filter_data.to_dict(orient='records')

    return {'director': nombre_director, 'total_revenue': revenue, 'movies': lista_pelis}



#Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

#Replace NaN with an empty string
movies_df['overview'] = movies_df['overview'].fillna('')

#Construct the required TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(movies_df['overview'])

#Construct a reverse map of indices and movie titles
indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(title, cosine_sim=cosine_sim):
    # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:6]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return movies_df['title'].iloc[movie_indices]

@app.get("/recomendaciones/{titulo}")
def recomendacion(titulo:str):
    return get_recommendations(titulo)