import pytest
from apps.movies.models import Movie


data_movie = {
    "title": "Transformers(2007)",
    "description": "The Transformers movie franchise is a series of live-action science fiction films based on the Hasbro toy line about warring factions of shape-shifting alien robots",
    "duration": 143,
    "poster_url": "https://en.wikipedia.org/wiki/Transformers_(film)#/media/File:Transformers07.jpg",
}


@pytest.fixture
def movie(db) -> Movie:
    return Movie.objects.create(**data_movie)
