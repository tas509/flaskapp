import sqlite3
import sys
from easygui import *
db = sqlite3.connect('test1.db')
delname=enterbox("Enter the name to be deleted")

cursor.execute('''DELETE FROM users WHERE name=?''',(delname,))
msgbox("Contact successfully deleted")
db.commit()

cursor.execute('''SELECT name, phone FROM users''')
user1 = cursor.fetchone() #retrieve the first row
#print(user1[0]) #Print the first column retrieved(user's name)
all_rows = cursor.fetchall()
print ("Your contact list \n")
for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
	print('{} \t{}'.format(row[0], row[1]))
db.commit()