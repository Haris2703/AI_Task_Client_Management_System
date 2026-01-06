import sqlite3


def create_db():
    # Database connection
    conn = sqlite3.connect('management.db')
    c = conn.cursor()

    # Tasks Table (Note: AUTOINCREMENT is one word in SQLite,
    # but simple INTEGER PRIMARY KEY also works automatically)
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, 
                  description TEXT, 
                  priority TEXT, 
                  status TEXT DEFAULT 'Pending')''')

    # Clients Table
    c.execute('''CREATE TABLE IF NOT EXISTS clients 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  email TEXT, 
                  project TEXT)''')

    conn.commit()
    conn.close()
    print("✅ Database and Tables created successfully!")


if __name__ == "__main__":
    create_db()
