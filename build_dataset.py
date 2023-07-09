#!/usr/bin/env python
# coding: utf-8

# In[155]:


import pandas as pd
from ast import literal_eval
import numpy as np


# ## carga de datos 

# In[156]:


df = pd.read_csv('Dataset/movies_dataset.csv')
df_credits = pd.read_csv('Dataset/credits.csv')

# describo los datos
# print(df.describe())



# In[157]:


df_credits.columns = ['cast','crew','id']
df_credits['id'] = pd.to_numeric(df_credits['id'], errors='coerce').fillna(-1).astype("int64")
df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(-1).astype("int64")
df = df.merge(df_credits,on='id')


# In[158]:


def safe_literal_list_eval(x):
    try:
        return literal_eval(x)
    except Exception:
        return []


# In[159]:


# Parse the stringified features into their corresponding python objects
features = ['cast','crew', 'genres', 'production_companies', 'spoken_languages', 'production_countries']
for feature in features:
    df[feature] = df[feature].apply(safe_literal_list_eval)


# In[160]:


# Get the director's name from the crew feature. If director is not listed, return NaN
def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan


# In[161]:


# Returns the entire list
def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        return names

    #Return empty list in case of missing/malformed data
    return []


# In[162]:


# Define new director, cast, genres  features that are in a suitable form.
df['director'] = df['crew'].apply(get_director)

features = ['cast', 'genres']
for feature in features:
    df[feature] = df[feature].apply(get_list)



# In[164]:


def safe_literal_eval(x):
    try:
        return literal_eval(x) if pd.notnull(x) else {}
    except Exception:
        return {} # si no podemos convertir a diccionario retornamos uno vacio
    
def get_dic_value_by_key(key):
    def get_value(x):
        try:
            return x.get(key, '')
        except Exception:
            return '-'
    return get_value


# In[165]:


# Convertir la columna 'belongs_to_collection' de cadena a diccionario
df['belongs_to_collection'] = df['belongs_to_collection'].fillna('{}')

df['belongs_to_collection'] = df['belongs_to_collection'].apply(safe_literal_eval)

df['belongs_to_collection_name'] = df['belongs_to_collection'].apply(get_dic_value_by_key('name'))



# In[166]:


def get_dic_value_from_list(key):
    def map_key(x):
        try:
            return [str(i.get(key,'') ) for i in x]
        except Exception:
            print(f'key {key} with val {x} is type {type(x)}')
            return [] 
        
    return map_key


# In[167]:


# Convertir la columna 'production_companies' de cadena a una lista de diccionarios
# df['production_companies'] = df['production_companies'].apply(lambda x: eval(x) if pd.notnull(x) else [])
# Crear una nueva columna 'production_companies_name' con la concatenación de las claves 'name' de los objetos
df['production_companies_name'] = df['production_companies'].apply(get_dic_value_from_list('name'))

df[['production_companies','production_companies_name']].head(5)


# In[181]:


#spoken_languages
# Crear una nueva columna 'spoken_languages_name' con la concatenación de las claves 'name' de los objetos
df['spoken_languages_name'] = df['spoken_languages'].apply(get_dic_value_from_list('name')).astype("string")

df[['title','spoken_languages','spoken_languages_name']]


# In[169]:


#production_countries
# Crear una nueva columna 'spoken_languages_name' con la concatenación de las claves 'name' de los objetos
df['production_countries_name'] = df['production_countries'].apply(get_dic_value_from_list('name')).astype("string")

df[['production_countries', 'production_countries_name']]


# In[170]:


#Los valores nulos de los campos revenue, budget deben ser rellenados por el número 0
df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0).astype("Float32")
df["budget"] = pd.to_numeric(df['budget'], errors='coerce').fillna(0).astype("Float32")



# In[171]:


#Los valores nulos del campo release_date deben eliminarse.
num_datos = len(df)
df=df.dropna(subset=['release_date'])
df['release_date']


# In[172]:


# De haber fechas, deberán tener el formato AAAA-mm-dd, además deberán crear la columna release_year 
# donde extraerán el año de la fecha de estreno.

# Convierto la columna 'release_date' al tipo de dato datetime para poder obtener el año
df['release_date'] = pd.to_datetime(df['release_date'], format='%Y-%m-%d', errors="coerce")

# borro los datos que no pueden ser convertidos a fecha
df=df.dropna(subset=['release_date'])

# creo la columna 'year' con el año extraído de 'release_date'
df['year'] = df['release_date'].dt.year

df['year']


# In[173]:


'''
Crear la columna con el retorno de inversión, llamada return con los campos revenue y budget,
dividiendo estas dos últimas revenue / budget, cuando no hay datos disponibles para calcularlo, 
deberá tomar el valor 0.
'''
#creo la columna retorno de inversión 
df['return_of_investment'] = df.apply(lambda row: row['revenue'] / row['budget'] if row['revenue'] > 0 and row['budget'] > 0 else 0, axis=1)


# In[174]:


# Eliminar las columnas no utilizadas
columnas_no_utilizadas = ['video', 'imdb_id', 'adult', 'original_title', 'poster_path', 'homepage', 'belongs_to_collection', 'genres','production_companies','production_countries']
df = df.drop(columnas_no_utilizadas, axis=1)


# In[175]:


# guardo la dataset transformado en un file .csv
df.to_csv('movies_dataset_processed.csv', index=False)

