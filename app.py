from flask import Flask , render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import bcrypt
from markupsafe import escape

app = Flask(__name__)

#MYSQL Configuracion    
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_users'  
mysql = MySQL(app)

#settings 
app.secret_key = 'myllavesecreta'

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    tabla_completa = mysql.connection.cursor()

    cur.execute('SELECT Nombre, Apellidos FROM usuarios')
    data_nombres = cur.fetchall()

    tabla_completa.execute('SELECT Nombre, Apellidos, Telefono, Correo, Pais, Direccion, Usuario FROM usuarios')

    return render_template("index.html", usuarios_tabla = tabla_completa)

@app.route('/Registro')
def Registro():
    return render_template('Registro_Usuario.html')

@app.route('/Verificacion', methods = ['POST'])
def Verificacion():
    if(request.method == 'POST'):
        nombre = request.form['Nombre']
        apellidos = request.form['Apellidos']
        telefono = request.form['Telefono']
        correo = request.form['Correo']
        pais = request.form['Pais']
        direccion = request.form['Direccion']
        
        usuario = request.form['Usuario']
        contraseña = request.form['Contraseña']

        #Encriptacion de contraseña --

        contra_utf8 = contraseña.encode('utf-8')
        sal = bcrypt.gensalt()

        contraseña_encriptada = bcrypt.hashpw(contra_utf8, sal)

        # -- Termino de encriptacion

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO usuarios (Nombre, Apellidos, Telefono, Correo, Pais, Direccion, Usuario, Contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        (nombre, apellidos, telefono, correo, pais, direccion, usuario, contraseña_encriptada))
        mysql.connection.commit()

        flash('Ingresado Correctamente')

        return redirect(url_for('Index'))
    

class Usuario:
    def __init__(self, usuario_dado):
        cur = mysql.connection.cursor()
        
        
        cur.execute('SELECT * FROM usuarios WHERE Usuario = %s', (usuario_dado,))
        usuario = cur.fetchone()

        if usuario:
            self.id = usuario[0]
            self.nombre = usuario[1]
            self.apellidos = usuario[2]
            self.telefono = usuario[3]
            self.correo = usuario[4]
            self.pais = usuario[5]
            self.direccion = usuario[6]
            self.usuario = usuario[7]
            self.contraseña = usuario[8]
        else:
            
            self.id = None
            self.nombre = None
            self.apellidos = None
            self.telefono = None
            self.correo = None
            self.pais = None
            self.direccion = None
            self.usuario = None
            self.contraseña = None
        
        cur.close() 

@app.route('/Verificacion_login', methods = ['POST'])
def Verificacion_login():

    if(request.method == 'POST'):

        Usuario_Login = request.form['Usuario_Login']
        Contraseña_Login = request.form['Contraseña_Login']

        cur = mysql.connection.cursor()
        consulta_usuario = cur.execute('SELECT Usuario FROM usuarios WHERE Usuario = %s',
        (Usuario_Login,))
        mysql.connection.commit()

        if(consulta_usuario):
            
            Contraseña_Login_utf_8 = bytes(Contraseña_Login, 'utf-8')

            Usuario_l = Usuario(Usuario_Login)

            if(bcrypt.checkpw(Contraseña_Login_utf_8, Usuario_l.contraseña.encode('utf-8'))):

                session["cookie_id"] = Usuario_l.id

                return redirect(url_for('Secciones'))

            else:

                flash('Usuario o Contraseña erroneas, verifique su informacion')
                return redirect(url_for('Index'))
        else:
            flash('Usuario o Contraseña erroneas, verifique su informacion')
            return redirect(url_for('Index'))


    return redirect(url_for('Index'))


@app.route('/Logout')
def Logout():
    session.pop("cookie_id", None)
    return redirect(url_for('Index')) 


@app.route('/Secciones')
def Secciones():
    if("cookie_id" in session):
        return render_template('Secciones.html')
    else:
        return redirect(url_for('Index'))   


@app.route('/Frutas_y_Verduras')
def Frutas_y_Verduras():
    return render_template('Frutas_y_Verduras.html')


if __name__ == '__main__' :
    app.run(port = 3002, debug = True)