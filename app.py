from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector

app = Flask(__name__)

# database master user:
# admin
# COP4710!

# TODO: change secret key
app.secret_key = 'your_secret_key'

def price_to_dollars(price):
    return '$' * price

@app.route('/')
def index():
    if 'logged_in' in session:
        connection = mysql.connector.connect(
            host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
            user="admin",
            password="COP4710!",
            database="tally_munch"
        )
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM restaurant ORDER BY trend_counter DESC LIMIT 10")
        top_restaurants = cursor.fetchall()

        connection.close()

        for restaurant in top_restaurants:
            restaurant['price_display'] = price_to_dollars(restaurant['price'])

        return render_template('index.html', rows=top_restaurants)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: Authenticate the user
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/createaccount', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # TODO: Authenticate the user
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template('createaccount.html')   


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


@app.route('/search', methods=['POST', 'GET'])
def search():
    if 'logged_in' in session:
        if request.method == 'POST':
            search_query = request.form['restaurant']

            connection = mysql.connector.connect(
                host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
                user="admin",
                password="COP4710!",
                database="tally_munch"
            )
            cursor = connection.cursor(dictionary=True)

            sql_query = "SELECT * FROM restaurant WHERE name LIKE %s"
            cursor.execute(sql_query, ('%' + search_query + '%',))
            restaurants = cursor.fetchall()

            connection.close()

            return render_template('search.html', rows=restaurants)
        else:
            return render_template('search.html')
    else:
        return redirect(url_for('login'))

@app.route('/restaurant/<int:restaurant_id>')
def restaurant_info(restaurant_id):
    connection = mysql.connector.connect(
        host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
        user="admin",
        password="COP4710!",
        database="tally_munch"
    )
    cursor = connection.cursor(dictionary=True)

    # Execute MySQL query to fetch information about the restaurant with the specified ID
    cursor.execute("SELECT * FROM restaurant WHERE id = %s", (restaurant_id,))
    restaurant_info = cursor.fetchone()

    connection.close()

    return render_template('restaurant_info.html', restaurant=restaurant_info)


if __name__ == "__main__":
    app.run(debug=True)
