"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Vehicles, Planets, Favorites
import json
#from models import Person

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

# # Handle/serialize errors like a JSON object
# @app.errorhandler(APIException)
# def handle_invalid_usage(error):
#     return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():
    users = User.query.all()
    # Create a list to hold the serialized data for each user
    users_data = [user.serialize() for user in users]

    return jsonify(users_data), 200

@app.route('/peoples', methods=['GET'])
def getPeoples():
    all_peoples = Characters.query.all()
    characters_data = [character.serialize() for character in all_peoples]
    return jsonify(characters_data), 200

@app.route('/peoples/<int:people_id>', methods=['GET'])
def getPeople(people_id):
    print(people_id)
    if request.method == 'GET':
        userInfo = Characters.query.get(people_id)
        if userInfo is None:
            return jsonify({"message": "people id not found"}), 404
        return jsonify(userInfo.serialize()), 200


@app.route('/plantes', methods=['GET'])
def getPlanets():
    all_planets = Planets.query.all()
    planets_data = [planet.serialize() for planet in all_planets]

    return jsonify(planets_data), 200

@app.route('/planets/<int:planet_id>', methods=['GET', 'PUT'])
def getPlanet(planet_id):

    planetInfo = Planets.query.get(planet_id)
    data = request.get_json()
    if request.method == 'GET':
        if planetInfo is None:
            return jsonify({"message": "planet id is not fround"}), 404
        return jsonify(planetInfo.serialize()), 200 
    elif request.method == 'PUT':
        if planetInfo is None: 
            return jsonify({"message": "planet id is not fround"}), 404
        planetInfo = data
        return jsonify(planetInfo.serialize()), 200

@app.route('/users/favorites', methods=['GET'])
def getAllFavorites():

    userInfo = Favorites.query.all()
    if request.method == 'GET':
        if userInfo is None:
            return jsonify({"message": "planet id is not fround"}), 404
        favorite_data = [favorite.serialize() for favorite in userInfo]
        return jsonify(favorite_data), 200 
    
@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def getUserFavorites(user_id):

    userInfo = Favorites.query.all()
    if request.method == 'GET':
        if userInfo is None:
            return jsonify({"message": "planet id is not fround"}), 404
        favorite_data = [favorite.serialize() for favorite in userInfo if favorite.user_id == user_id]
        return jsonify(favorite_data), 200
    
@app.route('/favorite/people', methods=['POST'])
def generatePeopleFavorite():

    data = request.get_json()

       # Create a new favorite object
    new_favorite = Favorites(user_id=data.user_id, people_id=data.people_id)

    # Add the new favorite to the database
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 200

@app.route('/favorite/planet', methods=['POST'])
def generatePlanetFavorite():

    data = request.get_json()

       # Create a new favorite object
    new_favorite = Favorites(user_id=data.user_id, planet_id=data.planet_id)

    # Add the new favorite to the database
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 200

@app.route('/favorite/<int:favorite_id>', methods=['DELETE'])
def deleteFavId(favorite_id):

    favorite_to_delete = Favorites.query.get(favorite_id)
    # Add the new favorite to the database
    db.session.delete(favorite_to_delete)
    db.session.commit()

    return jsonify({"message": "Favorite deleted successfully"}), 200

@app.route('/vehicles', methods=['GET'])
def getVehicles():

    all_vehicles = Vehicles.query.all()
    vehicles_data = [vehicle.serialize() for vehicle in all_vehicles]

    return jsonify(vehicles_data), 200

@app.route('/vehicles/<int:vehicle_id>', methods=['GET', 'PUT'])
def getVehicle(vehicle_id):

    vehicleInfo = Vehicles.query.get(vehicle_id)
    data = request.get_json()
    if request.method == 'GET':
        if vehicleInfo is None:
            return jsonify({"message": "planet id is not fround"}), 404
        return jsonify(vehicleInfo.serialize()), 200 
    elif request.method == 'PUT':
        if vehicleInfo is None: 
            return jsonify({"message": "planet id is not fround"}), 404
        vehicleInfo = data
        return jsonify(vehicleInfo.serialize()), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
