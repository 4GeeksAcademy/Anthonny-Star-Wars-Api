import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Favorite, Planet
import requests

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {"msg": "Hello, this is your GET /user response "}
    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    people = list(map(lambda item: item.serialize(), people))
    return jsonify(people), 200


@app.route('/people/<int:theid>', methods=['GET'])
def get_one_people(people_id):
    people = People.query.get(people_id)
    if people is None:
        raise APIException("User not found", status_code=404)
    return jsonify(people.serialize()), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users = list(map(lambda item: item.serialize(), users))
    return jsonify(users), 200


@app.route("/people/population", methods=['GET'])
def get_people_population():
    response = requests.get("https://www.swapi.tech/api/people?page=l&limit=300")
    response = response.json().get("results")
    
    for item in response:
        result = requests.get(item.get("url")).json().get("result").get("properties")
        people = People(
            name=result.get("name"),
            height=result.get("height"),
            mass=result.get("mass"),
            hair_color=result.get("hair_color"),
            skin_color=result.get("skin_color"),
            eye_color=result.get("eye_color"),
            birth_year=result.get("birth_year"),
            gender=result.get("gender")
        )
        db.session.add(people)

    try: 
        db.session.commit()
        return jsonify("populando listo"), 200
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify("error"), 500


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    planets = list(map(lambda item: item.serialize(), planets))
    return jsonify(planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)
    return jsonify(planet.serialize()), 200


@app.route('/planets/populate', methods=['GET'])
def populate_planets():
    response = requests.get("https://www.swapi.tech/api/planets?page=1&limit=60")
    results = response.json().get("results")

    for item in results:
        planet_data = requests.get(item.get("url")).json().get("result").get("properties")
        planet = Planet(
            name=planet_data.get("name"),
            diameter=planet_data.get("diameter"),
            rotation_period=planet_data.get("rotation_period"),
            orbital_period=planet_data.get("orbital_period"),
            gravity=planet_data.get("gravity"),
            population=planet_data.get("population"),
            climate=planet_data.get("climate"),
            terrain=planet_data.get("terrain"),
            surface_water=planet_data.get("surface_water")
        )
        db.session.add(planet)
    
    try: 
        db.session.commit()
        return jsonify("Planets populated successfully"), 200
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify("Error populating planets"), 500


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    
    if not favorites:
        return jsonify({"msg": "No favorites found"}), 404
    
    return jsonify(list(map(lambda item: item.serialize(), favorites))), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_fav(planet_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Planet added to favorites"}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"msg": "Error adding planet"}), 400


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_fav(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    
    if favorite is None:
        return jsonify({"msg": "Favorite planet not found"}), 404
    
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Planet removed from favorites"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"msg": "Error removing planet"}), 400


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_fav(people_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, people_id=people_id)
    
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Person added to favorites"}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"msg": "Error adding person"}), 400


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_fav(people_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    
    if favorite is None:
        return jsonify({"msg": "Favorite person not found"}), 404
    
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Person removed from favorites"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"msg": "Error removing person"}), 400


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)