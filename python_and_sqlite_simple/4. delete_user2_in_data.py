### Delete user with id 2
import sqlite3
db = sqlite3.connect('test1.db')
cursor= db.cursor()
delete_userid = 1
cursor.execute('''DELETE FROM users WHERE id = ? ''', (delete_userid,))
db.commit()


cursor.execute('''SELECT name, email, phone FROM users''')
all_rows = cursor.fetchall()
print ("The updated list\n")
print("#" * 80)
for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} \t {1}\t {2}'.format(row[0], row[1], row[2]))
db.commit()
print("#" * 80)