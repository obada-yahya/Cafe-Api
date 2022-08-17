from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api_secret_key = "SECURE_API"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read Record


@app.route("/random")
def random():
    cafes = db.session.query(Cafe).all()
    cafe = cafes[randint(0, len(cafes) - 1)]
    return jsonify(cafe.to_dict())


@app.route("/get_all")
def get_all():
    cafes = db.session.query(Cafe).all()
    cafes_to_dict = list(map(lambda x: x.to_dict(), cafes))
    return jsonify(cafe=cafes_to_dict)


@app.route("/search")
def search():
    cafes = Cafe.query.filter_by(location=request.args.get("loc")).all()
    if len(cafes) > 0:
        return jsonify(cafe=list(map(lambda x: x.to_dict(), cafes)))
    ans = {
        "Not Found": "Sorry, we don't have a cafe at that location."
    }
    return jsonify(error=ans)

# HTTP POST - Create Record
def check_bool(x:str):
    if x.lower() in ["true", "yes", "y", "1"]:
        return True
    return False


@app.route("/add",methods=["POST","GET"])
def adding():
    if request.method == "POST":
        cafe = Cafe(name=request.form.get("name"),
                    map_url=request.form.get("map_url"),
                    img_url=request.form.get("img_url"),
                    location=request.form.get("location"),
                    seats=request.form.get("seats"),
                    has_toilet=check_bool(request.form.get("has_toilet")),
                    has_wifi=check_bool(request.form.get("has_wifi")),
                    has_sockets=check_bool(request.form.get("has_sockets")),
                    can_take_calls=check_bool(request.form.get("can_take_calls")),
                    coffee_price=request.form.get("coffee_price"))
        db.session.add(cafe)
        db.session.commit()
    return jsonify(response={"success":"Successfully added the new cafe."})

# HTTP PUT/PATCH - Update Record

@app.route("/update-price/<coffee_id>", methods=["PATCH"])
def update_price(coffee_id):
    cafe = db.session.query(Cafe).filter_by(id=coffee_id).first()
    if cafe:
        cafe.coffee_price = request.form.get("new_price")
        db.session.commit()
        return jsonify(success="Successfully updated the price.")
    return jsonify(error={"Not Found":"Sorry a cafe with that id was not found in the database."}),404

# HTTP DELETE - Delete Record

@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = Cafe.query.get(int(cafe_id))
    if request.form.get("api_key") != api_secret_key:
        return jsonify({"error":"Sorry, that's not allowed. Make sure you have the correct api_key"})
    elif cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response="The Cafe is successfully is deleted ")
    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"})

if __name__ == '__main__':
    app.run(debug=True)
