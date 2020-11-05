from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskcrud'
mysql = MySQL(app)

app.secret_key = 'mysecretkey'


@app.route('/')
def main():
    if 'name' in session:
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/index')
def Index():
    if 'name' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM contacts')
        data = cur.fetchall()
        return render_template('index.html', contacts = data)
    else:
        return render_template('login.html')


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cur.fetchone()
        cur.close()

        if user:
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['loggedin'] = True
                session['id'] = user['id']
                session['name'] = user['name']
                session['email'] = user['email']
                cur = mysql.connection.cursor()
                cur.execute('SELECT * FROM contacts')
                data = cur.fetchall()
                return redirect(url_for('Index', contact = data))
            else:
                 flash('El usuario y/o la contraseña son incorrectos', 'altert-danger')
                 return render_template('login.html')
        else:
             flash('El usuario y/o la contraseña son incorrectos', 'altert-danger')
             return render_template('login.html')
    else:
        flash('Inicie sesión para poder ingresar', 'altert-danger')
        return render_template('login.html')


@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (name, email, password) VALUES(%s, %s, %s)',(name,email,hash_password,))
        mysql.connection.commit()
        flash('Usuario registrado correctamente, inicie sesión')
        session['name'] = name
        session['email'] = email
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')


@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        correo = request.form['correo']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO contacts (fullname, phone, email) VALUES(%s, %s, %s)',
        (fullname, phone, correo))
        mysql.connection.commit()
        flash('Contacto agregado correctamente')
        return redirect(url_for('Index'))


@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('edit-contact.html', contact = data[0])


@app.route('/update/<id>', methods = ['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        correo = request.form['correo']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE contacts
        SET fullname = %s,
          email = %s,
          phone = %s
        WHERE id = %s
        """, (fullname, correo, phone, id))
        mysql.connection.commit()
        flash('Contacto actualizado correctamente')
        return redirect(url_for('Index'))


@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contacto eliminado correctamente')
    return redirect(url_for('Index'))


if __name__ == '__main__':
    app.run(port = 3000, debug = True)
