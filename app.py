from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

# TODO: change secret key
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('index.html')
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
        return render_template('search.html')
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
