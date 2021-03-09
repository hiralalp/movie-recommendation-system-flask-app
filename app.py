from flask import Flask, jsonify, request, Markup
import pandas as pd
import pickle
import requests
import flask
import random
app = Flask(__name__)

IMG_PATH = 'https://image.tmdb.org/t/p/w1280'

SEARCH_API = 'https://api.themoviedb.org/3/search/movie?api_key=5bcb29fc066251f1f8877ad9ffa5b10d&query="'


def getMovies(movies_list):
    final_movies = []
    for movie in movies_list:
        response = requests.get(SEARCH_API+movie)
        data = response.json()
        final_movies.append(data['results'][0])
    return final_movies


def get_content_based_recommendation(title, similarity, indices, df):
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(similarity[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:6]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return df['title'].iloc[movie_indices]


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/recommendation', methods=['POST'])
def recommendation():
    df = pd.read_csv('final_movies_data2.csv')
    df.reset_index(inplace=True)
    indices = pd.Series(df.index, index=df['title'])
    recommender = pickle.load(open("similarity.pickel", 'rb'))
    final_dic = request.form.to_dict()
    movie_name = final_dic['movie_name']
    if movie_name == "":
        return flask.render_template('error.html')
    try:
        final_list = get_content_based_recommendation(
            movie_name, recommender, indices, df)
    except:
        movie_name = random.choice(
            ['Miss Jerry', 'Home, Sweet Home', 'Cleopatra'])
        final_list = get_content_based_recommendation(
            movie_name, recommender, indices, df)

    getMovies(final_list)
    return flask.render_template('index.html', movies=getMovies(final_list), image_path=IMG_PATH)


if __name__ == '__main__':
    app.run(debug=True)
