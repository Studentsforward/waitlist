from flask import *
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import config
from user import *

app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = config.USER
app.config['MYSQL_DATABASE_PASSWORD'] = config.PASS
app.config['MYSQL_DATABASE_DB'] = config.MYDB
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)





@app.route("/")
def main():
    return render_template("index.html")

@app.route("/login")
def loginScreen():
    return render_template("login.html")

@app.route("/main")
def routeToMain():
    return render_template("index.html")

@app.route("/home", methods=("GET", "POST"))
def home():
    return render_template("home.html")

@app.route("/signUp")
def showSignUp():
    return render_template("testsignup.html")

@app.route('/signUpPost',methods=['POST'])
def signUp():
    # read the posted values from the UI
    fname = request.form['inputfname']
    lname = request.form['inputlname']
    username = request.form['inputusername']
    email = request.form['inputemail']
    schoolname = request.form['inputschoolname']
    p1 = request.form['inputpassword1']
    p2 = request.form['inputpassword2']

    if not (fname and lname and username and email and schoolname and p1 and p2):
        return json.dumps({'error':'Forms not filled out'})
    #check that passwords match
    if (p1 != p2):
        return json.dumps({'error':'Passwords do not match'})

    u = User(username, email, p1)

    if not u.validEmail():
        return json.dumps({'error': "Invalid email"})
    #make sure username and email are not taken
    if u.usernameTaken():
        return json.dumps({'error':'That username is taken'})
    if u.emailTaken():
        return json.dumps({'error':'That email is in use'})

    errors = u.validatePassword() #either an array of strings, or empty if valid password
    if errors: #if errorArray is not empty
        return json.dumps({'error': " ".join(errors)})

    userInfo = {'username':username, 'email':email, 'fname':fname, 'lname':lname, 'schoolName':schoolname,'password': p1}
    if u.insertUserIntoDB(values = userInfo):
        return json.dumps({'success':'User created successfully!'})
    return json.dumps({'error':'There was an error creating your user account. Please try again later'})

@app.route('/waitlist', methods=['POST'])
def joinWaitlist():
    #read info from UI
    if request.method == 'POST':
        email = request.form['inputEmail']

    if not email:
        return json.dumps({'error':'No email given'})

    #"any non @ symbol 1 or more times, followed by an @ symbol, followed
    #by any non @ symbol 1 or more times, followed by a single period,
    #followed by any non @ symbol 1 or more times"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return json.dumps({'error':'Invalid email'})

    #create db instance
    conn = mysql.connect()
    cursor = conn.cursor() 

    #check if email exists in db
    sql = "SELECT dateCreated FROM waitlist WHERE email like %s"
    cursor.execute(sql, email)

    if cursor.rowcount == 0: #email does not exist, insert user
        sql = "INSERT INTO waitlist VALUES(%s,NULL)"
        cursor.execute(sql, email)
        conn.commit()

    #user should exist in db at this point. query waitlist number based on date
    sql = "SELECT count(dateCreated)+1 FROM waitlist WHERE dateCreated < (SELECT dateCreated FROM waitlist WHERE email like %s)"
    #return sql % email
    cursor.execute(sql, email)
    #return json.dumps({'success':'You are number ' + str(data[0]) + ' on our waitlist','waitlistNum':data[0], 'email':email})

    if cursor.rowcount != 0: #success
        data = cursor.fetchone()
        return json.dumps({'success':'You are number ' + str(data[0]) + ' on our waitlist','waitlistNum':data[0], 'email':email})
    else:
        return json.dumps({'error':'There was an issue putting you on our waitlist. Please try again in a moment'})

@app.route('/signIn')
def showSignIn():
    return render_template("testlogin.html")

@app.route('/signInPost',methods=['POST'])
def signIn():
    # read the posted values from the UI
    email = request.form['inputEmail']
    password = request.form['inputPassword']

    if not (email and password):
        return json.dumps({'error':'Forms not filled out'})

    u = User(email, email, password)
    if u.doesExist:
        #return redirect(url_for("home"), code=307)
        data = u.getData()
        return json.dumps({'success':'User authenticated', 'userDict':data})
    else:
        return json.dumps({'error':'Incorrect email or password'})


app.run('0.0.0.0', port=80)
