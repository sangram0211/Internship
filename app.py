
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sangram@0210",
    database="battery_db"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM battery")
    batteries = cursor.fetchall()
    return render_template('dashboard.html', batteries=batteries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cursor.fetchone()
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin'] = admin['username']
            return redirect(url_for('home'))
        else:
            return "Login failed. Try again."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        serial = request.form['serial']
        btype = request.form['type']
        status = request.form['status']
        cursor.execute("INSERT INTO battery (serial_number, type, status) VALUES (%s, %s, %s)",
                       (serial, btype, status))
        db.commit()
        return redirect(url_for('home'))
    return render_template('add_battery.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        status = request.form['status']
        cursor.execute("UPDATE battery SET status=%s WHERE id=%s", (status, id))
        db.commit()
        return redirect(url_for('home'))
    cursor.execute("SELECT * FROM battery WHERE id=%s", (id,))
    battery = cursor.fetchone()
    return render_template('edit_battery.html', battery=battery)

@app.route('/delete/<int:id>')
def delete(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    cursor.execute("DELETE FROM battery WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('home'))

@app.route('/report')
def report():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT status, COUNT(*) as count FROM battery GROUP BY status")
    report = cursor.fetchall()
    return render_template('report.html', report=report)

if __name__ == '__main__':
    app.run(debug=True)
