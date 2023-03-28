from flask import Blueprint, redirect, url_for, request
from tgtg import TgtgClient

from .models import User, TgtgSelf

import threading
import time

main = Blueprint('main', __name__)

@main.route("/")
def hello_world():
    print('hey!')
    print('hey Motherfucker!')
    return "Hello, World!", 200

@main.route("/authorize", methods=['POST'])
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


@main.route("/users/<id>")
def get_points(id):
    user_id = request.view_args['id']

    user = User.get_by_id(int(user_id))

    client = user.user_client()

    unmarked_orders_number = client.get_number_of_unmarked_orders(user.last_order_id)
    if unmarked_orders_number > 0:
        user.last_order_id = client.index_of_last_order()
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
    user.save()
    print("Ended successfully!")

# if __name__ == '__main__':
#     app.run()
