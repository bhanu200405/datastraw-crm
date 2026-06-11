import sqlite3

def setup_database():
    # Connect to a local file named 'crm.db' (it will create it if it doesn't exist)
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Execute the SQL script to create the tickets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'Open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Save the changes and close the connection
    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()