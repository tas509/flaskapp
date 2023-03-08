import sqlite3
db = sqlite3.connect('test1.db')

'''
# JUST GET ONE
cursor = db.cursor()
cursor.execute('SELECT name, email, phone FROM users')
user1 = cursor.fetchone() #retrieve the first row
print("The name of first user is",user1[0]) #Print the first column retrieved(user's name)
'''


cursor = db.cursor()
cursor.execute('''SELECT name, email, phone FROM users''')
all_rows = cursor.fetchall()
print ("The contact list\n")
print("#" * 80)

for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} \t {1}\t {2}'.format(row[0], row[1], row[2]))
db.commit()

print("#" * 80)