import sqlite3
db = sqlite3.connect('test1.db')
cursor = db.cursor()

name1 = 'Soumya'
phone1 = '3366858'
email1 = 'soumya@example1.com'
# A very secure password
password1 = '12345'
 
name2 = 'Shiny'
phone2 = '5557241'
email2 = 'shiny@example2.com'
password2 = 'abcdef'

#CREATE THE DATABASE
cursor = db.cursor()
cursor.execute('''CREATE TABLE users(
            id INTEGER PRIMARY KEY, 
            name TEXT,phone TEXT, 
            email TEXT unique, 
            password TEXT)''')
db.commit()


 
# Insert user 1
cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(?,?,?,?)''', (name1,phone1, email1, password1))
print('First user inserted')
 # Insert user 2
cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(?,?,?,?)''', (name2,phone2, email2, password2))
print('Second user inserted')
 
db.commit()