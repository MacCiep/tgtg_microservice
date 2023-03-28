import threading
import os

from flask import Flask, jsonify, request
from tgtg import TgtgClient
import requests

from flask_sqlalchemy import SQLAlchemy
import time
from marshmallow import Schema, fields

app = Flask(__name__)

# Database connection:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://maciejciepluch@localhost/tgtg_db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_TGTG")
#postgres://tgtg_db_user:PwjMe9kas35rtaxGtgEQRgsi7WVD8S47@dpg-cghha2fdvk4ml9umcrpg-a/tgtg_db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = 'secret string'
db = SQLAlchemy(app)

PAGE_SIZE = 10

@app.route("/")
def hello_world():
    print('hey!')
    print('hey Motherfucker!')
    return "Hello, World!", 200

@app.route("/authorize", methods=['POST'])
def authorize():
    request_body = request.get_json()
    user_id = request_body['user_id']
    email = request_body['email']
    print(request_body['email'])

    new_user = User(
        email=email,
        main_service_id=user_id,
    )
    new_user.save()
    threading.Thread(target=authorize_user_thread, args=[new_user]).start()

    return {'user_id': new_user.id}, 201


@app.route("/users/<id>")
def get_points(id):
    user_id = request.view_args['id']

    with app.app_context():
        user = User.get_by_id(int(user_id))

    if user is None:
        return {'message': 'Not authorized'}, 404

    client = user.user_client()

    unmarked_orders_number = client.get_number_of_unmarked_orders(user.last_order_id)
    if unmarked_orders_number > 0:
        user.last_order_id = client.index_of_last_order()
        with app.app_context():
            user.save()

    return {'number_of_unmarked_orders': unmarked_orders_number}, 200

def authorize_user_thread(user):
    time.sleep(2)
    client = TgtgClient(email=user.email)
    credentials = client.get_credentials()
    # TODO: Implement error logic
    if credentials is None:
        print("Ended with failure!")

    user.token=credentials['access_token']
    user.refresh_token=credentials['refresh_token']
    user.tgtg_id = credentials['user_id']
    user.tgtg_cookie = credentials['cookie']
    with app.app_context():
        user.save()
    print("Ended successfully!")

if __name__ == '__main__':
    app.run()
