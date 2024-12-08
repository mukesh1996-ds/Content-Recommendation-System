# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 10:10:20 2024

@author: Monu Sharma
"""

import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity

## Load the required datasets for this projects
movies = pd.read_csv('dataset/tmdb_5000_movies.csv')
credits = pd.read_csv('dataset/tmdb_5000_credits.csv')

## Let's check the top records for both the datasets 
print(movies.head(1))
print(credits.head(1))

# merging the columns 
movies = movies.merge(credits,on='title')
movies.shape

movies.info()

## Let's select the required columns in the dataframe for our project
movies = movies[['movie_id', "title",'overview','genres','keywords','cast','crew']]
movies.head()

## Let's check the missing values 
movies.isnull().sum()

## As we can see that overview column has 3 missing values which is not a big number then we can drop it. 
movies.dropna(inplace=True)

## Let's check the missing values 
movies.isnull().sum()

## Let's check the duplicate columns 
movies.duplicated().sum()

## Let's understand the data 
movies.iloc[0].genres

## The output is a list of dictionaries to preprocess this we can create an helper function

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
        return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords']=movies['keywords'].apply(convert)

def convert_cast(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter !=3:
            L.append(i['name'])
            counter+=1
        else:
            break
    return L

movies['cast'] = movies['cast'].apply(convert_cast)

def fetch_director(obj):
    L=[]
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

movies['crew']=movies['crew'].apply(fetch_director)
movies['overview'] = movies['overview'].apply(lambda x:x.split())
movies['genres'] = movies['genres'].apply(
    lambda x: [i.replace(" ", "") for i in x] if x is not None else x
)
movies['keywords']=movies['keywords'].apply(
    lambda x: [i.replace(" ", "") for i in x] if x is not None else x
)
movies['cast']=movies['cast'].apply(
    lambda x: [i.replace(" ", "") for i in x] if x is not None else x
)
movies['crew']=movies['crew'].apply(
    lambda x: [i.replace(" ", "") for i in x] if x is not None else x
)

movies['tags']=movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
movies.head()

## creating new dataframe to save all this 
new_df=movies[['movie_id','title','tags']]
new_df['tags'] = new_df['tags'].apply(
    lambda x: " ".join(x) if isinstance(x, (list, tuple)) else str(x)
)

new_df['tags']=new_df['tags'].apply(lambda x:x.lower())


ps=PorterStemmer()
def stem(text):
    y=[]
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

new_df['tags'] = new_df['tags'].apply(stem)

## Text Vectorization using Bag of Words
cv=CountVectorizer(max_features=5000,stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
cv.get_feature_names_out()

## Let's calculate the cosine similarites as we will calculate the angles between each vectors
similarity = cosine_similarity(vectors)
sorted(similarity[0],reverse=True)
sorted(list(enumerate(similarity[0])),reverse=True,key=lambda x:x[1])[1:6]

def recommend(movie):
    movie_index=new_df[new_df['title'] == movie].index[0]
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
    
    for i in movies_list:
        print(new_df.iloc[i[0]].title)

recommend('Avatar')

## Let's create a website now as my recommendation system is ready.
import pickle
pickle.dump(new_df,open('movies.pkl','wb'))

new_df['title'].values
