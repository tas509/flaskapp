import sqlite3
db = sqlite3.connect('test1.db')

cu= db.cursor()
newphone = '2342358'
userid = 1
cu.execute('''UPDATE users SET phone = ? WHERE id = ? ''',(newphone,userid))
cu.execute('''SELECT name, email, phone FROM users''')
all_rows = cu.fetchall()

print ("The updated list\n")
for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} \t {1}\t {2}'.format(row[0], row[1], row[2]))
db.commit()