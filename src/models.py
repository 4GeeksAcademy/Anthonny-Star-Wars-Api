from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable = False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable = False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    favorite = db.relationship('Favorite', backref='user', uselist=True)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "fullname": self.fullname,
        }
    
    def serialize_fav(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            # do not serialize the password, its a security breach
            "favorites": list(map(lambda item: item.serialize(), self.favorite))
        }
    
class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    height = db.Column(db.String(100), nullable=False)
    mass = db.Column(db.String(100), nullable=False)
    hair_color = db.Column(db.String(100), nullable=False)
    skin_color = db.Column(db.String(100), nullable=False)
    eye_color = db.Column(db.String(100), nullable=False)
    birth_year = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable = False, default=datetime.now(timezone.utc))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "created_at": self.created_at
        }
    

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    diameter = db.Column(db.String(120), nullable=False)
    rotation_period = db.Column(db.String(120), nullable=False)
    orbital_period = db.Column(db.String(120), nullable=False)
    gravity = db.Column(db.String(120), nullable=False)
    population = db.Column(db.String(120), nullable=False)
    climate = db.Column(db.String(120), nullable=False)
    terrain = db.Column(db.String(120), nullable=False)
    surface_water = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "orbital_period": self.orbital_period,
            "rotation_period": self.rotation_period,
            "gravity": self.gravity,
            "population": self.population,
            "diameter": self.diameter,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water
        }


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)  

    def serialize(self):
        return {
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id 
        }