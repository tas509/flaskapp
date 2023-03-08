import sys
import pathlib
import sqlite3

sys.path.insert(0,'/home/tomsmith/apps/flask/www')
from flask import Flask, render_template, request, url_for, flash, redirect, abort
from flask import send_from_directory
from flask_httpauth import HTTPBasicAuth #basic auth stuff
from werkzeug.security import generate_password_hash, check_password_hash #auth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


DB_PATH = f'{pathlib.Path(__file__).parent.resolve()}/mydatabase.db'
SITEPATH = "/home/tomsmith/apps/flask/www/"

############################ AUTH ######################################

# https://github.com/miguelgrinberg/Flask-HTTPAuth
users = {
    "tom": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

##########################################################################
 
def get_connection():
    conn = sqlite3.connect(SITEPATH +'/mydatabase.db')
    conn.row_factory = sqlite3.Row
    return conn

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_page(page_id):
    conn = get_connection()

    page = conn.execute('SELECT * FROM pages WHERE id = ?',(page_id,)).fetchone()

    if page is None:
        abort(404)
    return page


@app.route('/')
def index():
    conn = get_connection()
    

    sql = '''
    SELECT pages.*, users.name as owner_name 
    FROM 
    pages 
    INNER JOIN users ON pages.ownerId = users.id; 
    '''

    print(sql, conn)
    pages = conn.execute(sql).fetchall()

    
    results = {}
    for page in pages:
        id = page['id']

        sql = '''
        SELECT tags.*
        FROM tags
        INNER JOIN page_tags ON tags.id = page_tags.tag_id
        WHERE page_tags.page_id = ''' + str(id)
        tags = conn.execute(sql).fetchall()
        print(tags)
        #page['tags'] = tags

    user = auth.current_user()
    conn.close()   
    return render_template('index.html', pages=pages, user=user)

# ...

#page = db.execute('SELECT * FROM pages WHERE id = ?', (page_id,)).fetchone()

@app.route('/create/', methods=('GET', 'POST'))
@auth.login_required
def create():
    conn = get_connection()
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']

        if not title:
            flash('Title is required!')
        elif not text:
            flash('Text is required!')
        else:
            
            conn.execute('INSERT INTO pages (title, text, ownerId) VALUES (?, ?, 1)',
                         (title, text))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    conn.close()   
    return render_template('create.html')

@app.route('/page/edit/<int:id>', methods=('GET', 'POST'))
@auth.login_required
def edit(id):
    conn = get_connection()
    page = get_page(id)

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']

        if not title:
            flash('Title is required!')

        elif not text:
            flash('Text is required!')

        else:
            conn = get_connection()
            conn.execute('UPDATE pages SET title = ?, text = ?'
                         ' WHERE id = ?',
                         (title, text, id))
            conn.commit()
            
            return redirect(url_for('index'))

    conn.close()   
    return render_template('edit.html', page=page)

@app.route('/<int:id>/delete/', methods=('POST',))
@auth.login_required
def delete(id):
    conn = get_connection()
    post = get_page(id)

    conn.execute('DELETE FROM pages WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/page/<int:page_id>')
def show_page(page_id):
    # Retrieve page data from database
    #conn = get_db_connection()
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT p.*, u.name AS owner_name, GROUP_CONCAT(t.name) AS tag_names
                 FROM pages p
                 LEFT JOIN users u ON p.ownerId = u.id
                 LEFT JOIN page_tags pt ON p.id = pt.page_id
                 LEFT JOIN tags t ON pt.tag_id = t.id
                 WHERE p.id = ?''', (page_id,))
    page = c.fetchone()
    print("page",page)
    # Convert tag names string to list
   
    
    page_dict = dict_factory(c, page)
    page_dict['tag_names'] = page['tag_names'].split(',') if page['tag_names'] else []
    print("page_dict", page_dict)
   

    if not page:
        return "Page not found", 404

    
    print("page_dict", page_dict )

    conn.close()   
    # Render page using Jinja2 template
    return render_template('page.html', page=page_dict)

@app.route('/tags')
def tags():
    conn = get_connection()
    sql = '''SELECT tags.*
            FROM tags'''
    conn = get_connection()
    c = conn.cursor()
    tags = c.execute(sql).fetchall()


    conn.close()   
    return render_template('tags.html', tags=tags)

@app.route('/tag/<string:tag_name>')
def show_tag(tag_name):
    # Retrieve page data from database
    #conn = get_db_connection()
    conn = get_connection()
    c = conn.cursor()
    sql = "select * from tags where name ='{0}'".format(tag_name)
    tag = c.execute(sql).fetchone()
    print(tag)
    conn.close()
    return render_template('tag.html', tag=tag)


########################################################

@app.route('/reports/<path:path>')
def send_report(path):
    return send_from_directory('reports', path)

@app.route('/search/')
@app.route('/search/<string:urlquery>')
def search_pages(urlquery=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if urlquery == None:
        query = request.args.get('query')
    else:
        query = urlquery.replace("+", " ")#HACK!
    
    print("query: ", query)
    sql = '''SELECT pages.id, pages.title, pages.text, 
                users.name as owner, 
                GROUP_CONCAT(tags.name) as tags 
                FROM pages 
                JOIN users ON pages.ownerId = users.id 
                LEFT JOIN page_tags ON pages.id = page_tags.page_id 
                LEFT JOIN tags ON page_tags.tag_id = tags.id 
                WHERE pages.title 
                LIKE '%{0}%'
                OR 
                pages.text LIKE '%{0}%'
                GROUP BY pages.id'''.format(query)
    print(sql)
    c.execute(sql)
    print()
    rows = c.fetchall()
    pages = []
    for row in rows:
        page_dict = dict(row)
        print(page_dict)
        pages.append(page_dict)

    conn.close()
    return render_template('search.html', pages=pages, query=query)

if __name__ == "__main__":
    app.run()

