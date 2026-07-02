import sqlite3
import pandas as pd
import os



DB_NAME = "insights.db"

def setup_database():
    print("Initializing SQLite database...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("Loading Chinook database...")
    if os.path.exists("Chinook.db"):
        cursor.execute("ATTACH DATABASE 'Chinook.db' AS chinook;")

        cursor.execute("""
            SELECT name
            FROM chinook.sqlite_master
            WHERE type='table';
        """)
        tables = cursor.fetchall()

        for (table_name,) in tables:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name}
                AS SELECT * FROM chinook.{table_name};
            """)

        cursor.execute("DETACH DATABASE chinook;")

        print("✔ Chinook database imported successfully.")
    else:
        print("❌ Chinook.db not found.")
    


    print("Creating custom Transport Dataset...")
    cursor.execute ("""
    CREATE TABLE IF NOT EXISTS transport_logistics (
        shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT,
        destination TEXT,
        vehicle_type TEXT,
        distance_km REAL,
        travel_time_hours REAL,
        fuel_consumed_liters REAL,
        status TEXT
    )""")

    mock_transport = [
       ('Mumbai', 'Vadodara', 'Truck', 420.5, 8.5, 110.0, 'Delivered'),
        ('Surat', 'Ahmedabad', 'Tempo', 260.0, 5.0, 45.5, 'Delivered'),
        ('Vadodara', 'Surat', 'Truck', 150.2, 3.2, 38.0, 'In Transit'),
        ('Ahmedabad', 'Mumbai', 'Container', 530.0, 11.5, 160.0, 'Delayed'),
        ('Vapi', 'Vadodara', 'Truck', 240.8, 4.8, 62.0, 'Delivered') 
    ]
    cursor.executemany("""
        INSERT INTO transport_logistics (origin, destination, vehicle_type, distance_km, travel_time_hours, fuel_consumed_liters, status)
        VALUES (?, ?, ?, ?, ?, ?, ?) 
    """, mock_transport)
    print("Transport dataset created")

    print("Creating custom CSV Dataset...")
    csv_data = {
        'product_id': [101, 102, 103, 104, 105],
        'product_name': ['Wireless Mouse', 'Mechanical Keyboard', 'Type-C Hub', '4K Monitor', 'Studio Headphones'],
        'category': ['Electronics', 'Electronics', 'Accessories', 'Displays', 'Audio'],
        'price': [25.00, 85.50, 40.00, 320.00, 150.00],
        'stock_quantity': [120, 45, 200, 15, 30]
    }
    df_products = pd.DataFrame(csv_data)

    df_products.to_sql('Inventory_products', conn, if_exists='replace', index=False)
    print("CSV dataset created")

    conn.commit()
    conn.close()
    print("Database setup completed successfully.")

if __name__ == "__main__":
    setup_database()

