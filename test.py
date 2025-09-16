import sqlite3

conn = sqlite3.connect('db.sqlite3')  # замени на имя своей базы, если другое
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(domains);")
for row in cursor.fetchall():
    print(row)
conn.close()