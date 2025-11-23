import sqlite3

# Connect to your database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Add 'verified' column
cursor.execute("ALTER TABLE users ADD COLUMN verified INTEGER DEFAULT 0;")

conn.commit()
conn.close()

print("Column 'verified' added successfully!")
