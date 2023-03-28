from .extensions import db
from tgtg import TgtgClient

class TgtgSelf:
    def __init__(self, email=None, token=None, refresh_token=None, tgtg_id=None, tgtg_cookie=None):
        self.email = email
        self.token = token
        self.refresh_token = refresh_token
        self.tgtg_id = tgtg_id
        self.tgtg_cookie = tgtg_cookie
        self.client = None
        self.orders = None

    def index_of_last_order(self):
        self.__get_reedemed_orders()
        return self.orders[0]['order_id']

    def get_number_of_unmarked_orders(self, last_marked_order_id):
        self.__get_reedemed_orders()
        index_in_request = self.__index_of_last_order(last_marked_order_id)
        if index_in_request is None:
            return len(self.orders)
        elif index_in_request == 0 and last_marked_order_id is None:
            return 1

        return index_in_request

    def authorize(self):
        return TgtgClient(email=self.email).get_credentials()

    def __client(self):
        self.client = TgtgClient(access_token=self.token,
                               refresh_token=self.refresh_token,
                               user_id=self.tgtg_id,
                               cookie=self.tgtg_cookie)

    def __index_of_last_order(self, last_order_id):
        return next((index for (index, d) in enumerate(self.orders) if d["order_id"] == last_order_id), None)

    def __get_reedemed_orders(self):
        if self.orders is not None:
            return None

        if self.client is None:
            self.__client()

        orders_response = self.client.get_inactive(page=0, page_size=40)
        if orders_response is None:
            return None

        self.orders = [order for order in orders_response['orders'] if order["state"] == "REDEEMED"]


# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    main_service_id = db.Column(db.Integer, unique=True)
    token = db.Column(db.String, primary_key=False)
    refresh_token = db.Column(db.String, primary_key=False)
    tgtg_id = db.Column(db.String, primary_key=False)
    tgtg_cookie = db.Column(db.String, primary_key=False)
    last_order_id = db.Column(db.String, primary_key=False)

    def __init__(self, email, main_service_id, token=None, refresh_token=None, tgtg_id=None, tgtg_cookie=None):
        self.email = email
        self.main_service_id = main_service_id
        self.token = token
        self.refresh_token = refresh_token
        self.tgtg_id = tgtg_id
        self.tgtg_cookie = tgtg_cookie

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        # with app.app_context():
        return cls.query.get_or_404(id)

    def save(self):
        print('test')
        # with app.app_context():
        db.session.add(self)
        db.session.commit()

    def user_client(self):
        return TgtgSelf(
            token=self.token,
            refresh_token=self.refresh_token,
            tgtg_id=self.tgtg_id,
            tgtg_cookie=self.tgtg_cookie
        )

    def delete(self):
        db.session.delete(self)
        db.session.commit()
