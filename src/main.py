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
from models import db, Member, children
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/all', methods=['GET'])
def get_all_member():
    all_member = Member.query.order_by(Member.age.desc())
    all_member = list(map(lambda x: x.serialize("Member:"), all_member)) 
    return jsonify(all_member), 200

@app.route('/member/<int:id>', methods=['GET'])
def get_single_member(id):
    member = Member.query.get(id).serialize("Member")

    query_children = db.session.query(children).filter(children.c.parent_id == id).all()
    child = list( map(lambda x: Member.query.get(x[0]).serialize("Child"), query_children))

    query_parents = db.session.query(children).filter(children.c.child_id == id).all() 
    parents = list( map(lambda x: Member.query.get(x[1]).serialize("Parent"), query_parents))
    
    return jsonify(member, child, parents), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
