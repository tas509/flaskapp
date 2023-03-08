import sqlite3

conn = sqlite3.connect('./mydatabase.db')
conn.row_factory = sqlite3.Row



sql = '''
SELECT pages.*, users.name as owner_name 
FROM 
pages 
INNER JOIN users ON pages.ownerId = users.id; 
'''

print(sql, conn)
pages = conn.execute(sql).fetchall()
for page in pages:
    print(page)