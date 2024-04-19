from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)

# database master user:
# admin
# COP4710!

# TODO: change secret key
app.secret_key = 'your_secret_key'



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

        cursor.execute("SELECT * FROM Restaurants ORDER BY trend_counter DESC LIMIT 10")
        top_restaurants = cursor.fetchall()

        connection.close()

        for restaurant in top_restaurants:
            restaurant['price_display'] = restaurant['price']       #remooved the price_to_dollars function since the default price from yelp is in the format we want already

        return render_template('index.html', rows=top_restaurants)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Establish database connection
        connection = mysql.connector.connect(
            host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
            user="admin",
            password="COP4710!",
            database="tally_munch"
        )
        cursor = connection.cursor(dictionary=True)
        
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Query the database for the provided credentials
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()  # Fetch one row from the result

        # Close the database connection
        connection.close()

        if user:
            # If user is found, set session variable to indicate user is logged in
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            # If user is not found, display error message and render login page again
            flash('Username or password incorrect. Please try again.', 'error')

    # If the request method is GET or if user is not found, render the login form
    return render_template('login.html')

@app.route('/createaccount', methods=['GET', 'POST'])
def create_account():
    # Establish database connection
    connection = mysql.connector.connect(
        host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
        user="admin",
        password="COP4710!",
        database="tally_munch"
    )
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        address = request.form['address']
        dietary_restrictions = request.form['dietary_restrictions']

        # Insert the form data into the 'users' table
        insert_query = "INSERT INTO users (username, password, first_name, last_name, address, dietary_restrictions) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (username, password, first_name, last_name, address, dietary_restrictions))
        connection.commit()  # Commit the transaction

        # Set session variable to indicate user is logged in (you might want to adjust this based on your authentication logic)
        session['logged_in'] = True
        
        # Redirect to the index page
        return redirect(url_for('index'))
    
    # If the request method is GET, render the create account form
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

            sql_query = "SELECT * FROM Restaurants WHERE name LIKE %s"
            cursor.execute(sql_query, ('%' + search_query + '%',))
            restaurants = cursor.fetchall()

            connection.close()

            return render_template('search.html', rows=restaurants)
        else:
            return render_template('search.html')
    else:
        return redirect(url_for('login'))

@app.route('/restaurant/<restaurant_id>')
def restaurant_info(restaurant_id):
    connection = mysql.connector.connect(
        host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
        user="admin",
        password="COP4710!",
        database="tally_munch"
    )
    cursor = connection.cursor(dictionary=True)

    # Execute MySQL query to fetch information about the restaurant with the specified ID
    cursor.execute("SELECT * FROM Restaurants WHERE id = %s", (restaurant_id,))
    restaurant_info = cursor.fetchone()




    # Query to select features and amenities for the given restaurant_id
    query = """
            SELECT f.Feature_Name
            FROM RestaurantFeatures AS RF
            INNER JOIN Features_and_Amenities AS f ON RF.FeatureID = f.FeatureID
            WHERE RF.id = %s
        """

    cursor.execute(query, (restaurant_id,))

    # Fetch all the results
    features = cursor.fetchall()

    # Extract the names of features
    feature_names = [feature['Feature_Name'] for feature in features]

    connection.close()

    return render_template('restaurant_info.html', restaurant=restaurant_info, features=feature_names)


if __name__ == "__main__":
    app.run(debug=True)
