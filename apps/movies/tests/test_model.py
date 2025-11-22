import pytest
from apps.movies.models import Movie


data_movie = {
    "title": "Drive (2011 film)",
    "description": "Drive is a 2011 American action drama film directed by Nicolas Winding Refn. The screenplay, written by Hossein Amini, is based on James Sallis's 2005 novel. ",
    "duration": 100,
    "poster_url": "https://en.wikipedia.org/wiki/The_Drive.jpg",
}


@pytest.mark.django_db
def test_create_movie():
    movie = Movie.objects.create(**data_movie)
    assert movie.title == data_movie["title"]
    assert movie.description == data_movie["description"]
    assert movie.duration == data_movie["duration"]
    assert movie.poster_url == data_movie["poster_url"]
