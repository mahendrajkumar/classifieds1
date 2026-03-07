import duckdb
import os

DB_FILE = "classifieds.db"

def get_db():
    conn = duckdb.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = duckdb.connect(DB_FILE)
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS listing_id_seq START 1;
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER DEFAULT nextval('listing_id_seq'),
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            category VARCHAR NOT NULL,
            location VARCHAR,
            image_url VARCHAR,
            contact_email VARCHAR NOT NULL,
            contact_phone VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        );
    """)
    # Insert some dummy data if empty
    res = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    if res == 0:
        conn.execute("""
            INSERT INTO listings (title, description, price, category, location, image_url, contact_email)
            VALUES 
            ('MacBook Pro M2', 'Barely used MacBook Pro M2, 16GB RAM, 512GB SSD.', 1200.00, 'Electronics', 'San Francisco, CA', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=600&auto=format&fit=crop', 'seller1@example.com'),
            ('Trek Mountain Bike', 'Good condition mountain bike, 21 gears. Minor scratches.', 150.00, 'Vehicles', 'Denver, CO', 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?q=80&w=600&auto=format&fit=crop', 'seller2@example.com'),
            ('Downtown 1-Bedroom Apartment', 'Spacious apartment downtown with great views and balcony. Pet friendly.', 1500.00, 'Real Estate', 'Austin, TX', 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=600&auto=format&fit=crop', 'seller3@example.com'),
            ('Professional Web Development', 'I will build a modern, responsive website for your business. FastAPI, NextJS, etc.', 500.00, 'Services', 'Remote', 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?q=80&w=600&auto=format&fit=crop', 'dev@example.com')
        """)
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
