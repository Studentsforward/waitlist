class User:
    def __init__(self, username, email, password, cursor):
        self.username = username
        self.email = email
        self.password = password
        self.cursor = cursor
        self.doesExist = self.exists()

    #returns True if user has username/email and password combination, False otherwsie
    def exists(self):
        if not self.cursor:
            return "Unable to check if user exists. Cursor not set"

        #check db to check if user exists
        sql = "select password from users where email=%s OR username=%s limit 1"
        self.cursor.execute(sql, (self.email, self.username))
        
        if self.cursor.rowcount == 0:
            return False
        
        data = self.cursor.fetchone()
        if check_password_hash(data[0], self.password):
            return True
        else:
            return False

    def getData(self):
        if not self.cursor:
            return "Unable to check if user exists. Cursor not set"

        if doesExist:
           print "hi" 
        else:
            print "Cannot query for user %s: user does not exist" % self.username        
