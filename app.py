from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)

# database master user:
# admin
# COP4710!

# TODO: change secret key
app.secret_key = 'your_secret_key'

currUser = ""

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

        cursor.execute("SELECT Food_category FROM Food_Option")
        data = [item['Food_category'] for item in cursor.fetchall()]
        
        connection.close()

        for restaurant in top_restaurants:
            restaurant['price_display'] = restaurant['price']       #remooved the price_to_dollars function since the default price from yelp is in the format we want already

        return render_template('index.html', rows=top_restaurants, data=data)
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
            session['username'] = username
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

    cursor.execute("SELECT Food_category FROM Food_Option")
    data = [item['Food_category'] for item in cursor.fetchall()]
    
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        address = request.form['address']
        favorite_cuisine = request.form['favorite_cuisine']

        # Insert the form data into the 'users' table
        insert_query = "INSERT INTO users (username, password, first_name, last_name, address, favorite_cuisine) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (username, password, first_name, last_name, address, favorite_cuisine))
        connection.commit()  # Commit the transaction

        # Set session variable to indicate user is logged in (you might want to adjust this based on your authentication logic)
        session['logged_in'] = True
        session['username'] = username
        
        # Redirect to the index page
        return redirect(url_for('index'))
    
    # If the request method is GET, render the create account form
    return render_template('createaccount.html', data=data)



@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    connection = mysql.connector.connect(
        host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
        user="admin",
        password="COP4710!",
        database="tally_munch"
    )
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT Food_category FROM Food_Option")
    data = [item['Food_category'] for item in cursor.fetchall()]


    if 'save_settings' in request.form:
        password = request.form['password']
        favorite_cuisine = request.form['favorite_cuisine']
        username = session['username']
        
        # Query to check if the provided password matches the user's password
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data and user_data['password'] == password:
            # If the password matches, update the favorite cuisine in the database
            update_query = "UPDATE users SET favorite_cuisine = %s WHERE username = %s"
            cursor.execute(update_query, (favorite_cuisine, username))
            connection.commit()  # Commit the transaction
            flash('Settings updated successfully!', 'success')
        else:
            flash('Incorrect password. Please try again.', 'error')

    elif 'delete_account' in request.form:
        delete_text = request.form['delete']
        username = session['username']
        
        # Extracting the username from the delete text
        delete_username = delete_text.split("DELETE ")[-1]

        # Checking if the delete text matches the expected format
        if delete_username == username:
            # Delete the user from the users table
            delete_query = "DELETE FROM users WHERE username = %s"
            cursor.execute(delete_query, (username,))
            connection.commit()  # Commit the transaction
            flash('Account deleted successfully!', 'success')
            # Redirect to the login page or any other appropriate page
            return redirect(url_for('login'))
        else:
            flash('Incorrect delete text. Please enter the correct delete text.', 'error')

    return render_template('settings.html', data=data)

@app.route('/search', methods=['POST', 'GET'])
def search():
    if 'logged_in' in session:
        if request.method == 'POST':
            
            if 'restaurant' in request.form:
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

                sql_query = "SELECT COUNT(*) AS total_restaurants FROM Restaurants WHERE name LIKE %s"
                cursor.execute(sql_query, ('%' + search_query + '%',))
                aggregated_result = cursor.fetchone()
                total_restaurants = aggregated_result['total_restaurants']

                connection.close()

                return render_template('search.html', rows=restaurants, count=total_restaurants)
            
            elif 'food' in request.form:
                search_query = request.form['food']

                connection = mysql.connector.connect(
                    host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
                    user="admin",
                    password="COP4710!",
                    database="tally_munch"
                )   
                cursor = connection.cursor(dictionary=True)

                sql_query = """
                    SELECT * 
                    FROM Restaurants 
                    WHERE id IN (
                        SELECT id 
                        FROM RestaurantsFoodOptions 
                        WHERE FoodOptionID IN (
                            SELECT FoodOptionID 
                            FROM Food_Option 
                            WHERE Food_Category LIKE %s
                        )
                    )
                """
                cursor.execute(sql_query, ('%' + search_query + '%',))
                restaurants = cursor.fetchall()

                connection.close()

                return render_template('search.html', rows=restaurants)
            
            elif 'searchByPreference' in request.form:
                # Search by favorite cuisine
                # Get the username from the session
                username = session.get('username')

                # Establish database connection
                connection = mysql.connector.connect(
                    host="cop4710-tallymunch.c3gw2k8i8nc0.us-east-1.rds.amazonaws.com",
                    user="admin",
                    password="COP4710!",
                    database="tally_munch"
                )
                cursor = connection.cursor(dictionary=True)

                # Query to get the favorite cuisine of the user
                cursor.execute("SELECT favorite_cuisine FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()

                if user_data:
                    favorite_cuisine = user_data['favorite_cuisine']

                    # Query to search for restaurants by favorite cuisine
                    sql_query = """
                        SELECT * 
                        FROM Restaurants 
                        WHERE id IN (
                            SELECT id 
                            FROM RestaurantsFoodOptions 
                            WHERE FoodOptionID IN (
                                SELECT FoodOptionID 
                                FROM Food_Option 
                                WHERE Food_Category LIKE %s
                            )
                        )
                    """
                    cursor.execute(sql_query, ('%' + favorite_cuisine + '%',))
                    restaurants = cursor.fetchall()

                    connection.close()

                    return render_template('search.html', rows=restaurants)
        
        # Default return statement if no conditions are met
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

    # Increment trend_counter for the clicked restaurant
    update_query = "UPDATE Restaurants SET trend_counter = trend_counter + 1 WHERE id = %s"
    cursor.execute(update_query, (restaurant_id,))
    connection.commit()

    connection.close()

    return render_template('restaurant_info.html', restaurant=restaurant_info, features=feature_names)


def changeCurrUser(x):
    global currUser
    currUser = x

if __name__ == "__main__":
    app.run(debug=True)
