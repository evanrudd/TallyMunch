# TallyMunch
A flask application for Florida State Students to find restaurants in Tallahassee.

## How to Run Development Server
Ensure in "app.py":
```
if __name__ == "__main__":
  app.run(debug=True)
```
Install mySQL import:
```
pip install mysql-connector-python
```
Then in the terminal in the root directory run:
```
python3 app.py
```
A development server will then be visible at http://127.0.0.1:5000
