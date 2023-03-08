import sqlite3
import sys
from easygui import *
db = sqlite3.connect('test1.db')
# Get a cursor object
cursor = db.cursor()
#cursor.execute('''    CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT,phone TEXT)''')
#db.commit()
def enbox():
	msg= "Enter your personal information"
	title = "Contact Application"
	fieldNames = ["Name","Phone"]
	users = []  # we start with blanks for the values
	users = multenterbox(msg,title, fieldNames)
	cursor.execute(''' INSERT INTO users(name, phone) VALUES(?,?)''',users)
	db.commit()
	print ("Reply was:", users)
ynmsg=" Do you want to continue "
title="Please confirm"
while True:
	enbox()
	if not ynbox(ynmsg,title):
		 break
cursor.execute('''SELECT name, phone FROM users''')
user1 = cursor.fetchone() #retrieve the first row
#print(user1[0]) #Print the first column retrieved(user's name)
all_rows = cursor.fetchall()
print ("Your contact list \n")
for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
	print('{} \t {}'.format(row[0], row[1]))