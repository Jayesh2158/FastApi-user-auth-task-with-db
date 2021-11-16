from . import main

def get_movie_genre(genres):
    import pdb;pdb.set_trace()
    movieList = []
    for movie in main.movies:
        # temp = jsonable_encoder.loads(movie)
        if movie['genres'] == genres:
            movieList.append(movie)
    return movieList

