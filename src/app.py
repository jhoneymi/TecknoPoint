from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit, namespace, Namespace
from flask_mysqldb import MySQL
from creditcard import CreditCard
import bcrypt
import datetime
import os

#libreria para la factura en PDF
import pdfkit

# Libreria par el tiempo
from datetime import datetime

import random
import string

# Librerias para mandar correos electronicos
import smtplib
from email.message import EmailMessage


app = Flask(__name__)

# solo se declarar variables pero no mi amor
mensage = ""

# Configuración de la clave secreta para sesiones
app.secret_key = 'xyzsdfg'

# SoketIO Confiuracion de una instacia
socketio = SocketIO(app)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'teknopoint_original'
app.config['UPLOAD_FOLDER'] = 'src/static/uploads'

mysql = MySQL(app)

#^ Cierre de Caja
@app.route('/cierre')
def cierre():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills")
    bills = cur.fetchall()

    fechahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    totalingresos = 0
    totalegresos = 0
    totaltarjeta = 0
    totalefectivo = 0
    totaldevoluciones = 0
    observaciones = ""
    arqueocaja = 0

    cur.execute("SELECT * FROM closing_box")
    data = cur.fetchone()

    saldo = data[2]

    if saldo > 0:
        saldoinicial = saldo
    else:
        saldoinicial = 10000

    for bill in bills:
        total_bill = bill[11]
        egresos_bill = bill[6]

        totalegresos += egresos_bill
        totalingresos += total_bill

        methodo = bill[5]

        if methodo == "Tarjeta":
            totaltarjeta += total_bill
        elif methodo == "Efectivo":
            totalefectivo += total_bill
        else:
            flash("Hubo un error")
            
        return render_template('bills.htmls')
    
    cur.execute("INSERT INTO closing_box (fechahora, saldoinicial, totalingresos, totalegresos, totalventasefectivo, totalventastarjeta, totaldevoluciones, arqueocaja, observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (fechahora, saldoinicial, totalingresos, totalegresos, totalefectivo, totaltarjeta, totaldevoluciones, arqueocaja, observaciones))
    mysql.connection.commit()

    cur.execute("DELETE FROM bills")
    mysql.connection.commit()
    cur.close()
    

#~ PDF
@app.route('/generar_pdf')
def generate_pdf():
    # Path al archivo HTML
    html_file = 'src/templates/detalle.html'

    # Nombre del archivo PDF de salida
    pdf_file = 'factura.pdf'

    # Configuración de pdfkit
    options = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': "UTF-8",
        'no-outline': None
    }

    # Ruta al ejecutable de wkhtmltopdf
    wkhtmltopdf_path = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'

    # Convertir HTML a PDF
    pdfkit.from_file(html_file, pdf_file, options=options, configuration=pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path))


#? Pago con Tarjeta
@app.route('/pay', methods=["GET","POST"])
def pay():

    IA()

    # Obtener los datos del formulario
    numero_tarjeta = request.form['numero_tarjeta']
    nombre_titular = request.form['nombre_titular']
    fecha_vencimiento = request.form['fecha_vencimiento']
    cvv = request.form['cvv']
    cliente = request.form['cliente']
    cajero = request.form['cajero']
    total = request.form['total']

    # Obtener los datos del cliente
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM clients WHERE client_id=%s"
    data = (cliente,)
    cursor.execute(query, data)
    result = cursor.fetchone()

    rnc = result[6]
    ubicacion = result[2]
    contacto = result[4]
    customer = result[1]

    # Total
    partes = total.split()
    numero = partes[1]
    total_sin_dolar = numero.strip('$')
    total_general = str(total_sin_dolar)

    # Verificar si el número de tarjeta es válido o no
    tarjeta = CreditCard(numero_tarjeta)

    new_id = CIB()

    if tarjeta:
        fecha_hora = datetime.now()
        fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d")

        number_bill = GNF()

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO bills (id, date, number_bill, customer, discount, way_to_pay, `change`, cashier, rnc_client_bill, ubicacion, contacto, total_general) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (new_id, fecha_hora_formateada, number_bill, customer, "0", "Tarjeta", "0", cajero, rnc, ubicacion, contacto, total_general))
        mysql.connection.commit()
        APB(new_id)

        cur.execute("DELETE FROM articles")
        mysql.connection.commit()
        cur.close()

        flash("La compra se realizó con éxito")
        return redirect(url_for('article'))
    else:
        flash("Hubo un problema con la tarjeta")
        return redirect(url_for('article'))

def APB(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles")

    # Obtener todas las filas de la consulta como una lista de tuplas
    articulos = cur.fetchall()

    for articulo in articulos:
        # Insertar cada campo en la tabla art_bills
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO art_bill (id_bills, decrition, price, itbis, amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (id, articulo[1], articulo[2], articulo[3], articulo[4]))

        # (Optional) Commit the changes to the database
        mysql.connection.commit()

def CIB():
    con = mysql.connection
    cur = con.cursor()
    cur.execute("SELECT MAX(id) FROM bills")

    resultado = cur.fetchone()

    if resultado is None or resultado[0] is None:
        next_bill = 1
    else:
        next_bill = resultado[0] + 1
    cur.close()

    return next_bill
    
def GNF():
    last_number_bill = OUNFD()

    if not last_number_bill:
        new_number_bill = '00001'
    else:
       
        new_number = int(last_number_bill) + 1
        
        new_number_bill = '{:05d}'.format(new_number)

    return new_number_bill


def OUNFD():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT number_bill FROM bills ORDER BY number_bill DESC LIMIT 1")
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            return resultado[0]
        else:
            return None
    except mysql.connector.Error as e:
        print("Error al obtener el último número de factura:", e)
        return None
    
def IA():
    cur = mysql.connection.cursor()

    try:
        cur.execute("SELECT * FROM articles")
        articles = cur.fetchall()

        for article in articles:
            id_articles = article[0]

            cur.execute("SELECT product_amount FROM products WHERE product_id = %s", (id_articles,))
            amount = cur.fetchone()

            cur.execute("UPDATE products SET amount = %s WHERE product_id = %s", (amount, id_articles))

    finally:
        cur.close()

#* Pago con Efectivo
@app.route("/payment", methods=["GET", "POST"])
def payment():
    
    IAE()

    # Obtener los datos del formulario
    cliente = request.form['cliente']
    cajero = request.form['cajero']
    cambio = request.form['cambio']
    total = request.form['total']

    # Obtener los datos del cliente
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM clients WHERE client_id=%s"
    data = (cliente,)
    cursor.execute(query, data)
    result = cursor.fetchone()

    rnc = result[6]
    ubicacion = result[2]
    contacto = result[4]
    customer = result[1]

    # Total
    partes = total.split()
    numero = partes[1]
    total_sin_dolar = numero.strip('$')
    total_general = str(total_sin_dolar)

    new_id = CIBE()

    fecha_hora = datetime.now()
    fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d")

    number_bill = GNFE()

    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO bills (id, date, number_bill, customer, discount, way_to_pay, `change`, cashier, rnc_client_bill, ubicacion, contacto, total_general) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (new_id, fecha_hora_formateada, number_bill, customer, "0", "Efectivo", cambio, cajero, rnc, ubicacion, contacto, total_general))
    mysql.connection.commit()
    APBE(new_id)

    cur.execute("DELETE FROM articles")
    mysql.connection.commit()
    cur.close()

    flash("La compra se realizó con éxito")
    return redirect(url_for('article'))

def APBE(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles")

    # Obtener todas las filas de la consulta como una lista de tuplas
    articulos = cur.fetchall()

    for articulo in articulos:
        # Insertar cada campo en la tabla art_bills
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO art_bill (id_bills, decrition, price, itbis, amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (id, articulo[1], articulo[2], articulo[3], articulo[4]))

        # (Optional) Commit the changes to the database
        mysql.connection.commit()

def CIBE():
    con = mysql.connection
    cur = con.cursor()
    cur.execute("SELECT MAX(id) FROM bills")

    resultado = cur.fetchone()

    if resultado is None or resultado[0] is None:
        next_bill = 1
    else:
        next_bill = resultado[0] + 1
    cur.close()

    return next_bill
    
def GNFE():
    last_number_bill = OUNFDE()

    if not last_number_bill:
        new_number_bill = '00001'
    else:
       
        new_number = int(last_number_bill) + 1
        
        new_number_bill = '{:05d}'.format(new_number)

    return new_number_bill


def OUNFDE():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT number_bill FROM bills ORDER BY number_bill DESC LIMIT 1")
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            return resultado[0]
        else:
            return None
    except mysql.connector.Error as e:
        print("Error al obtener el último número de factura:", e)
        return None
    
def IAE():
    cur = mysql.connection.cursor()

    try:
        cur.execute("SELECT * FROM articles")
        articles = cur.fetchall()

        for article in articles:
            id_articles = article[0]

            cur.execute("SELECT product_amount FROM products WHERE product_id = %s", (id_articles,))
            amount = cur.fetchone()

            cur.execute("UPDATE products SET amount = %s WHERE product_id = %s", (amount, id_articles))

    finally:
        cur.close()


#! Inactive
@app.route('/inactive')
def inactive():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM clients WHERE activity_id = %s", ("2"))
    INCT = cur.fetchall()

    return INCT

#* Active
@app.route('/active/<id>')
def active(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE clients SET activity_id = %s WHERE client_id = %s",(1,id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('inicio'))


#! Search
@app.route('/buscar', methods=['POST'])
def buscar():
    query = request.form['query']
    resultados = buscar_en_bd(query)
    return jsonify(resultados)

def buscar_en_bd(query):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT product_name FROM products WHERE product_name LIKE %s", ('%' + query + '%',))
    resultados = [row[1] for row in cursor.fetchall()]
    cursor.close()
    return resultados

#* Inicio
@app.route('/')
def index():
    return redirect(url_for('login'))

#& Help
@app.route("/help")
def help():
    return render_template('help.html')

#?  Inicio
@app.route('/inicio', methods = ['GET', 'POST'])
def inicio():
    customer = obtener_customer()
    INCT = inactive()
    return render_template('inicio.html', INCT = INCT, CUST = customer)

#*  Admin
@app.route('/admin')
def  admin():
    time = schedule()
    return render_template('admin.html', time = time)

@app.route('/schedule')
def schedule():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM time")
    time = cur.fetchall

    return time

class MyNamespace(Namespace):
    def on_connect(self):
        print('Cliente conectado')

    def on_disconnect(self):
        print('Cliente desconectado')

    def on_get_users(self):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        emit('update_users', users)

socketio.on_namespace(MyNamespace('/my_namespace'))

#* Bills
@app.route('/bills', methods=['GET','POST'])
def bill():
    bills = obtener_bills()
    return render_template('bills.html', bills = bills)

@app.route('/bills_table')
def obtener_bills():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills")
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/factura_detalle/<id>')
def factura_detalle(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
    
    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general)

    return render_template("detalle.html", bill=bill, detail=detail, total_general=total_general_formatted)

#TODO Customers
@app.route('/customers')
def customer():
    clientes = obtener_customer()
    return render_template('customers.html', clientes=clientes)

@app.route('/obtener_customer')
def obtener_customer():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM clients WHERE activity_id = %s",("1"))
    client = cursor.fetchall()
    cursor.close()

    return client

@app.route('/add_customer', methods=['POST', 'GET'])
def add_customer():
    if request.method == 'POST':
        nombre_cliente = request.form['cust_name']
        direccion_cliente = request.form['cust_address']
        telefono_cliente = request.form['cust_phone'] 
        email_cliente = request.form['cust_email']
        rnc = request.form['rnc_client']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO clients (client_name, client_address, client_phone, client_email, activity_id, rnc_client) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre_cliente, direccion_cliente, telefono_cliente, email_cliente, "1", rnc)
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('customer'))
    
@app.route('/deactivate_client/<int:id>')
def deactivate_client(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE clients SET activity_id = %s WHERE client_id = %s",(2,id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('customer'))

@app.route('/edit_customer/<id>')
def edit_customer(id):
        cur = mysql.connection.cursor()
        cur.execute(' SELECT * FROM clients WHERE client_id = %s', (id))
        data = cur.fetchall()
        
        return render_template('edit_customer.html', datos = data[0])

@app.route('/update_customer/<id>', methods=['POST','GET'])
def update_customer(id):
    if request.method == 'POST':
        nombre_cliente = request.form['cust_name']
        direccion_cliente = request.form['cust_address']
        telefono_cliente = request.form['cust_phone'] 
        email_cliente = request.form['cust_email']
        rnc = request.form['rnc_client']

        cur = mysql.connection.cursor()
        cur.execute('UPDATE clients SET client_name = %s, client_address = %s, client_phone = %s, client_email = %s, activity_id = %s, rnc_client = %s WHERE client_id = %s', (nombre_cliente, direccion_cliente, telefono_cliente, email_cliente, '1', rnc, id))
        mysql.connection.commit()
        flash('Contact Updated Successfully')
        return redirect(url_for('customer'))



#* Articles
@app.route('/article')
def article():
    datos = obtener_datos_inv()
    articles = obtener_articles()
    customer = obtener_customer()
    employees = obtener_datos_emp()
    calculo = calculos()
    return render_template('articles.html', datos = datos, articles = articles, calculo = calculo, customer = customer, emp = employees, fullname = session['fullname'])

@app.route('/calculos')
def calculos():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM articles')
    cal = cur.fetchall()

    resultados = []

    total_price = 0
    total_itbis = 0

    for fila in cal:
        art_price = fila[2]
        art_itbis = fila[3]
        art_mount = fila[4]

        subtotal = art_mount * art_price
        
        if art_itbis == art_itbis:
            itbis = art_itbis
        else:
            itbis += art_itbis

        subtotal_itbis = itbis * subtotal / 100

        total_price += subtotal
        total_itbis += subtotal_itbis

    # Calculate total as the sum of subtotal and ITBIS
    total_total = total_price + total_itbis

    # Redondear los valores a dos decimales
    total_price = round(total_price, 2)
    total_itbis = round(total_itbis, 2)
    total_total = round(total_total, 2)

    resultados.append({'subtotal': total_price, 'itbis': total_itbis, 'total': total_total})

    return resultados

@app.route('/obtener_articles')
def obtener_articles():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM articles')
    article = cursor.fetchall()
    cursor.close()
    return article

@app.route('/incluir_art/<id>')
def incluir(id):
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM articles WHERE art_nombre = (SELECT product_name FROM products WHERE product_id = %s)', (id,))
    existing_article = cur.fetchone()

    if existing_article:
        flash('El artículo ya fue añadido.')
    else:
        cur.execute('SELECT * FROM products WHERE product_id = %s', (id,))
        data = cur.fetchall()

        if data:
            art_id = data[0][0]
            art_name  = data[0][1]
            art_price = data[0][2]
            art_itbis = data[0][3]
            art_mount = "1"
            catalogue = data[0][6]

            cur.execute('INSERT INTO articles (id, art_nombre, art_precio, art_itbis, art_cantidad, catalogue) VALUES (%s, %s, %s, %s, %s, %s)', (art_id, art_name, art_price, art_itbis, art_mount, catalogue))
            mysql.connection.commit()

            cur.execute('UPDATE products SET product_amount = product_amount - 1 WHERE product_id = %s', (id,))
            mysql.connection.commit()

        cur.close()
        return redirect(url_for('article'))
    
    return redirect(url_for('article'))


@app.route('/agregar_cantidad_art/<int:id>')
def agregar_cantidad(id):
    try:
        cur = mysql.connection.cursor()

        session['id_product'] = id

        # Obtener la cantidad actual del artículo
        cur.execute('SELECT art_cantidad FROM articles WHERE id = %s', (id,))
        current_quantity = cur.fetchone()[0]

        # Obtener la cantidad límite del producto asociado al artículo
        cur.execute('SELECT amount FROM products WHERE product_id = %s', (id,))
        limit_quantity = cur.fetchone()[0]

        print("Cantidad actual del artículo:", current_quantity)
        print("Cantidad límite del producto:", limit_quantity)

        # Verificar si la cantidad actual supera la cantidad límite
        if current_quantity >= limit_quantity:
            flash('No se puede agregar más cantidad. Límite alcanzado.')
        else:
            # Incrementar la cantidad del artículo
            cur.execute('UPDATE articles SET art_cantidad = art_cantidad + 1 WHERE id = %s', (id,))
            mysql.connection.commit()

            cur.execute('UPDATE products SET product_amount = product_amount - 1 WHERE product_id = %s', (id,))
            mysql.connection.commit()
            flash('Cantidad agregada correctamente.')
    except Exception as e:
        flash('Error al agregar cantidad: {}'.format(str(e)))
    finally:
        cur.close()

    return redirect(url_for('article'))

@app.route('/quitar_cantidad_art/<id>')
def quitar_cantidad(id):
    cur = mysql.connection.cursor()
    
    # Obtener la cantidad actual del producto en la tabla articles
    cur.execute('SELECT art_cantidad FROM articles WHERE id = %s', (id,))
    current_quantity = cur.fetchone()[0]

    # Verificar si la cantidad es mayor que cero antes de restar
    if current_quantity > 1:
        cur.execute('UPDATE products SET product_amount = product_amount + 1 WHERE product_id = %s', (id,))
        mysql.connection.commit()

        # Decrementar la cantidad solo si es mayor que cero
        cur.execute('UPDATE articles SET art_cantidad = art_cantidad - 1 WHERE id = %s', (id,))
        mysql.connection.commit()
    else:
        flash('La cantidad no puede ser menor que cero.')

    cur.close()
    return redirect(url_for('article'))

@app.route('/remove_article/<string:id>')
def remove_article(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM articles WHERE id = {0}'.format(id))
    mysql.connection.commit()

    cur.execute('UPDATE products SET product_amount = product_amount + 1 WHERE product_id = %s', (id,))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('article'))

#!  Inventario
@app.route('/inventario')
def inventario():
    datos = obtener_datos_inv()
    return render_template('inventario.html', datos=datos)

@app.route('/obtener_datos_inv')
def  obtener_datos_inv():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM products')
    data = cursor.fetchall()
    cursor.close()
    return data

@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        art_name = request.form['art_name']
        art_price = request.form['art_precio']
        art_itbis = request.form['art_itbis']
        art_cant = request.form['art_cantidad']
        art_catalogo = request.form['catalogo']
        art_img = request.files['image']

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM products WHERE product_name = %s", (art_name,))
        existing_article = cur.fetchone()

        if existing_article:
            flash('El artículo ya existe en la base de datos', 'error')
            return redirect(url_for('inventario'))
        
        if art_img.filename != '':
            art_img.save(os.path.join(app.config['UPLOAD_FOLDER'], art_img.filename))


        cur.execute("INSERT INTO products (product_name, product_price, product_itbis, product_amount, amount, product_catalogue, image) VALUES (%s,%s,%s,%s,%s,%s,%s)", (art_name, art_price, art_itbis, art_cant, art_cant, art_catalogo,art_img.filename))
        mysql.connection.commit()
        cur.close()
        
    return redirect(url_for('inventario'))

@app.route('/remove_art/<string:id>')
def remove_art(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM products WHERE product_id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('inventario'))

@app.route('/edit/<id>')
def get_art(id):
        cur = mysql.connection.cursor()
        cur.execute(' SELECT * FROM products WHERE product_id = %s', (id))
        data = cur.fetchall()
        return render_template('edit.html',datos = data[0])

@app.route('/update/<id>', methods = ['POST', 'GET'])
def update(id):

    if request.method == 'POST':

        art_name = request.form['art_name']
        art_price = request.form['art_precio']
        art_itbis = request.form['art_itbis']
        art_cant = request.form['art_cantidad']
        art_catalogo = request.form['catalogo']
        art_imagen = request.files['image']

        if art_imagen.filename != '':
            art_imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], art_imagen.filename))


        cur = mysql.connection.cursor()
        cur.execute('UPDATE products SET product_name = %s, product_price = %s, product_itbis = %s, product_amount = %s, amount = product_amount, product_catalogue = %s, image = %s WHERE product_id = %s', (art_name, art_price, art_itbis, art_cant, art_catalogo,art_imagen.filename,id))
        mysql.connection.commit()
        flash('Contact Updated Successfully')
        return redirect(url_for('inventario'))


#TODO  Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND username = %s", (email, username))
        user = cur.fetchone()

        if user:

            # Successful login, store information in the session
            session['id'] = user[0]
            session['email'] = email
            session['username'] = username
            session['fullname'] = user[1]
            flash('Successful login', 'success')
            session['logged in'] = True
            session['role_id'] = user[5]

            session_id = str(session['id'])
            fecha_hora = datetime.now()
            fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S.%f")

            cur.execute("UPDATE users SET state = TRUE WHERE user_id = %s", (user[0],))
            mysql.connection.commit()

            socketio.emit('get_users', namespace='/my_namespace')

            # Verify the password using bcrypt
            stored_password = user[4].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):

                if session['role_id'] == 1:

                    cur = mysql.connection.cursor()
                    cur.execute('SELECT * FROM time WHERE id_users = %s',(session_id))
                    duplicate = cur.fetchall()

                    if duplicate:
                        cur = mysql.connection.cursor()
                        cur.execute('UPDATE time SET entry_date = %s WHERE id_users = %s',(fecha_hora_formateada,session_id))
                        mysql.connection.commit()
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute('INSERT INTO time (id_users, entry_date) VALUES (%s, %s)',(session_id, fecha_hora_formateada))
                        mysql.connection.commit()

                    return redirect(url_for('admin'))
                elif session['role_id'] == 2:
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT * FROM time WHERE id_users = %s',(session_id))
                    duplicate = cur.fetchall()

                    if duplicate:
                        cur = mysql.connection.cursor()
                        cur.execute('UPDATE time SET entry_date = %s WHERE id_users = %s',(fecha_hora_formateada,session_id))
                        mysql.connection.commit()
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute('INSERT INTO time (id_users, entry_date) VALUES (%s, %s)',(session_id, fecha_hora_formateada))
                        mysql.connection.commit()
                    # # Enviar correo electronico cuando se logue e usuario
                    # correo_remitente = "tecknopoint1@gmail.com"
                    # contrasena_remitente = "mrvw gpsb whcr tjjx"
                    # servidor_smtp = "smtp.gmail.com"
                    # puerto_smtp = 587

                    # correo_destinatario = email
                    # asunto="Bienvenido a Teckno Point"
                    # mensaje="Te has logueado con exito en nuestro punto de venta."

                    # email = EmailMessage()
                    # email["From"] = correo_remitente
                    # email["To"] = correo_destinatario
                    # email["Subject"] = asunto
                    # email.set_content(mensaje)

                    # with smtplib.SMTP(servidor_smtp, puerto_smtp) as smtp:
                    #     smtp.starttls()
                    #     smtp.login(correo_remitente, contrasena_remitente)

                    #     smtp.send_message(email)
                    return redirect(url_for('inicio'))
                elif session['role_id'] == 3:
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT * FROM time WHERE id_users = %s',(session['id']))
                    duplicate = cur.fetchall()

                    if duplicate:
                        cur = mysql.connection.cursor()
                        cur.execute('UPDATE time SET entry_date = %s WHERE id_users = %s',(fecha_hora_formateada,session['id']))
                        mysql.connection.commit()
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute('INSERT INTO time (id_users, entry_date) VALUES (%s, %s)',(session['id'], fecha_hora_formateada))
                        mysql.connection.commit()
                    return redirect(url_for('inicio_emp'))
                else:
                    return redirect(url_for('login'))
            else:
                flash('Username or password incorrect', 'error')
                return redirect(url_for('login'))
        else:
            flash('Username or password incorrect', 'error')
            return redirect(url_for('login'))
        
    return render_template('login.html')

#~ Registro
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        user = request.form['user']
        password = request.form['password']

        pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd, salt)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (fullname, email, username, password, role_id) VALUES (%s, %s, %s, %s, %s)",(fullname, email, user, hashed_password.decode('utf-8'), "2"))
        mysql.connection.commit()
        cur.close()

        # Successful registration, store information in the session
        session['user'] = user
        flash('Successful registration', 'success')
        return redirect(url_for('login'))
    return render_template('login')

#^ Perfil
@app.route('/perfil')
def  perfil():
    if 'email' in session:
        return render_template('profile.html', username=session['username'], emailuser=session['email'])
    else:
        return redirect(url_for('login'))

#& Logout
@app.route('/logout')
def logout():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    user = cur.fetchone()

    cur.execute("UPDATE users SET state = FALSE WHERE user_id = %s", (user[0],))
    mysql.connection.commit()

    socketio.emit('get_users', namespace='/my_namespace')

    fecha_hora = datetime.now()
    fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S.%f")

    cur = mysql.connection.cursor()
    cur.execute('UPDATE time SET departure_date = %s WHERE id_users = %s',(fecha_hora_formateada,session['id']))
    mysql.connection.commit()

    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

#?  Proveedores
@app.route('/proveedor')
def proveedor():
    prov = obtener_datos_prov()
    return render_template('proveedores.html', prov=prov)

@app.route('/obtener_datos_prov')
def  obtener_datos_prov():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM suppliers")
    prov = cursor.fetchall()
    cursor.close()
    return prov

@app.route('/remove_prov/<string:id>')
def remove_prov(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM suppliers WHERE supplier_id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('proveedor'))

@app.route('/edit_prov/<id>')
def get_prov(id):
        cur = mysql.connection.cursor()
        cur.execute(' SELECT * FROM suppliers WHERE supplier_id = %s', (id))
        data = cur.fetchall()
        return render_template('edit_prov.html',datos = data[0])

@app.route('/update_prov/<id>', methods = ['POST', 'GET'])
def update_prov(id):

    if request.method == 'POST':

        prov_name = request.form['prov_name']
        prov_address = request.form['prov_address']
        prov_phone = request.form['prov_phone']
        prov_email = request.form['prov_email']

        cur = mysql.connection.cursor()
        cur.execute(' UPDATE suppliers SET supplier_name = %s, supplier_address = %s, supplier_phone = %s, supplier_email = %s WHERE supplier_id = %s', (prov_name, prov_address, prov_phone, prov_email,id))
        mysql.connection.commit()
        flash('Contact Updated Successfully')
        return redirect(url_for('proveedor'))


@app.route('/add_prov', methods=['GET', 'POST'])
def  add_prov():  
        if request.method == 'POST':
            prov_name = request.form['prov_name']
            prov_address = request.form['prov_address']
            prov_phone = request.form['prov_phone']
            prov_email = request.form['prov_email']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO suppliers (supplier_name, supplier_address, supplier_phone, supplier_email) VALUES (%s,%s,%s,%s)", (prov_name, prov_address, prov_phone, prov_email))
            mysql.connection.commit()
            cur.close()

        return redirect(url_for('proveedor'))

#! Empleados

@app.route('/inicio_emp')
def inicio_emp():
    return render_template('/inicio_emp.html')

@app.route('/empleados')
def empleados():
    empleados = obtener_datos_emp()
    return render_template('/empleados.html', empleados=empleados)

@app.route('/obtener_datos_emp')
def  obtener_datos_emp():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE role_id = %s",('3'))
    data = cursor.fetchall()
    cursor.close()
    return data

@app.route('/add_emp', methods=['GET', 'POST'])
def add_emp():
    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        user = request.form['user']
        password = request.form['password']

        pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd, salt)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (fullname, email, username, password, role_id) VALUES (%s,%s,%s,%s,%s)", (fullname,email,user,hashed_password,'3'))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('empleados'))
    
@app.route('/remove_emp/<string:id>')
def remove_emp(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM users WHERE user_id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('empleados'))

@app.route('/edit_emp/<id>')
def get_emp(id):
        cur = mysql.connection.cursor()
        cur.execute(' SELECT * FROM users WHERE user_id = %s', (id))
        data = cur.fetchall()
        return render_template('edit_emp.html',datos = data[0])

@app.route('/update_emp/<id>', methods = ['POST', 'GET'])
def update_emp(id):

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        user = request.form['user']
        password = request.form['password']

        pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd, salt)

        cur = mysql.connection.cursor()
        cur.execute(' UPDATE users SET fullname = %s, email = %s, username = %s, password = %s WHERE user_id = %s', (fullname, email, user, hashed_password,id))
        mysql.connection.commit()
        flash('Contact Updated Successfully')
        return redirect(url_for('empleados'))
    
@app.route('/search_emp', methods = ['POST', 'GET'])
def  search_employee():

    if request.form == 'POST':
        query = request.form['fullname']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE fullname = %s AND role_id = %s",(query,'3'))
        data = cursor.fetchall()
        cursor.close()

        empleados = data
    return render_template('/empleados.html', empleados = empleados)




if __name__ == '__main__':
    app.run(debug=True)