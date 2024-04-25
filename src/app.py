from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flask_socketio import SocketIO, emit, namespace, Namespace
from flask_mysqldb import MySQL

# from creditcard import CreditCard
import bcrypt
import datetime
import os
import threading
import io

#libreria para la factura en PDF
import pdfkit

# Librerias para el tiempo
from datetime import datetime, timedelta
import time

# Librerias Random
import random
import string

# Librerias para mandar correos electronicos
import smtplib
from email.message import EmailMessage


app = Flask(__name__)

# Ruta al ejecutable de wkhtmltopdf
wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

# Ruta para crear el pdf que se va a enviar
pdf_output_folder = r'C:\Users\slime\Desktop\TecnoPoint 2\src\pdfs'

# Configura pdfkit para usar la ruta del ejecutable
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# solo se declarar variables pero no mi amor
mensage = ""

# Configuración de la clave secreta para sesiones
def aleatoria(longitud):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    cadena_aleatoria = ''.join(random.choice(caracteres) for _ in range(longitud))
    return cadena_aleatoria

cadena = aleatoria(10)

app.secret_key = cadena

# SoketIO Confiuracion de una instacia
socketio = SocketIO(app)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'teknopoint_original'
app.config['UPLOAD_FOLDER'] = 'src/static/uploads'

mysql = MySQL(app)

# Loader
@app.route('/loader')
def loader():
    return render_template('loader.html')

def intermedio():
    contador()

def contador():

    contar = 0

    while True:

        contar += 1
        print(contar)

        if contar >= 6000000:
            return redirect(url_for('login'))

# Manejador de error para URL no encontrada (404)
@app.errorhandler(404)
def page_not_found(error):
    previous_page = request.referrer
    if previous_page is None:
        return redirect(url_for('index'))
    return redirect(previous_page)

#~ enviar facturas
def enviar(id):
    pdf_output_path = os.path.join(pdf_output_folder, 'factura.pdf')
    if os.path.exists(pdf_output_path):
        os.remove(pdf_output_path)

    id_factura = str(id)
    session['id_factura_enviada'] = int(id_factura)

    # Renderiza el contenido HTML
    url = 'http://127.0.0.1:5000/factura_detalle/' + id_factura

    # Genera el PDF desde el HTML
    pdf = pdfkit.from_url(url, False, configuration=config)

    # Guarda el PDF como archivo en la carpeta especificada
    with open(pdf_output_path, 'wb') as f:
        f.write(pdf)

    enviar_e()

    # Devuelve una respuesta con la ubicación del archivo PDF generado
    return f'PDF generado y guardado en: {pdf_output_path}'

# @app.route('/enviar_WhatsApp')
# def enviar_w():

@app.route('/enviar_Email')
def enviar_e():

    pdf_output_path = os.path.join(pdf_output_folder, 'factura.pdf')
    pdf_path = pdf_output_path

    # Configuración del correo electrónico
    correo_remitente = "tecknopoint1@gmail.com"
    contrasena_remitente = "mrvw gpsb whcr tjjx"
    correo_destinatario = "slimerbatista27@gmail.com"
    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587

    # Crear mensaje de correo electrónico
    email = EmailMessage()
    email["From"] = correo_remitente
    email["To"] = correo_destinatario
    email["Subject"] = "Factura adjunta"
    email.set_content("Adjunto encontrarás la factura")

    # Adjuntar el archivo PDF
    with open(pdf_path, "rb") as attachment:
        contenido_pdf = attachment.read()
    email.add_attachment(contenido_pdf, maintype="application", subtype="octet-stream", filename=os.path.basename(pdf_path))

    # Enviar correo electrónico
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as smtp:
        smtp.starttls()
        smtp.login(correo_remitente, contrasena_remitente)
        smtp.send_message(email)

    # Send Customer

    id_factura = session['id_factura_enviada']

    cur = mysql.connection.cursor()
    cur.execute("SELECT customer FROM bills WHERE id = %s", (id_factura,))
    customer = cur.fetchone()

    cur.execute("SELECT client_email FROM clients WHERE client_name = %s", (customer,))
    email_client = cur.fetchone()[0] 

    correo_remitente = "tecknopoint1@gmail.com"
    contrasena_remitente = "mrvw gpsb whcr tjjx"
    correo_destinatario = email_client
    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587

    email = EmailMessage()
    email["From"] = correo_remitente
    email["To"] = correo_destinatario
    email["Subject"] = "Factura adjunta"
    email.set_content("Adjunto encontrarás la factura")

    with open(pdf_path, "rb") as attachment:
        contenido_pdf = attachment.read()
    email.add_attachment(contenido_pdf, maintype="application", subtype="octet-stream", filename=os.path.basename(pdf_path))

    with smtplib.SMTP(servidor_smtp, puerto_smtp) as smtp:
        smtp.starttls()
        smtp.login(correo_remitente, contrasena_remitente)
        smtp.send_message(email)


    return redirect(url_for('article'))

#^ Cierre de Caja
@app.route('/closing')
def closing():
    if session['logged in'] == True and session['role_id'] == 2:
        closes = obtener_closing()
        return render_template('closing.html', close = closes)
    else:
        return redirect(url_for('login'))

def obtener_closing():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM closing_box')
    closings = cur.fetchall()

    return closings

@app.route('/cierre', methods = ['POST','GET'])
def cierre():
    id_C = CIBC()
        
    fullname = session['fullname']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s",('1'))
    bills = cur.fetchall()

    observaciones = request.form['observacion']

    fechahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    totalingresos = 0
    totalegresos = 0
    totaltarjeta = 0
    totalefectivo = 0
    totaldevoluciones = 0
    arqueocaja = 0
    cajero = fullname

    cur.execute("SELECT * FROM closing_box ORDER BY fechahora DESC LIMIT 1")
    last_insertion = cur.fetchone()

    if last_insertion:
        saldo = last_insertion[8]
        if saldo is not None and saldo > 0:
            saldoinicial = saldo
        else:
            saldoinicial = 1000
    else:
        saldoinicial = 1000

    for bill in bills:
        total_bill = bill[12]
        egresos_bill = bill[7]

        totalegresos += egresos_bill
        totalingresos += total_bill

        methodo = bill[5]

        if methodo == "Tarjeta":
            totaltarjeta += total_bill
        elif methodo == "Efectivo":
            totalefectivo += total_bill
        else:
            flash("Hubo un error")

        saldo_final = saldoinicial + totalingresos - totalegresos
        
        arqueocaja = saldo_final - saldoinicial
                
        
        cur.execute("INSERT INTO closing_box (id_closing, fechahora, saldoinicial, totalingresos, totalegresos, totalventasefectivo, totalventastarjeta, totaldevoluciones, arqueocaja, observaciones, cajero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (id_C, fechahora, saldoinicial, totalingresos, totalegresos, totalefectivo, totaltarjeta, totaldevoluciones, arqueocaja, observaciones, cajero))
        mysql.connection.commit()
        cur.close

        cur.execute("UPDATE bills SET estado = %s",('2'))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('bill'))

@app.route('/detalle_c/<id>')
def detalle_c(id):

    session['id_c'] = id

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM closing_box WHERE id_closing = %s",(id))
    detalle = cur.fetchall()

    balance_json()

    return render_template('detalle_c.html', detalle = detalle)

@app.route('/CierreBalance_json')
def balance_json():

    id_Cierre = session['id_c']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM closing_box WHERE id_closing = %s",(id_Cierre))
    detalle = cur.fetchall()

    # Obtener los datos del Cierre
    for fila in detalle:
        saldo_inicial = fila[2]
        total_ingresos = fila[3]
        total_egresos = fila[4]
        pagos_tarjeta = fila[6]
        pagos_efectivo = fila[5]
        arqueo_caja = fila[8]

    # Crear un diccionario con los datos para el gráfico
    data = {
        'saldo_incial': saldo_inicial,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'total_tarjeta': pagos_tarjeta,
        'total_efectivo': pagos_efectivo,
        'arqueo_caja': arqueo_caja 

    }

    # Devolver los datos como JSON
    return jsonify(data)

def CIBC():
    con = mysql.connection
    cur = con.cursor()
    cur.execute("SELECT MAX(id_closing) FROM closing_box")

    resultado = cur.fetchone()

    if resultado is None or resultado[0] is None:
        next_bill = 1
    else:
        next_bill = resultado[0] + 1
    cur.close()

    return next_bill


@app.route('/factura/<id>')
def factura(id):
    
    session['id_factura'] = id

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis
    
    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("factura.html", bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)

#~ PDF
@app.route('/descargar_pdf')
def descargar_pdf():

    id_factura = session['id_factura']

    # URL del contenido a convertir en PDF
    url = 'http://127.0.0.1:5000/factura/' + id_factura
    
    # Genera el PDF desde la URL
    pdf = pdfkit.from_url(url, False, configuration=config)

    id_factura_int = int(id_factura)
    
    if id_factura_int >= 10:
        # Crea una respuesta para descargar el PDF
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=factura N. 000' + id_factura + '.pdf'
    elif id_factura_int > 99:
        # Crea una respuesta para descargar el PDF
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=factura N. 00' + id_factura + '.pdf'
    else:
        # Crea una respuesta para descargar el PDF
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=factura N. 0000' + id_factura + '.pdf'

    return response

@app.route('/descargar_cotizacion_pdf')
def descargar_cotizacion_pdf():

    id_cotizacion = session['id_cotizacion']

    # URL del contenido a convertir en PDF
    url = 'http://127.0.0.1:5000/cotizacion_p/' + id_cotizacion
    
    # Genera el PDF desde la URL
    pdf = pdfkit.from_url(url, False, configuration=config)

    id_cotizacion_int = int(id_cotizacion)
    
    if id_cotizacion_int >= 10:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=cotizacion N. 000' + id_cotizacion + '.pdf'
    elif id_cotizacion_int > 99:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=cotizacion N. 00' + id_cotizacion + '.pdf'
    else:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=cotizacion N. 0000' + id_cotizacion + '.pdf'

    return response


#? Pago con Tarjeta
@app.route('/pay', methods=["GET","POST"])
def pay():

    IA()

    # Obtener los datos del formulario
    numero_tarjeta = request.form['numero_tarjeta']
    nombre_titular = request.form['nombre_titular']
    fecha_vencimiento = request.form['fecha_vencimiento']
    cvv = request.form['cvv']
    discount = request.form['discount']
    ex_itbis = request.form['ex-itbis']
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
    # tarjeta = CreditCard(numero_tarjeta)
    tarjeta = numero_tarjeta

    new_id = CIB()

    if tarjeta:
        fecha_hora = datetime.now()
        fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

        number_bill = GNF()

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO bills (id, date, number_bill, customer, discount, way_to_pay, paid,`change`, cashier, rnc_client_bill, ubicacion, contacto, total_general, estado, Itbisextra) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (new_id, fecha_hora_formateada, number_bill, customer, discount, "Tarjeta", "0", "0", cajero, rnc, ubicacion, contacto, total_general, 1, ex_itbis))
        mysql.connection.commit()
        APB(new_id)

        enviar(new_id)

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
    monto = request.form['monto']
    total = request.form['total']
    discount = request.form['discount']
    ex_itbis = request.form['ex-itbis']

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

    total_float = float(total_general)
    monto_float = float(monto)

    cambio = monto_float - total_float

    new_id = CIBE()

    fecha_hora = datetime.now()
    fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

    number_bill = GNFE()

    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO bills (id, date, number_bill, customer, discount, way_to_pay, paid, `change`, cashier, rnc_client_bill, ubicacion, contacto, total_general, estado, Itbisextra) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (new_id, fecha_hora_formateada, number_bill, customer, discount, "Efectivo", monto_float, cambio, cajero, rnc, ubicacion, contacto, total_general, 1, ex_itbis))
    mysql.connection.commit()
    APBE(new_id)

    enviar(new_id)

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

    return redirect(url_for('customer'))


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
    return redirect(url_for('loader'))

#& Help
@app.route("/help")
def help():
    return render_template('help.html')

#?  Inicio
@app.route('/inicio', methods = ['GET', 'POST'])
def inicio():
    if session['logged in'] == True and session['role_id'] == 2:
        customer = obtener_customer()
        INCT = inactive()
        return render_template('inicio.html', INCT = INCT, CUST = customer)
    else:
        return redirect(url_for('login'))

#*  Admin
@app.route('/admin', methods = ['GET','POST'])
def  admin():
    if session['logged in'] == True and session['role_id'] == 1:
        users = obtener_Users()
        time = obtener_tiempo()
        return render_template('admin.html', time = time, users = users)
    else:
        return redirect(url_for('login'))

def obtener_Users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    return users

def obtener_tiempo():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM time")
    time = cur.fetchall()

    return time

#! History
@app.route('/history', methods=['GET','POST'])
def history():
    if session['logged in'] == True:
        historys = obtener_historys()
        total = 0

        for fila in historys:

            total += fila[12]

        return render_template('history.html', history = historys, total = total)
    else:
        return redirect(url_for('login'))

def obtener_historys():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s ORDER BY date DESC, id DESC ",("2"))
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/filtrar', methods=['POST', 'GET'])
def filtro():
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        if fecha_inicio is None and fecha_fin is None:
            selecion = request.form['seleccion']
            fecha_inicio = 0
            fecha_fin = 0

            if selecion == "diario":
                # Obtener el rango de fechas para el día actual
                fecha_inicio = datetime.now().strftime("%d-%m-%Y")
                fecha_fin = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
            elif selecion == "semanal":
                # Obtener el rango de fechas para la semana actual
                fecha_actual = datetime.now()
                fecha_sem = fecha_actual - timedelta(days=fecha_actual.weekday())
                fecha_inicio = fecha_sem.strftime("%d-%m-%Y")
                fecha_fin = (fecha_sem + timedelta(days=6)).strftime("%d-%m-%Y")
            elif selecion == "trimestral":
                # Obtener el rango de fechas para el trimestre actual
                fecha_inicio = datetime.now()
                trimestre_actual = (fecha_inicio.month - 1) // 3 + 1
                fecha_trimestre = datetime(fecha_inicio.year, 3 * trimestre_actual - 2, 1)
                fecha_inicio = fecha_trimestre.strftime("%d-%m-%Y")
                fecha_fin = fecha_inicio  # Fin del trimestre es el mismo que el inicio
            elif selecion == "anual":
                # Obtener el rango de fechas para el año actual
                fecha_inicio = datetime.now().strftime("01-01-%Y")
                fecha_fin = datetime.now().strftime("31-12-%Y")
            elif selecion == "mensual":
                # Obtener el rango de fechas para el mes actual
                fecha_inicio = datetime.now().replace(day=1).strftime("%d-%m-%Y")
                fecha_fin = (datetime.now().replace(day=1) + timedelta(days=31)).strftime("%d-%m-%Y")         
    else:
        fecha_inicio = None
        fecha_fin = None

    filtro = obtener_filtro_history(fecha_inicio, fecha_fin)
        
    total = sum(fila[12] for fila in filtro)

    return render_template('filtrar.html', history=filtro, total=total)

def obtener_filtro_history(fecha_inicio, fecha_fin):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s AND date BETWEEN %s AND %s", ("2", fecha_inicio, fecha_fin))
    data = cur.fetchall()
    cur.close()

    return data

#! Delete Bill
@app.route('/delete_bill/<id>')
def delete_bill(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM art_bill WHERE id_bills = %s",(id,))
    mysql.connection.commit()

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM bills WHERE id = %s",(id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('bill_adm'))

#^ Edit Bill
@app.route('/edit_bill/<id>')
def edit_bill(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM bills WHERE id = %s',(id))
    bill_data = cur.fetchone()

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM art_bill WHERE id_bills = %s',(id))
    art_bill = cursor.fetchall()

    return render_template('edit_bill.html', bill_data=bill_data, article = art_bill)

@app.route('/update_bill/<id>', methods = ['POST', 'GET'])
def update_bill(id):

    if request.method == 'POST':

        fecha = request.form['date']
        cliente = request.form['customer']
        descuento = request.form['discount']
        methodo_pago = request.form['way_to_pay']
        monto = request.form['paid']
        cambio = request.form['change']
        cajero = request.form['cashier']
        rnc = request.form['rnc_client']
        ubicacion = request.form['ubicacion']
        contacto = request.form['contacto']
        total_general = request.form['total']
        ex_itbis = request.form['ex_itbis']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE bills SET date = %s, customer = %s, discount = %s, way_to_pay = %s, paid = %s, `change` = %s, cashier = %s, rnc_client_bill = %s, ubicacion = %s, contacto = %s, total_general = %s, Itbisextra = %s WHERE id = %s",
                    (fecha, cliente, descuento, methodo_pago, monto, cambio, cajero, rnc, ubicacion, contacto, total_general, ex_itbis, id))
        
        for idx, fila in enumerate(request.form.getlist('description')):
            descripcion = request.form.getlist('description')[idx]
            precio = request.form.getlist('price')[idx]
            itbis = request.form.getlist('itbis')[idx]
            cantidad = request.form.getlist('quantity')[idx]

            cur.execute("""UPDATE art_bill SET decrition = %s, price = %s, itbis = %s, amount = %s WHERE id_bills = %s AND decrition = %s""",
                        (descripcion, precio, itbis, cantidad, id, descripcion))
        
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('bill_adm'))
    
    return redirect(url_for('admin'))

#* Bills Admin
@app.route('/bills_adm', methods=['GET','POST'])
def bill_adm():
    if session['logged in'] == True and session['role_id'] == 1:
        bills = obtener_bills_adm()
        return render_template('bills_adm.html', bills = bills)
    else:
        return redirect(url_for('login'))


@app.route('/bills_table_adm')
def obtener_bills_adm():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s",("1"))
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/factura_detalle_adm/<id>')
def factura_detalle_adm(id):

    session['id_factura'] = id

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0
    total_discount = 0
    total_ex_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis

    for fila1 in bill:
        discount = fila1[4]
        ex_itbis = fila1[14]

        total_discount += subtotal * discount / 100
        total_ex_itbis += sub_total * ex_itbis / 100
    
    total_general_discount = total_general - total_discount
    total_general_ex_itbis = total_general_discount + total_ex_itbis

    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general_ex_itbis)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("detalle_adm.html", bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)

#* Bills
@app.route('/bills', methods=['GET','POST'])
def bill():
    if session['logged in'] == True and session['role_id'] == 2:
        bills = obtener_bills()
        return render_template('bills.html', bills = bills)
    else:
        return redirect(url_for('login'))


@app.route('/bills_table')
def obtener_bills():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s",("1"))
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/factura_detalle/<id>')
def factura_detalle(id):

    session['id_factura'] = id

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0
    total_discount = 0
    total_ex_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis

        for fila1 in bill:

            discount = fila1[4]
            ex_itbis = fila1[14]

            total_discount += subtotal * discount / 100
            total_ex_itbis += sub_total * ex_itbis / 100
        
    total_general_discount = total_general - total_discount
    total_general_ex_itbis = total_general_discount + total_ex_itbis
    
    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general_ex_itbis)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("detalle.html", bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)

#TODO Customers
@app.route('/customers', methods = ['GET', 'DELETE'])
def customer():
    if session['logged in'] == True and session['role_id'] == 2:
        clientes = obtener_customer()
        INCT = inactive()
        return render_template('customers.html', INCT = INCT, clientes=clientes)
    else:
        return redirect(url_for('login'))

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
    
@app.route('/deactivate_client/<int:id>', methods = ['GET', 'DELETE'])
def deactivate_client(id):
    if request.method == 'DELETE':
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
    
@app.route('/search_customers', methods=['POST'])
def search_customers():
    query = request.form['query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clients WHERE client_name LIKE %s AND activity_id LIKE %s", ('%' + query + '%', '1'))
    results = cur.fetchall()
    cur.close()
    return jsonify([{'id': result[0], 'name': result[1], 'address': result[2], 'phone': result[3], 'email': result[4], 'rnc': result[6]} for result in results])

@app.route('/search_customers_inactive', methods=['POST'])
def search_customers_inactive():
    query = request.form['query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clients WHERE client_name LIKE %s AND activity_id LIKE %s", ('%' + query + '%', '2'))
    results = cur.fetchall()
    cur.close()
    return jsonify([{'id': result[0], 'name': result[1], 'address': result[2], 'phone': result[3], 'email': result[4], 'rnc': result[6]} for result in results])


#* Articles
@app.route('/article')
def article():
    if session['logged in'] == True and session['role_id'] == 2:
        datos = obtener_datos_inv()
        articles = obtener_articles()
        customer = obtener_customer()
        employees = obtener_datos_emp()
        calculo = calculos()
        return render_template('articles.html', datos = datos, articles = articles, calculo = calculo, customer = customer, emp = employees, fullname = session['fullname'])
    else:
        return redirect(url_for('login'))

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


def enviar_alerta(producto,amount):

    nombre_p = producto
    stock = amount

    # Enviar correo electronico cuando se logue e usuario
    correo_remitente = "tecknopoint1@gmail.com"
    contrasena_remitente = "mrvw gpsb whcr tjjx"
    correo_destinatario = "slimerbatista27@gmail.com"
    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587

    correo_destinatario = email
    asunto="¡Alerta de Stock Bajo! 🚨"
    mensaje=f"""
                Solo quería advertirte que nuestro stock de {nombre_p} está llegando a niveles críticos. Actualmente solo quedan {stock} unidades disponibles en el punto de venta.

                ¡Es hora de reabastecer antes de que sea demasiado tarde!

                Gracias,
                TecknoPoint"""

    email = EmailMessage()
    email["From"] = correo_remitente
    email["To"] = correo_destinatario
    email["Subject"] = asunto
    email.set_content(mensaje)

    with smtplib.SMTP(servidor_smtp, puerto_smtp) as smtp:
        smtp.starttls()
        smtp.login(correo_remitente, contrasena_remitente)

        smtp.send_message(email)

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
@app.route('/inventario', methods = ['GET', 'DELETE'])
def inventario():
    if session['logged in'] == True and session['role_id'] == 2:
        datos = obtener_datos_inv()
        return render_template('inventario.html', datos=datos)
    else:
        return redirect(url_for('login'))

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE product_name LIKE %s", ('%' + query + '%',))
    results = cur.fetchall()
    cur.close()
    print(results)
    return jsonify(results)

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

@app.route('/remove_art/<string:id>', methods=['DELETE'])
def remove_art(id):

    if request.method == 'DELETE':

        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM products WHERE product_id = {0}'.format(id))
        mysql.connection.commit()
        flash('Contact Removed Successfully')
        return redirect(url_for('inventario'))

@app.route('/edit/<id>')
def get_art(id):
        cur = mysql.connection.cursor()
        cur.execute(' SELECT * FROM products WHERE product_id = %s', (id,))
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
        elif art_imagen.filename == '':
            cur = mysql.connection.cursor()
            cur.execute('SELECT image FROM products WHERE product_id = %s',(id,))
            art_imagen.filename = cur.fetchone()

        cur = mysql.connection.cursor()
        cur.execute('UPDATE products SET product_name = %s, product_price = %s, product_itbis = %s, product_amount = %s, amount = product_amount, product_catalogue = %s, image = %s WHERE product_id = %s', (art_name, art_price, art_itbis, art_cant, art_catalogo,art_imagen.filename,id))
        mysql.connection.commit()
        flash('Contact Updated Successfully')
        return redirect(url_for('inventario'))
    

#TODO  Login
@app.route('/login', methods=['GET','POST'])
def login():

    session['logged in'] = False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user:

            # Successful login, store information in the session
            session['id'] = user[0]
            session['username'] = username
            session['fullname'] = user[1]
            flash('Successful login', 'success')
            session['logged in'] = True
            session['role_id'] = user[5]

            session_id = str(session['id'])
            fecha_hora = datetime.now()
            fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S.%f")

            # cur.execute("UPDATE users SET state = TRUE WHERE user_id = %s", (session_id,))
            # mysql.connection.commit()

            cur = mysql.connection.cursor()
            cur.execute('UPDATE users SET state = %s WHERE user_id = %s',("1", session_id))
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
                        cur.execute('INSERT INTO time (id, id_users, entry_date) VALUES (%s, %s, %s)',(session_id, session_id, fecha_hora_formateada))
                        mysql.connection.commit()

                    return redirect(url_for('admin'))
                
                elif session['role_id'] == 2:
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT * FROM time WHERE id_users = %s',(session_id,))
                    duplicate = cur.fetchall()

                    if duplicate:
                        cur = mysql.connection.cursor()
                        cur.execute('UPDATE time SET entry_date = %s WHERE id_users = %s',(fecha_hora_formateada,session_id))
                        mysql.connection.commit()
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute('INSERT INTO time (id, id_users, entry_date) VALUES (%s, %s, %s)',(session_id, session_id, fecha_hora_formateada))
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
                    cur.execute('SELECT * FROM time WHERE id_users = %s',(session_id,))
                    duplicate = cur.fetchall()

                    if duplicate:
                        cur = mysql.connection.cursor()
                        cur.execute('UPDATE time SET entry_date = %s WHERE id_users = %s',(fecha_hora_formateada,session_id))
                        mysql.connection.commit()
                    else:
                        cur = mysql.connection.cursor()
                        cur.execute('INSERT INTO time (id, id_users, entry_date) VALUES (%s, %s, %s)',(session_id, session_id, fecha_hora_formateada))
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

    cur = mysql.connection.cursor()
    cur.execute('UPDATE users SET state = %s WHERE user_id = %s',("2", session['id']))
    mysql.connection.commit()

    # cur.execute("UPDATE users SET state = FALSE WHERE user_id = %s", (user[0],))
    # mysql.connection.commit()

    socketio.emit('get_users', namespace='/my_namespace')

    fecha_hora = datetime.now()
    fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S.%f")

    cur = mysql.connection.cursor()
    cur.execute('UPDATE time SET departure_date = %s WHERE id_users = %s',(fecha_hora_formateada,session['id']))
    mysql.connection.commit()

    session.clear()
    mensage = 'Sesión cerrada exitosamente', 'success'

    flash(message=mensage)
    return redirect(url_for('loader'))

#?  Proveedores
@app.route('/proveedor', methods = ['GET', 'DELETE'])
def proveedor():
    if session['logged in'] == True and session['role_id'] == 2:
        prov = obtener_datos_prov()
        return render_template('proveedores.html', prov=prov)
    else:
        return redirect(url_for('login'))

@app.route('/obtener_datos_prov')
def  obtener_datos_prov():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM suppliers")
    prov = cursor.fetchall()
    cursor.close()
    return prov

@app.route('/remove_prov/<string:id>', methods = ['GET','DELETE'])
def remove_prov(id):
    if request.method == 'DELETE':
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
            cur.execute("INSERT INTO suppliers (supplier_name, supplier_address, supplier_phone, supplier_email, activity_id) VALUES (%s,%s,%s,%s,%s)", (prov_name, prov_address, prov_phone, prov_email,'1'))
            mysql.connection.commit()
            cur.close()

        return redirect(url_for('proveedor'))

@app.route('/search_suppliers', methods=['POST'])
def search_suppliers():
    query = request.form['query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM suppliers WHERE supplier_name LIKE %s ", ('%' + query + '%',))
    results = cur.fetchall()
    cur.close()
    return jsonify([{'id': result[0], 'name': result[1], 'address': result[2], 'phone': result[3], 'email': result[4]} for result in results])

#& Cotizacion Admin
@app.route('/cotizacion_adm')
def cotizacion_adm():
    if session['logged in'] == True and session['role_id'] == 1:
        cotiz = obtener_adm_cotizacion()
        return render_template('cotizacion_adm.html', cotiz = cotiz)
    else:
        return redirect(url_for('login'))

@app.route('/cotizacion_adm_table')
def obtener_adm_cotizacion():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s",("1"))
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/detalle_cotizacion_adm/<id>')
def detalle_cotizacion_adm(id):

    session['id_cotizacion'] = id

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0
    total_discount = 0
    total_ex_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis

        for fila1 in bill:
            discount = fila1[4]
            ex_itbis = fila1[14]

            total_discount += subtotal * discount / 100
            total_ex_itbis += sub_total * ex_itbis / 100
    
    total_general_discount = total_general - total_discount
    total_general_ex_itbis = total_general_discount + total_ex_itbis
    
    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general_ex_itbis)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("detalle_cotizacion_adm.html", bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)


#* Cotizacion
@app.route('/cotizacion')
def cotizacion():
    if session['logged in'] == True and session['role_id'] == 2:
        cotiz = obtener_cotizacion()
        return render_template('cotizacion.html', cotiz = cotiz)
    else:
        return redirect(url_for('login'))

@app.route('/cotizacion_table')
def obtener_cotizacion():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s",("1"))
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/detalle_cotizacion/<id>')
def detalle_cotizacion(id):

    session['id_cotizacion'] = id

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0
    total_discount = 0
    total_ex_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis
    
        for fila1 in bill:
            discount = fila1[4]
            ex_itbis = fila1[14]

            total_discount += subtotal * discount / 100
            total_ex_itbis += sub_total * ex_itbis / 100
        
    total_general_discount = total_general - total_discount
    total_general_ex_itbis = total_general_discount + total_ex_itbis

    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general_ex_itbis)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("detalle_cotizacion.html", bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)


#? Cotizacion_emp

@app.route('/cotizacion_emp')
def cotiz_emp():
    if session['logged in'] == True and session['role_id'] == 3:
        cotiz = obtener_cotizacion_emp()
        return render_template('cotizacion_emp.html', cotiz = cotiz)
    else:
        return redirect(url_for('login'))

@app.route('/cotizacion_table')
def obtener_cotizacion_emp():
    if 'fullname' in session:
        fullname = session['fullname']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s AND cashier = %s",("1", fullname))
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/cotizacion_detalle_emp/<id>')
def cotizacion_detalle_emp(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0
    total_discount = 0
    total_ex_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis

        for fila1 in bill:
            discount = fila1[4]
            ex_itbis = fila1[14]

            total_discount += subtotal * discount / 100
            total_ex_itbis += sub_total * ex_itbis / 100
    
    total_general_discount = total_general - total_discount
    total_general_ex_itbis = total_general_discount + total_ex_itbis
    
    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general_ex_itbis)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("detalle_cotizacion_emp.html",bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)

@app.route('/cotizacion_p/<id>')
def cotizacion_p(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis
    
    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("cotizacion_detalle.html", bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)


#! Empleados

@app.route('/inicio_emp')
def inicio_emp():
    if session['logged in'] == True and session['role_id'] == 3:
        return render_template('/inicio_emp.html')
    else:
        return redirect(url_for('login'))

@app.route('/bills_emp')
def bill_emp():
    bills = obtener_bills_emp()
    return render_template('bills_emp.html', bills = bills)

@app.route('/bills_table')
def obtener_bills_emp():
    if 'fullname' in session:
        fullname = session['fullname']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s AND cashier = %s",("1", fullname))
    data = cur.fetchall()
    cur.close()

    return data

@app.route('/factura_detalle_emp/<id>')
def factura_detalle_emp(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE id = %s",(id,))
    bill = cur.fetchall()
    cur.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM art_bill WHERE id_bills = %s",(id,))
    detail = cursor.fetchall()
    cursor.close()

    total_general = 0
    sub_total = 0
    total_itbis = 0
    total_discount = 0
    total_ex_itbis = 0

    for fila in detail:
        art_price = fila[3]
        art_itbis = fila[4]
        art_mount = fila[5]

        subtotal = art_mount * art_price
        itbis = subtotal + ( subtotal * art_itbis / 100)
        sub_itbis = subtotal * art_itbis / 100

        # Calcular el total general sumando subtotal e ITBIS de cada producto
        total_general += itbis
        sub_total += art_mount * art_price
        total_itbis += sub_itbis
    
        for fila1 in bill:
            discount = fila1[4]
            ex_itbis = fila1[14]

            total_discount += subtotal * discount / 100
            total_ex_itbis += sub_total * ex_itbis / 100

    total_general_discount = total_general - total_discount
    total_general_ex_itbis = total_general_discount + total_ex_itbis

    # Formatear los números total_general e itbis con dos decimales
    total_general_formatted = "{:.2f}".format(total_general_ex_itbis)
    sub_total_formatted = "{:.2f}".format(sub_total)
    total_itbis_formatted = "{:.2f}".format(total_itbis)
    
    for fila in bill:
        fecha_N = fila[1]

    fecha_V = fecha_N + timedelta(days=30)

    return render_template("detalle_emp.html", bill=bill, detail=detail, total_itbis = total_itbis_formatted, subtotal = sub_total_formatted, total_general=total_general_formatted, fecha = fecha_V)

@app.route('/article_emp')
def article_emp():
    if session['logged in'] == True and session['role_id'] == 2:
        datos = obtener_datos_inv()
        articles = obtener_articles_emp()
        customer = obtener_customer()
        employees = obtener_datos_emp()
        calculo = calculos_emp()
        return render_template('articles_emp.html', datos = datos, articles = articles, calculo = calculo, customer = customer, emp = employees, fullname = session['fullname'])
    else:
        return redirect(url_for('login'))

@app.route('/calculos_emp')
def calculos_emp():
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

@app.route('/obtener_articles_emp')
def obtener_articles_emp():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM articles')
    article = cursor.fetchall()
    cursor.close()
    return article

@app.route('/incluir_art_emp/<id>')
def incluir_emp(id):
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
        return redirect(url_for('article_emp'))
    
    return redirect(url_for('article_emp'))

@app.route('/pay_emp', methods=["GET","POST"])
def pay_emp():

    IA()

    # Obtener los datos del formulario
    numero_tarjeta = request.form['numero_tarjeta']
    nombre_titular = request.form['nombre_titular']
    fecha_vencimiento = request.form['fecha_vencimiento']
    cvv = request.form['cvv']
    cliente = request.form['cliente']
    cajero = request.form['cajero']
    total = request.form['total']
    discount = request.form['discount']
    ex_itbis = request.form['ex-itbis']

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
    tarjeta = numero_tarjeta

    new_id = CIB()

    if tarjeta:
        fecha_hora = datetime.now()
        fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

        number_bill = GNF()

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO bills (id, date, number_bill, customer, discount, way_to_pay, paid, `change`, cashier, rnc_client_bill, ubicacion, contacto, total_general, estado, Itbisextra) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (new_id, fecha_hora_formateada, number_bill, customer, discount, "Tarjeta", "0", "0", cajero, rnc, ubicacion, contacto, total_general, 1, ex_itbis))
        mysql.connection.commit()
        APB(new_id)

        enviar(new_id)

        cur.execute("DELETE FROM articles")
        mysql.connection.commit()
        cur.close()

        flash("La compra se realizó con éxito")
        return redirect(url_for('article_emp'))
    else:
        flash("Hubo un problema con la tarjeta")
        return redirect(url_for('article_emp'))

@app.route("/payment_emp", methods=["GET", "POST"])
def payment_emp():
    
    IAE()

    # Obtener los datos del formulario
    cliente = request.form['cliente']
    cajero = request.form['cajero']
    monto = request.form['monto']
    total = request.form['total']
    discount = request.form['discount']
    ex_itbis = request.form['ex-itbis']
    

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

    total_float = float(total_general)
    monto_float = float(monto)

    cambio = monto_float - total_float

    new_id = CIBE()

    fecha_hora = datetime.now()
    fecha_hora_formateada = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

    number_bill = GNFE()

    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO bills (id, date, number_bill, customer, discount, way_to_pay, paid, `change`, cashier, rnc_client_bill, ubicacion, contacto, total_general, estado, Itbisextra) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (new_id, fecha_hora_formateada, number_bill, customer, discount, "Efectivo", monto_float, cambio, cajero, rnc, ubicacion, contacto, total_general, 1, ex_itbis))
    mysql.connection.commit()
    APBE(new_id)

    enviar(new_id)

    cur.execute("DELETE FROM articles")
    mysql.connection.commit()
    cur.close()

    flash("La compra se realizó con éxito")
    return redirect(url_for('article_emp'))

@app.route('/agregar_cantidad_art_emp/<int:id>')
def agregar_cantidad_emp(id):
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

    return redirect(url_for('article_emp'))

@app.route('/quitar_cantidad_art_emp/<id>')
def quitar_cantidad_emp(id):
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
    return redirect(url_for('article_emp'))

@app.route('/remove_article_emp/<string:id>')
def remove_article_emp(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM articles WHERE id = {0}'.format(id))
    mysql.connection.commit()

    cur.execute('UPDATE products SET product_amount = product_amount + 1 WHERE product_id = %s', (id,))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('article_emp'))

@app.route('/cierre_emp', methods = ['POST','GET'])
def cierre_emp():

    id_C = CIBC()
    fullname = session['fullname']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bills WHERE estado = %s AND cashier = %s",(1,fullname))
    bills = cur.fetchall()

    observaciones = request.form['observacion']

    fechahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    totalingresos = 0
    totalegresos = 0
    totaltarjeta = 0
    totalefectivo = 0
    totaldevoluciones = 0
    arqueocaja = 0
    cajero = fullname

    cur.execute("SELECT * FROM closing_box ORDER BY fechahora DESC LIMIT 1")
    last_insertion = cur.fetchone()

    if last_insertion:
        saldo = last_insertion[2]
        if saldo is not None and saldo > 0:
            saldoinicial = saldo
        else:
            saldoinicial = 1000
    else:
        saldoinicial = 1000

    for bill in bills:
        total_bill = bill[12]
        egresos_bill = bill[7]

        totalegresos += egresos_bill
        totalingresos += total_bill

        methodo = bill[5]

        if methodo == "Tarjeta":
            totaltarjeta += total_bill
        elif methodo == "Efectivo":
            totalefectivo += total_bill
        else:
            flash("Hubo un error")

    saldo_final = saldoinicial + totalingresos - totalegresos
        
    arqueocaja = saldo_final - saldoinicial
                
        
    cur.execute("INSERT INTO closing_box (id_closing, fechahora, saldoinicial, totalingresos, totalegresos, totalventasefectivo, totalventastarjeta, totaldevoluciones, arqueocaja, observaciones, cajero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (id_C, fechahora, saldoinicial, totalingresos, totalegresos, totalefectivo, totaltarjeta, totaldevoluciones, arqueocaja, observaciones, cajero))
    mysql.connection.commit()
    cur.close

    cur.execute("UPDATE bills SET estado = %s",('2'))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('bill_emp'))

#? Empleados Funcion

@app.route('/empleados', methods = ['GET', 'DELETE'])
def empleados():
    if session['logged in'] == True and session['role_id'] == 2:
        empleados = obtener_datos_emp()
        return render_template('/empleados.html', empleados=empleados)
    else:
        return redirect(url_for('login'))

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
    
@app.route('/remove_emp/<string:id>', methods = ['GET', 'DELETE'])
def remove_emp(id):
    if request.method == 'DELETE':
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM time WHERE id_users = {0}'.format(id))
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

@app.route('/search_employees', methods=['POST'])
def search_employees():
    query = request.form['query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE fullname LIKE %s AND role_id = %s", ('%' + query + '%','3'))
    results = cur.fetchall()
    cur.close()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)