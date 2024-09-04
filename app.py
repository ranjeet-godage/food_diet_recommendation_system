from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

# MySQL configuration
db_config = {
    'user': 'root',
    'password': 'root',  # Update with your MySQL password
    'host': 'localhost',
    'database': 'diet_recommendation'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Do not hash password

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {e}")
        finally:
            cursor.close()
            conn.close()

    return render_template('create_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        stored_password = cursor.fetchone()
        cursor.close()
        conn.close()

        if stored_password and stored_password[0] == password:  # Compare unhashed password
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            flash("Invalid username or password")

    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET age = %s, height = %s, weight = %s WHERE username = %s",
                       (age, height, weight, session['username']))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Profile updated successfully')
        return redirect(url_for('welcome'))

    return render_template('profile.html')

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch user profile information
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT age, height, weight FROM users WHERE username = %s", (session['username'],))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_data:
        age, height, weight = user_data
        # Convert height from cm to meters
        height_m = height / 100.0
        # Calculate BMI
        bmi = weight / (height_m ** 2)
        bmi = round(bmi, 2)
    else:
        bmi = None

    return render_template('welcome.html', username=session['username'], bmi=bmi)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
