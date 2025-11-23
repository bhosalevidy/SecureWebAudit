import sqlite3

# Connect to your existing database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Check if 'verified' column already exists
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]

if "verified" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN verified INTEGER DEFAULT 0")
    print("✅ 'verified' column added successfully!")
else:
    print("ℹ️ 'verified' column already exists.")

# Commit changes and close connection
conn.commit()
conn.close()
