import sqlalchemy
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UR OWN INFO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
Bootstrap(app)
db = SQLAlchemy(app)

API_KEY = "UR OWN INFO"
API_READ_ACCESS_TOCKEN = "UR OWN INFO"

url = "https://api.themoviedb.org/3/search/movie"
headers = {
    "accept": "application/json",
    "Authorization": "UR OWN INFO"
}


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String(250))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))


class EditForm(FlaskForm):
    your_rating = StringField('Your Rating(out of 10)', validators=[DataRequired()])
    your_review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('submit')


class AddMovie(FlaskForm):
    title = StringField("movie title", validators=[DataRequired()])
    submit = SubmitField("submit")


with app.app_context():
    db.create_all()


@app.route('/', methods=['POST', 'GET'])
def home():
    # all_movies = db.session.query(Movie).all()
    movie_id = request.args.get('movie_api_id')
    if movie_id:
        response = requests.get(url=f"https://api.themoviedb.org/3/movie/{movie_id}", headers=headers)
        movie_title = response.json()["title"]
        movie_img_url = f"https://image.tmdb.org/t/p/w500{response.json()['poster_path']}"
        movie_year = response.json()['release_date'].split('-')[0]
        movie_description = response.json()["overview"]

        new_movie = Movie(
            title=movie_title,
            year=movie_year,
            description=movie_description,
            rating=None,
            ranking=None,
            review=None,
            img_url=movie_img_url
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id_index=new_movie.id))
    # 👉👉👉👉非常重要，edit需要一个id_index（数据库id）， 前面步骤是index.html传播回去。
    # 👉👉👉👉这里如果redirect后，是另一个到edit的路径，需要重新传播一个次这个 id_index = new_movie.id
    # db.session.query().order_by(Movie.rating.desc())
    # db.session.query.order_by(Movie.rating.desc()).all()
    # db.session.query(Movie)
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    edit_form = EditForm()
    movie_id = request.args.get('id_index')
    # print(movie_id) movie_id 不对
    movie_selected = Movie.query.get(movie_id)
    if edit_form.validate_on_submit():
        movie_selected.rating = edit_form.your_rating.data
        movie_selected.review = edit_form.your_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", edit_form=edit_form, movie_selected=movie_selected)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id_index')
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['POST', 'GET'])
def add():
    add_form = AddMovie()
    # 找到需要添加的电影名称
    if add_form.validate_on_submit():
        movie_title = add_form.title.data
        params = {
            "query": movie_title,
            "include_adult": "false",
            "language": "en-US",
            "page": 1
        }
        response = requests.get(url, headers=headers, params=params)
        searched_movies = response.json()["results"]
        return render_template("select.html", searched_movies=searched_movies)

    return render_template("add.html", add_form=add_form)


if __name__ == '__main__':
    app.run(debug=True)
