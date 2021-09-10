import hmac
import sqlite3
from datetime import timedelta
from flask import Flask, request
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from flask_mail import Mail, Message


# user table
class User(object):
    def __init__(self, id, email, username, password):
        self.id = id
        self.email = email
        self.username = username
        self.password = password


def table():
    conn = sqlite3.connect('store.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users"
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "email TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


table()


def fetch_users():
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * from users')
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[1], data[2], data[3]))
    return new_data


users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)

# products table
class Products(object):
    def __init__(self, id, product_id, product_name, product_price, product_quantity):
        self.id = id
        self.product_id = product_id
        self.product_name = product_name
        self.product_price = product_price
        self.product_quantity = product_quantity
        # self.total = total


def product_table():
    conn = sqlite3.connect('store.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product"
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "product_id TEXT NOT NULL,"
                 "product_name TEXT NOT NULL,"
                 "product_price TEXT NOT NULL,"
                 "product_quantity TEXT NOT NULL)")
    print("product table created successfully")
    conn.close()


product_table()


def fetch_products():
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * from product')
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(Products(data[0], data[1], data[2], data[3], data[4]))
    return new_data


users2 = fetch_products()

app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config["JWT_EXPIRATION_DELTA"] = timedelta(days=1)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'isaacscassiem2003@gmail.com'
app.config['MAIL_PASSWORD'] = 'CassiemIsaacs@2003'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# user register
@app.route('/user-registration/', methods=['POST'])
def user_registration():
    response = {

    }
    if request.method == "POST":
        with sqlite3.connect("store.db") as conn:
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email,username,password) VALUES(?,?,?)",
                           (email, username, password))
            conn.commit()
            response["message"] = 'Success'
            response["status_code"] = 201

        msg = Message('Hello Message', sender='isaacscassiem2003@gmail.com', recipients=email)
        msg.body = "My email using Flask"
        mail.send(msg)
        return "Message sent"

    return response


# gets users
@app.route('/get-users/', methods=['GET'])
def get_users():
    response = {}
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        carts = cursor.fetchall()

    response['status_code'] = 201
    response['data'] = carts
    return response


# creates products
@app.route('/products-create/', methods=['POST'])
@jwt_required()
def products_create():
    response = {}

    if request.method == "POST":
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        product_quantity = request.form['product_price']
        product_price = request.form['product_quantity']
        # total = int(product_price) * int(product_quantity)

        with sqlite3.connect('store.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product (product_id, product_name, product_price,product_quantity) "
                           "VALUES(?, ?, ?, ?)",
                           (product_id, product_name, product_price, product_quantity))
            conn.commit()
            response['message'] = "item added successfully"
            response['status_code'] = 201
        return response


# show product
@app.route('/get-products/', methods=['GET'])
def get_products():
    response = {}
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")
        carts = cursor.fetchall()

    response['status_code'] = 201
    response['data'] = carts
    return response


# shows one product
@app.route('/get-product/<int:id>', methods=['GET'])
def get_product(id):
    response = {}
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id=" + str(id))
        carts = cursor.fetchall()

    response['status_code'] = 201
    response['data'] = carts
    return response


# delete product
@app.route("/delete-product/<int:id>", )
@jwt_required()
def delete_product(id):
    response = {}
    with sqlite3.connect("store.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(id))
        conn.commit()
        response['status_code'] = 201
        response['message'] = "product deleted successfully"
    return response


# route to edit products
@app.route('/edit-product/<int:id>', methods=['PUT'])
@jwt_required()
def edit_product(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('store.db') as conn:
            product_name = request.form['product_name']
            product_price = request.form['product_price']
            product_quantity = request.form['product_quantity']
            put_data = {}

            if product_name is not None:
                put_data["product_name"] = product_name
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_name =? WHERE id =?", (put_data['product_name'], id))
                conn.commit()
                response['message'] = "Update was successful"
                response["status_code"] = 201

            if product_price is not None:
                put_data["product_price"] = product_price
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_price =? WHERE id =?", (put_data['product_price'], id))
                conn.commit()
                response['message'] = "Update was successful"
                response["status_code"] = 201

            if product_quantity is not None:
                put_data["product_quantity"] = product_quantity
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_quantity =? WHERE id =?",
                               (put_data['product_quantity'], id))
                conn.commit()
                response['message'] = "Update was successful"
                response["status_code"] = 201
            return response


if __name__ == '__main__':
    app.run()
