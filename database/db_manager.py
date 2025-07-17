"""
Database Manager
Handles all database operations with SQLite backend
Includes dummy data generation with Unsplash images
"""

import sqlite3
import os
import logging
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations with dummy data"""
    
    def __init__(self, db_path: str = "coffee_pos.db"):
        self.db_path = db_path
        self._init_database()
        self._populate_dummy_data()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    is_available BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Product options table (for customizations)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_options (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    option_name TEXT NOT NULL,
                    option_value TEXT NOT NULL,
                    price_modifier REAL DEFAULT 0,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT UNIQUE,
                    phone TEXT,
                    loyalty_points INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    order_number TEXT UNIQUE NOT NULL,
                    subtotal REAL NOT NULL,
                    tax REAL NOT NULL,
                    total REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    status TEXT DEFAULT 'completed',
                    cashier_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            
            # Order items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    customizations TEXT,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            # Inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER UNIQUE,
                    current_stock INTEGER NOT NULL,
                    min_stock INTEGER DEFAULT 10,
                    max_stock INTEGER DEFAULT 100,
                    last_restocked TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _populate_dummy_data(self):
        """Populate database with dummy data if empty"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if we already have data
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] > 0:
                return
            
            logger.info("Populating database with dummy data...")
            
            # Coffee products with Unsplash images
            coffee_products = [
                {
                    "name": "Espresso",
                    "category": "Coffee",
                    "price": 2.50,
                    "description": "Rich and bold espresso shot",
                    "image_url": "https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=300&h=300&fit=crop"
                },
                {
                    "name": "Latte",
                    "category": "Coffee", 
                    "price": 3.50,
                    "description": "Smooth espresso with steamed milk",
                    "image_url": "https://images.unsplash.com/photo-1561882468-9110e03e0f78?w=300&h=300&fit=crop"
                },
                {
                    "name": "Cappuccino",
                    "category": "Coffee",
                    "price": 3.50,
                    "description": "Equal parts espresso, steamed milk, and foam",
                    "image_url": "https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=300&h=300&fit=crop"
                },
                {
                    "name": "Americano",
                    "category": "Coffee",
                    "price": 3.00,
                    "description": "Espresso diluted with hot water",
                    "image_url": "https://images.unsplash.com/photo-1459755486867-b55449bb39ff?w=300&h=300&fit=crop"
                },
                {
                    "name": "Mocha",
                    "category": "Coffee",
                    "price": 4.00,
                    "description": "Espresso with chocolate and steamed milk",
                    "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop"
                },
                {
                    "name": "Macchiato",
                    "category": "Coffee",
                    "price": 3.75,
                    "description": "Espresso with a dollop of steamed milk foam",
                    "image_url": "https://images.unsplash.com/photo-1485808191679-5760e28b2c20?w=300&h=300&fit=crop"
                }
            ]
            
            # Tea products
            tea_products = [
                {
                    "name": "Earl Grey",
                    "category": "Tea",
                    "price": 2.75,
                    "description": "Classic black tea with bergamot",
                    "image_url": "https://images.unsplash.com/photo-1597318499019-68eee882d346?w=300&h=300&fit=crop"
                },
                {
                    "name": "Green Tea",
                    "category": "Tea",
                    "price": 2.50,
                    "description": "Fresh and light green tea",
                    "image_url": "https://images.unsplash.com/photo-1556881286-fcdb26e34ac6?w=300&h=300&fit=crop"
                },
                {
                    "name": "Chamomile",
                    "category": "Tea",
                    "price": 2.50,
                    "description": "Soothing herbal tea",
                    "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop"
                },
                {
                    "name": "Chai Latte",
                    "category": "Tea",
                    "price": 3.25,
                    "description": "Spiced tea with steamed milk",
                    "image_url": "https://images.unsplash.com/photo-1578374173705-7d95a6f49cfc?w=300&h=300&fit=crop"
                }
            ]
            
            # Pastry products
            pastry_products = [
                {
                    "name": "Croissant",
                    "category": "Pastries",
                    "price": 2.00,
                    "description": "Buttery, flaky pastry",
                    "image_url": "https://images.unsplash.com/photo-1555507036-ab794f576c88?w=300&h=300&fit=crop"
                },
                {
                    "name": "Blueberry Muffin",
                    "category": "Pastries",
                    "price": 2.50,
                    "description": "Fresh baked muffin with blueberries",
                    "image_url": "https://images.unsplash.com/photo-1426869981800-95ebf51ce900?w=300&h=300&fit=crop"
                },
                {
                    "name": "Danish",
                    "category": "Pastries",
                    "price": 2.75,
                    "description": "Sweet pastry with fruit filling",
                    "image_url": "https://images.unsplash.com/photo-1509365390234-d2837de0711a?w=300&h=300&fit=crop"
                },
                {
                    "name": "Chocolate Chip Cookie",
                    "category": "Pastries",
                    "price": 1.50,
                    "description": "Homemade chocolate chip cookie",
                    "image_url": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=300&h=300&fit=crop"
                }
            ]
            
            # Other products
            other_products = [
                {
                    "name": "Orange Juice",
                    "category": "Other",
                    "price": 3.00,
                    "description": "Fresh squeezed orange juice",
                    "image_url": "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=300&h=300&fit=crop"
                },
                {
                    "name": "Bottled Water",
                    "category": "Other",
                    "price": 1.50,
                    "description": "Premium bottled water",
                    "image_url": "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=300&h=300&fit=crop"
                },
                {
                    "name": "Granola Bar",
                    "category": "Other",
                    "price": 2.25,
                    "description": "Healthy granola bar snack",
                    "image_url": "https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=300&h=300&fit=crop"
                }
            ]
            
            # Insert all products
            all_products = coffee_products + tea_products + pastry_products + other_products
            
            for product in all_products:
                cursor.execute("""
                    INSERT INTO products (name, category, price, description, image_url)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    product["name"],
                    product["category"], 
                    product["price"],
                    product["description"],
                    product["image_url"]
                ))
            
            # Add product options for customization
            product_options = [
                # Milk options for coffee/tea
                (1, "Milk Type", "Whole Milk", 0.0),
                (1, "Milk Type", "Almond Milk", 0.5),
                (1, "Milk Type", "Oat Milk", 0.6),
                (1, "Milk Type", "Soy Milk", 0.5),
                (1, "Size", "Small", 0.0),
                (1, "Size", "Medium", 0.5),
                (1, "Size", "Large", 1.0),
                # Add syrup options
                (2, "Syrup", "Vanilla", 0.5),
                (2, "Syrup", "Caramel", 0.5),
                (2, "Syrup", "Hazelnut", 0.5),
            ]
            
            for option in product_options:
                cursor.execute("""
                    INSERT INTO product_options (product_id, option_name, option_value, price_modifier)
                    VALUES (?, ?, ?, ?)
                """, option)
            
            # Add dummy customers
            customers = [
                ("John Smith", "john@email.com", "555-0101", 50),
                ("Jane Doe", "jane@email.com", "555-0102", 120),
                ("Bob Johnson", "bob@email.com", "555-0103", 30),
                ("Alice Brown", "alice@email.com", "555-0104", 80),
            ]
            
            for customer in customers:
                cursor.execute("""
                    INSERT INTO customers (name, email, phone, loyalty_points)
                    VALUES (?, ?, ?, ?)
                """, customer)
            
            # Add dummy users
            users = [
                ("admin", "admin123", "Administrator", "admin"),
                ("cashier1", "cash123", "John Cashier", "cashier"),
                ("manager1", "mgr123", "Jane Manager", "manager"),
            ]
            
            for user in users:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?)
                """, user)
            
            # Add inventory data
            cursor.execute("SELECT id FROM products")
            product_ids = [row[0] for row in cursor.fetchall()]
            
            for product_id in product_ids:
                stock = random.randint(15, 50)
                cursor.execute("""
                    INSERT INTO inventory (product_id, current_stock, min_stock, max_stock)
                    VALUES (?, ?, 10, 100)
                """, (product_id, stock))
            
            # Add some dummy orders
            self._generate_dummy_orders(cursor)
            
            conn.commit()
            logger.info("Dummy data populated successfully")
    
    def _generate_dummy_orders(self, cursor):
        """Generate dummy order history"""
        # Get product IDs and customer IDs
        cursor.execute("SELECT id, price FROM products")
        products = cursor.fetchall()
        
        cursor.execute("SELECT id FROM customers")
        customers = [row[0] for row in cursor.fetchall()]
        
        # Generate orders for the last 30 days
        start_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            order_date = start_date + timedelta(days=day)
            # Generate 5-15 orders per day
            daily_orders = random.randint(5, 15)
            
            for order_num in range(daily_orders):
                order_number = f"ORD{order_date.strftime('%Y%m%d')}{order_num:03d}"
                customer_id = random.choice(customers) if random.random() < 0.7 else None
                
                # Generate order items
                num_items = random.randint(1, 4)
                selected_products = random.sample(products, min(num_items, len(products)))
                
                subtotal = 0
                order_items = []
                
                for product_id, price in selected_products:
                    quantity = random.randint(1, 3)
                    item_total = price * quantity
                    subtotal += item_total
                    
                    order_items.append((product_id, quantity, price))
                
                tax = subtotal * 0.08
                total = subtotal + tax
                
                payment_methods = ["cash", "card", "mobile"]
                payment_method = random.choice(payment_methods)
                
                cashiers = ["Jane Doe", "John Cashier", "Alice Brown"]
                cashier = random.choice(cashiers)
                
                # Insert order
                cursor.execute("""
                    INSERT INTO orders (customer_id, order_number, subtotal, tax, total, 
                                      payment_method, cashier_name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (customer_id, order_number, subtotal, tax, total, 
                     payment_method, cashier, order_date))
                
                order_id = cursor.lastrowid
                
                # Insert order items
                for product_id, quantity, unit_price in order_items:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                        VALUES (?, ?, ?, ?)
                    """, (order_id, product_id, quantity, unit_price))
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get all products in a category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM products 
                WHERE category = ? AND is_available = 1
                ORDER BY name
            """, (category,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_product_options(self, product_id: int) -> List[Dict]:
        """Get customization options for a product"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM product_options 
                WHERE product_id = ?
                ORDER BY option_name, option_value
            """, (product_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def create_order(self, customer_id: Optional[int], order_items: List[Dict], 
                    payment_method: str, cashier_name: str) -> int:
        """Create a new order"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Calculate totals
            subtotal = sum(item['quantity'] * item['unit_price'] for item in order_items)
            tax = subtotal * 0.08
            total = subtotal + tax
            
            # Generate order number
            order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Insert order
            cursor.execute("""
                INSERT INTO orders (customer_id, order_number, subtotal, tax, total,
                                  payment_method, cashier_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, order_number, subtotal, tax, total,
                 payment_method, cashier_name))
            
            order_id = cursor.lastrowid
            
            # Insert order items
            for item in order_items:
                customizations = json.dumps(item.get('customizations', []))
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, customizations)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, item['product_id'], item['quantity'], 
                     item['unit_price'], customizations))
            
            conn.commit()
            return order_id
    
    def get_daily_sales(self, date: str) -> Dict:
        """Get sales data for a specific date"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as order_count,
                    SUM(total) as total_sales,
                    SUM(tax) as total_tax,
                    AVG(total) as avg_order_value
                FROM orders 
                WHERE DATE(created_at) = ?
            """, (date,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'order_count': row[0] or 0,
                    'total_sales': row[1] or 0,
                    'total_tax': row[2] or 0,
                    'avg_order_value': row[3] or 0
                }
            return {'order_count': 0, 'total_sales': 0, 'total_tax': 0, 'avg_order_value': 0}
    
    def get_low_stock_items(self) -> List[Dict]:
        """Get items with low stock"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.name, i.current_stock, i.min_stock
                FROM products p
                JOIN inventory i ON p.id = i.product_id
                WHERE i.current_stock <= i.min_stock
                ORDER BY i.current_stock
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
