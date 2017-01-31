import MySQLdb
import config
import random
import re
from werkzeug import generate_password_hash, check_password_hash


#   TODO
#certain functions like userameTaken() and the like should be moved to a DB class, as a user querying to see if its own username has been taken doesnt make much logical sense

#designed to be a class which allows full autonomy (minus deleting the account) over the user personal information
#userDict is used for storing values as strings
class User:
    db = MySQLdb.connect(host='localhost', user=config.USER, passwd=config.PASS, db=config.MYDB)
    cursor = db.cursor()
    requiredFields = ['fname','lname','username','email','password'] #items that cannot be null in the db

    def __init__(self, username, email, password):
        self.userDict = {'username':username, 'email':email, 'password':password}
        self.doesExist = self.exists()

    #i like this get method the most
    def get(self, val):
        if not val in self.userDict:
            return
        return self.userDict[val]

    #returns True if user has username/email and password combination, False otherwsie
    def exists(self):
        #check db to check if user exists
        if not all (vals in self.userDict for vals in ("username","email", "password")):
            return False

        sql = "select password from users where email=%s OR username=%s limit 1"
        self.cursor.execute(sql, (self.userDict['email'], self.userDict['username']))
        
        if self.cursor.rowcount == 0:
            return False
        
        data = self.cursor.fetchone()
        if check_password_hash(data[0], self.userDict['password']):
            return True
        else:
            return False

    def getData(self):
        if self.doesExist:
            if not 'email' in self.userDict or not 'username' in self.userDict:
                return "Cannot query for user %s: user does not exist"

            sql = "SELECT userID, fname, lname, username, email, schoolName FROM users WHERE email = %s OR username = %s LIMIT 1"
            self.cursor.execute(sql, (self.userDict['email'], self.userDict['username']))
            data = self.cursor.fetchone()

            temp = {}
            temp['userID'] = data[0]
            temp['fname'] = data[1]
            temp['lname'] = data[2]
            temp['username'] = data[3]
            temp['email'] = data[4]
            temp['schoolName'] = data[5] #is there a better way to do this?

            for val in temp:
                self.userDict[val] = temp[val]
            return temp #dont send userDict due to password existing in plain text there
        else:
            return "Cannot query for user %s: user does not exist" % self.userDict['username']        

    def validEmail(self):
        if not 'email' in self.userDict:
            return False

        #"any non @ symbol 1 or more times, followed by an @ symbol, followed
        #by any non @ symbol 1 or more times, followed by a single period,
        #followed by any non @ symbol 1 or more times"
        return re.match(r"[^@]+@[^@]+\.[^@]+", self.userDict['email'])

    #returns array of error messages which is empty upon valid password
    def validatePassword(self):
        #check to see if password matches general requirements
        #1 or more capital letters
        #8 or more characters
        #1 or more numbers

        if not 'password' in self.userDict:
            return False

        p1 = self.userDict['password']
        errors = []
        if not any(x.isupper() for x in p1):
            errors.append('Your password needs at least 1 capital letter<br/>')
        if not any(x.isdigit() for x in p1):
            errors.append('Your password needs at least 1 number<br/>')
        if len(p1) < 8:
            errors.append('Your password needs to be at least 8 characters<br/>')

        return errors

    #returns True or False
    def usernameTaken(self):
        if not 'username' in self.userDict:
            return True
        sql = "SELECT count(username) FROM users WHERE username LIKE %s"
        self.cursor.execute(sql, [self.get('username')])
        data = self.cursor.fetchone()
        for row in data:
            if row != 0: #username taken
                return True
        return False

    #returns True or False
    def emailTaken(self):
        if not 'email' in self.userDict:
            return True
        sql = "SELECT count(email) FROM users WHERE email LIKE %s"
        self.cursor.execute(sql, [self.get('email')])
        data = self.cursor.fetchone()
        for row in data:
            if row != 0: #email taken
                return True
        return False

    def userIDTaken(self, userID = ""):
        #if no userID value is available
        if not 'userID' in self.userDict and userID == "":
            return True
 
        sql = "SELECT count(userID) FROM users WHERE userID LIKE %s"
        print sql + userID or self.get('userID')
        self.cursor.execute(sql, [userID or self.get('userID')]) #if userID = "", then pass other value
        data = self.cursor.fetchone()

        if data[0] != 0: #userID taken
            return True

        return False

    #requires the user to already exist in db
    #returns true or false on success or failure
    def updateUser(self):
        if not self.doesExist:
            print "Unable to save user %s: user does not exist" % self.userDict['username']
            return False

        return False

    #queries db until if finds a non-used valid 16 character ID
    #returns valid userID
    def generateValidID(self):
        # there are 16! (factorial) possible options, this loop should not run more than a few times at the very worst, assuming random generates pseudo-random keys
        timesTried = 0
        while timesTried < 1000:
            userID = "".join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(16))

            if not self.userIDTaken(userID = userID):
                #userID is not taken, return userID
                return userID
            ++timesTried

        print "Error while trying to create a valid ID. Generated %d IDs" % timesTried
        return "0"

    #requires user to not exist in db
    #returns true or false on success or failure
    def insertUserIntoDB(self, values = {}):
        if self.doesExist:
            print "Unable to insert user %s: user already exists" % self.userDict['username']
            return False
        if not values:
            print "Unable to insert user %s: must pass a values dict" % self.userDict['username']
            print "Values dict must contain these values: {'" + "', '".join(requiredFields) + "'}"
            return False

        unusedFields = []
        for f in self.requiredFields:
            if not f in values:
                unusedFields.append(f)

        if unusedFields: #if unused fields is not empty 
            print "Unable to insert user " + self.userDict['username'] + ": values dict needs these keys to be valid: {'" + "', '".join(unusedFields) + "'}"
            return False

        
        if 'userID' in values: #set id in db if userID value is passed
            self.userDict['userID'] = values['userID']
        elif not 'userID' in self.userDict: #otherwise set it to a random valid id
            self.userDict['userID'] = self.generateValidID()

        if self.userDict['userID'] == "0":
            #error generating valid ID
            return False

        if not 'schoolName' in self.userDict:
            if 'schoolName' in values:
                self.userDict['schoolName'] = values['schoolName']
            else:
                self.userDict['schoolName'] = 'None'

        hashed_password = generate_password_hash(values['password'])

        sql = "INSERT INTO users VALUES(%s,%s,%s,%s,%s,%s,%s, NOW())" #this makes me sad. how can we make this better?
        self.cursor.execute(sql, (self.userDict['userID'], values['fname'], values['lname'], values['username'], values['email'], hashed_password, self.userDict['schoolName']))
        data = self.cursor.fetchall()

        if len(data) is 0:
            print "Inserted user into db"
            self.db.commit()
            for key in values: 
                self.userDict[key] = values[key]
            
            print self.userDict
            return True
        else:
            return False
