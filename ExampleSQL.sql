-- DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL
  
);

CREATE TABLE tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE pages (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  text TEXT,
  price FLOAT,
  views INTEGER DEFAULT 0,
  created_at DATE DEFAULT (datetime('now', 'localtime')),
  score REAL,
  is_published BOOLEAN NOT NULL DEFAULT 0,

  ownerId INTEGER NOT NULL,
  FOREIGN KEY(ownerId) REFERENCES users(id) ON DELETE CASCADE
  
);

-- Note: FOREIGN KEY(ownerId) REFERENCES users(id) <-- won't delete pages owned when the user
-- is deleted.
 
CREATE TABLE page_tags (
  page_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY (page_id, tag_id),
  FOREIGN KEY (page_id) REFERENCES pages(id),
  FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- END DATABASE CREATION

-- DATABASE ALTERATION

ALTER TABLE pages ADD COLUMN image BLOB NULL;

-- INSERT DEFAULT DATA

INSERT INTO users (name, email, password) VALUES ('John Smith', 'john.smith@example.com', 'password123');
INSERT INTO users (name, email, password) VALUES ('Jane Doe', 'jane.doe@example.com', 'password456');

INSERT INTO tags (name) VALUES ('Important');
INSERT INTO tags (name) VALUES ('Urgent');

-- Assuming user with id 1 owns the first page
INSERT INTO pages (id, title, text, ownerId) VALUES (1, 'My First Page', 'This is the text of my first page.', 1);

-- Assuming user with id 2 owns the second page
INSERT INTO pages (id, title, text, ownerId) VALUES (2, 'My Second Page', 'This is the text of my second page.', 2);

-- Assuming pages with ids 1 and 2 are tagged with "Important" and page 2 is also tagged with "Urgent"
INSERT INTO page_tags (page_id, tag_id) VALUES (1, 1);
INSERT INTO page_tags (page_id, tag_id) VALUES (2, 1);
INSERT INTO page_tags (page_id, tag_id) VALUES (2, 2);

UPDATE pages SET title = 'Updated Page Name', text = 'This is the updated text for the page with id 1' WHERE id = 1;

--------------------------
DELETE FROM users WHERE id = 1; -- deletes the user with id 1
DELETE FROM pages WHERE ownerId = 1; -- deletes all pages owned by the user with id 1

CREATE INDEX idx_pages_ownerId ON pages(ownerId); -- creates an index on the ownerId column of the pages table, which can improve performance when joining the pages and users tables

DROP TABLE pages; -- deletes the pages table and all of its data
DROP INDEX idx_pages_ownerId; -- deletes the index on the ownerId column of the pages table

-------------------------- QUERY EXAMPLES 

SELECT * FROM users; -- selects all columns from the users table
SELECT name, email FROM users WHERE id = 1; -- selects only the name and email columns for the user with id 1

-- selects the name and text of each page, along with the name of the page's owner
SELECT pages.title, pages.text, users.name as owner_name FROM pages INNER JOIN users ON pages.ownerId = users.id; 

SELECT pages.*
FROM pages
INNER JOIN page_tags ON pages.id = page_tags.page_id
INNER JOIN tags ON page_tags.tag_id = tags.id
WHERE tags.name = 'Urgent';



SELECT tags.*
FROM tags
INNER JOIN page_tags ON tags.id = page_tags.tag_id
WHERE page_tags.page_id = 1;

---------------------------- MORE ADVANCED QUERIES

SELECT pages.id, pages.title, COUNT(page_tags.tag_id) AS tag_count
FROM pages
INNER JOIN page_tags ON pages.id = page_tags.page_id
INNER JOIN tags ON page_tags.tag_id = tags.id
WHERE tags.name = 'Urgent'
GROUP BY pages.id
ORDER BY tag_count DESC, pages.title ASC
LIMIT 10;

-- VIEWS

-- A
CREATE VIEW page_tags_view AS
SELECT pages.title, tags.name AS tag_name
FROM pages
INNER JOIN page_tags ON pages.id = page_tags.page_id
INNER JOIN tags ON page_tags.tag_id = tags.id;

-- B
SELECT name
FROM page_tags_view
WHERE tag_name = 'Urgent';

--C
SELECT name, COUNT(tag_name) AS tag_count
FROM page_tags_view
GROUP BY name;

-- D
SELECT tag_name, COUNT(name) AS page_count
FROM page_tags_view
GROUP BY tag_name
ORDER BY page_count DESC
LIMIT 10;

-- E
SELECT tag_name, COUNT(name) AS page_count
FROM page_tags_view
INNER JOIN pages ON page_tags_view.name = pages.name
WHERE pages.ownerId = 1
GROUP BY tag_name
ORDER BY page_count DESC
LIMIT 10;

--------------------------------- END


/* USING SQLITE FROM THE COMMAND LINE

sqlite3 mydatabase.db --create a database
SELECT * FROM users; -- must plop into a REPL

sqlite3 mydatabase.db < myscript.sql -- < -- fire some sql at the  db.

sqlite3 mydatabase.db
.mode csv
.import mydata.csv mytable

sqlite3 mydatabase.db
.mode csv
.headers on
.output mydata.csv
SELECT * FROM mytable;



### PYTHON CODE

import sqlite3

conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()

# example data
title = 'My Page'
text = "This is my page's text with a single quote: O'Brien"
owner_id = 1
tag_ids = [1, 2, 3]

# insert the page
c.execute("INSERT INTO pages 
        (title, text, ownerId)   
            VALUES 
        (?, ?, ?)",
        (title, text, owner_id))
        page_id = c.lastrowid

# insert the page tags
for tag_id in tag_ids:
    c.execute("INSERT INTO page_tags (pageId, tagId) VALUES (?, ?)",
              (page_id, tag_id))

# commit the changes
conn.commit()

# close the connection
conn.close()

*/

/*
USING SQLITE WITH JSON - FIRST LOAD THE LIBRARY...
    SELECT load_extension('libsqlite3_json.dylib');

THEN QUERY LIKE THIS...
    SELECT json_group_array(json_object('id', pages.id, 'title', pages.title, 'text', pages.text, 'ownerId', pages.ownerId, 'tags', (SELECT json_group_array(tags.name) FROM tags INNER JOIN page_tags ON tags.id = page_tags.tagId WHERE page_tags.pageId = pages.id))) as pages_json FROM pages;


AND INSERT LIKE THIS...
{
  "title": "My Page",
  "text": "This is my page.",
  "ownerId": 1,
  "tags": ["tag1", "tag2"]
}

WITH RECURSIVE tags(tag) AS (
  SELECT json_each.value FROM json_each(json_extract(json_data, '$.tags'))
),
tag_ids(id) AS (
  SELECT tags.tag_id FROM tags LEFT JOIN tags ON tags.tag = tags.name
),
page(id, title, text, ownerId) AS (
  SELECT NULL, json_extract(json_data, '$.title'), json_extract(json_data, '$.text'), json_extract(json_data, '$.ownerId')
  FROM (SELECT :json_data AS json_data)
)
INSERT INTO pages (id, title, text, ownerId)
SELECT page.id, page.title, page.text, page.ownerId
FROM page, tag_ids
LEFT JOIN page_tags ON page_tags.pageId = page.id AND page_tags.tagId = tag_ids.id
WHERE page_tags.pageId IS NULL;



*/

















