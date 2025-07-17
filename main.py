"""
Coffee Shop POS System - Fixed Version
Main application with simplified but functional implementation
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simplified database manager"""
    
    def __init__(self, db_path: str = "coffee_pos.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                is_available BOOLEAN DEFAULT 1
            )
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                subtotal REAL NOT NULL,
                tax REAL NOT NULL,
                total REAL NOT NULL,
                payment_method TEXT NOT NULL,
                cashier_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Check if we need to populate data
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            self._populate_dummy_data(cursor)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def _populate_dummy_data(self, cursor):
        """Populate with dummy data"""
        products = [
            ("Espresso", "Coffee", 2.50, "Rich and bold espresso shot"),
            ("Latte", "Coffee", 3.50, "Smooth espresso with steamed milk"),
            ("Cappuccino", "Coffee", 3.50, "Equal parts espresso, steamed milk, and foam"),
            ("Americano", "Coffee", 3.00, "Espresso diluted with hot water"),
            ("Mocha", "Coffee", 4.00, "Espresso with chocolate and steamed milk"),
            ("Macchiato", "Coffee", 3.75, "Espresso with a dollop of steamed milk foam"),
            ("Earl Grey", "Tea", 2.75, "Classic black tea with bergamot"),
            ("Green Tea", "Tea", 2.50, "Fresh and light green tea"),
            ("Chamomile", "Tea", 2.50, "Soothing herbal tea"),
            ("Chai Latte", "Tea", 3.25, "Spiced tea with steamed milk"),
            ("Croissant", "Pastries", 2.00, "Buttery, flaky pastry"),
            ("Blueberry Muffin", "Pastries", 2.50, "Fresh baked muffin with blueberries"),
            ("Danish", "Pastries", 2.75, "Sweet pastry with fruit filling"),
            ("Cookie", "Pastries", 1.50, "Homemade chocolate chip cookie"),
            ("Orange Juice", "Other", 3.00, "Fresh squeezed orange juice"),
            ("Water", "Other", 1.50, "Premium bottled water")
        ]
        
        cursor.executemany("""
            INSERT INTO products (name, category, price, description)
            VALUES (?, ?, ?, ?)
        """, products)
        
        logger.info("Dummy data populated successfully")
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if category == "All":
            cursor.execute("SELECT * FROM products WHERE is_available = 1 ORDER BY category, name")
        else:
            cursor.execute("SELECT * FROM products WHERE category = ? AND is_available = 1 ORDER BY name", (category,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def create_order(self, order_items: List[Dict], payment_method: str, cashier_name: str) -> int:
        """Create a new order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate totals
        subtotal = sum(item['quantity'] * item['unit_price'] for item in order_items)
        tax = subtotal * 0.08
        total = subtotal + tax
        
        # Generate order number
        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Insert order
        cursor.execute("""
            INSERT INTO orders (order_number, subtotal, tax, total, payment_method, cashier_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (order_number, subtotal, tax, total, payment_method, cashier_name))
        
        order_id = cursor.lastrowid
        
        # Insert order items
        for item in order_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item['product_id'], item['quantity'], item['unit_price']))
        
        conn.commit()
        conn.close()
        return order_id

class NewOrderPanel:
    """New Order Panel - Simplified implementation"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.db = DatabaseManager()
        self.current_order = []
        self.order_number = 123
        self.current_category = "Coffee"
        
        self.create_interface()
        self.load_products()
    
    def create_interface(self):
        """Create the interface"""
        self.main_frame = ttk_bs.Frame(self.parent)
        
        # Header
        header_frame = ttk_bs.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk_bs.Label(header_frame, text="New Order", font=('Segoe UI', 24, 'bold'))
        title_label.pack(side=LEFT)
        
        user_label = ttk_bs.Label(header_frame, text="Jane Doe", font=('Segoe UI', 14))
        user_label.pack(side=RIGHT)
        
        # Content area
        content_frame = ttk_bs.Frame(self.main_frame)
        content_frame.pack(fill=BOTH, expand=True)
        
        # Left side - Products
        self.create_products_section(content_frame)
        
        # Right side - Order
        self.create_order_section(content_frame)
        
        self.update_order_display()
    
    def create_products_section(self, parent):
        """Create products section"""
        products_frame = ttk_bs.LabelFrame(parent, text="Products", padding=10)
        products_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # Search bar
        search_frame = ttk_bs.Frame(products_frame)
        search_frame.pack(fill=X, pady=(0, 10))
        
        search_entry = ttk_bs.Entry(search_frame, font=('Segoe UI', 11))
        search_entry.pack(fill=X)
        search_entry.insert(0, "Search menu items")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, 'end') if search_entry.get() == "Search menu items" else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search menu items") if search_entry.get() == "" else None)
        
        # Category tabs
        category_frame = ttk_bs.Frame(products_frame)
        category_frame.pack(fill=X, pady=(0, 10))
        
        categories = ["Coffee", "Tea", "Pastries", "Other"]
        self.category_buttons = {}
        
        for category in categories:
            btn = ttk_bs.Button(
                category_frame,
                text=category,
                command=lambda c=category: self.switch_category(c),
                bootstyle="primary" if category == self.current_category else "outline-primary"
            )
            btn.pack(side=LEFT, padx=(0, 5))
            self.category_buttons[category] = btn
        
        # Products grid
        products_container = ttk_bs.Frame(products_frame)
        products_container.pack(fill=BOTH, expand=True)
        
        # Create scrollable frame
        canvas = tk.Canvas(products_container, highlightthickness=0)
        scrollbar = ttk_bs.Scrollbar(products_container, orient="vertical", command=canvas.yview)
        self.products_grid_frame = ttk_bs.Frame(canvas)
        
        self.products_grid_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.products_grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def create_order_section(self, parent):
        """Create order section"""
        order_frame = ttk_bs.LabelFrame(parent, text=f"Order #{self.order_number}", padding=10, width=350)
        order_frame.pack(side=RIGHT, fill=Y)
        order_frame.pack_propagate(False)
        
        # Order items
        self.order_items_frame = ttk_bs.Frame(order_frame)
        self.order_items_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        # Totals
        totals_frame = ttk_bs.Frame(order_frame)
        totals_frame.pack(fill=X, pady=(0, 10))
        
        # Subtotal
        subtotal_frame = ttk_bs.Frame(totals_frame)
        subtotal_frame.pack(fill=X)
        ttk_bs.Label(subtotal_frame, text="Subtotal").pack(side=LEFT)
        self.subtotal_label = ttk_bs.Label(subtotal_frame, text="$0.00")
        self.subtotal_label.pack(side=RIGHT)
        
        # Tax
        tax_frame = ttk_bs.Frame(totals_frame)
        tax_frame.pack(fill=X)
        ttk_bs.Label(tax_frame, text="Tax (8%)").pack(side=LEFT)
        self.tax_label = ttk_bs.Label(tax_frame, text="$0.00")
        self.tax_label.pack(side=RIGHT)
        
        # Total
        total_frame = ttk_bs.Frame(totals_frame)
        total_frame.pack(fill=X, pady=(10, 0))
        ttk_bs.Label(total_frame, text="Total", font=('Segoe UI', 14, 'bold')).pack(side=LEFT)
        self.total_label = ttk_bs.Label(total_frame, text="$0.00", font=('Segoe UI', 14, 'bold'))
        self.total_label.pack(side=RIGHT)
        
        # Buttons
        button_frame = ttk_bs.Frame(order_frame)
        button_frame.pack(fill=X)
        
        ttk_bs.Button(button_frame, text="Clear Order", command=self.clear_order, bootstyle="secondary").pack(fill=X, pady=(0, 5))
        ttk_bs.Button(button_frame, text="Charge", command=self.process_payment, bootstyle="success").pack(fill=X)
    
    def load_products(self):
        """Load products from database"""
        # Clear existing products
        for widget in self.products_grid_frame.winfo_children():
            widget.destroy()
        
        products = self.db.get_products_by_category(self.current_category)
        
        # Create product buttons in grid
        row = 0
        col = 0
        for product in products:
            product_frame = ttk_bs.Frame(self.products_grid_frame, style="ProductCard.TFrame", padding=10)
            product_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Product name
            name_label = ttk_bs.Label(product_frame, text=product['name'], font=('Segoe UI', 11, 'bold'), cursor="hand2")
            name_label.pack(pady=(0, 5))
            name_label.bind("<Button-1>", lambda e, p=product: self.add_to_order(p))
            
            # Product price
            price_label = ttk_bs.Label(product_frame, text=f"${product['price']:.2f}", font=('Segoe UI', 10), bootstyle="success", cursor="hand2")
            price_label.pack()
            price_label.bind("<Button-1>", lambda e, p=product: self.add_to_order(p))
            
            # Make frame clickable
            product_frame.bind("<Button-1>", lambda e, p=product: self.add_to_order(p))
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(3):
            self.products_grid_frame.columnconfigure(i, weight=1)
    
    def switch_category(self, category):
        """Switch product category"""
        self.current_category = category
        
        # Update button styles
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="outline-primary")
        
        self.load_products()
    
    def add_to_order(self, product):
        """Add product to order"""
        # Check if product already in order
        for item in self.current_order:
            if item['product']['id'] == product['id']:
                item['quantity'] += 1
                break
        else:
            # Add new item
            self.current_order.append({
                'product': product,
                'quantity': 1
            })
        
        self.update_order_display()
    
    def remove_from_order(self, product_id):
        """Remove product from order"""
        self.current_order = [item for item in self.current_order if item['product']['id'] != product_id]
        self.update_order_display()
    
    def update_order_display(self):
        """Update order display"""
        # Clear current items
        for widget in self.order_items_frame.winfo_children():
            widget.destroy()
        
        # Add order items
        for item in self.current_order:
            item_frame = ttk_bs.Frame(self.order_items_frame, padding=5)
            item_frame.pack(fill=X, pady=2)
            
            # Left side - quantity and name
            left_frame = ttk_bs.Frame(item_frame)
            left_frame.pack(side=LEFT, fill=X, expand=True)
            
            qty_name = ttk_bs.Label(
                left_frame,
                text=f"{item['quantity']}x {item['product']['name']}",
                font=('Segoe UI', 10, 'bold')
            )
            qty_name.pack(anchor=W)
            
            # Right side - price and remove button
            right_frame = ttk_bs.Frame(item_frame)
            right_frame.pack(side=RIGHT)
            
            price = item['product']['price'] * item['quantity']
            price_label = ttk_bs.Label(right_frame, text=f"${price:.2f}", font=('Segoe UI', 10))
            price_label.pack(side=RIGHT, padx=(10, 0))
            
            remove_btn = ttk_bs.Button(
                right_frame,
                text="×",
                width=3,
                command=lambda pid=item['product']['id']: self.remove_from_order(pid)
            )
            remove_btn.pack(side=RIGHT)
        
        # Update totals
        subtotal = sum(item['product']['price'] * item['quantity'] for item in self.current_order)
        tax = subtotal * 0.08
        total = subtotal + tax
        
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.tax_label.configure(text=f"${tax:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
    
    def clear_order(self):
        """Clear the current order"""
        self.current_order.clear()
        self.update_order_display()
    
    def process_payment(self):
        """Process payment"""
        if not self.current_order:
            return
        
        # Create order items for database
        order_items = []
        for item in self.current_order:
            order_items.append({
                'product_id': item['product']['id'],
                'quantity': item['quantity'],
                'unit_price': item['product']['price']
            })
        
        # Save to database
        order_id = self.db.create_order(order_items, "cash", "Jane Doe")
        
        # Show success message
        success_window = ttk_bs.Toplevel(self.parent)
        success_window.title("Payment Processed")
        success_window.geometry("300x150")
        success_window.transient(self.parent)
        success_window.grab_set()
        
        ttk_bs.Label(
            success_window,
            text="Payment Processed Successfully!",
            font=('Segoe UI', 14, 'bold')
        ).pack(expand=True)
        
        ttk_bs.Label(
            success_window,
            text=f"Order ID: {order_id}",
            font=('Segoe UI', 10)
        ).pack()
        
        ttk_bs.Button(
            success_window,
            text="OK",
            command=success_window.destroy
        ).pack(pady=10)
        
        # Clear order and increment order number
        self.clear_order()
        self.order_number += 1

class POSApplication:
    """Main POS Application - Simplified"""
    
    def __init__(self):
        self.root = ttk_bs.Window(themename="flatly")
        self.root.title("Coffee Shop POS")
        self.root.state('zoomed')
        
        self.current_tab = None
        self.create_interface()
    
    def create_interface(self):
        """Create main interface"""
        main_container = ttk_bs.Frame(self.root)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Content area
        self.content_frame = ttk_bs.Frame(main_container)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))
        
        # Load default tab
        self.load_tab("new_order")
    
    def create_sidebar(self, parent):
        """Create sidebar"""
        sidebar = ttk_bs.Frame(parent, width=60, style='secondary.TFrame')
        sidebar.pack(side=LEFT, fill=Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Logo
        logo_label = ttk_bs.Label(sidebar, text="☕", font=('Arial', 24))
        logo_label.pack(pady=20)
        
        # Navigation buttons
        nav_buttons = [
            ("📋", "New Order", "new_order"),
            ("📊", "Analytics", "analytics"),
            ("📝", "Orders", "orders"),
            ("⚙️", "Settings", "settings")
        ]
        
        for icon, tooltip, tab_name in nav_buttons:
            btn = ttk_bs.Button(
                sidebar,
                text=icon,
                command=lambda t=tab_name: self.load_tab(t),
                width=6
            )
            btn.pack(fill=X, pady=2)
        
        # User info
        user_frame = ttk_bs.Frame(sidebar)
        user_frame.pack(side=BOTTOM, fill=X, pady=10)
        
        ttk_bs.Label(user_frame, text="👤", font=('Arial', 16)).pack()
        ttk_bs.Label(user_frame, text="Jane Doe", font=('Segoe UI', 8), wraplength=50).pack()
    
    def load_tab(self, tab_name):
        """Load tab content"""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if tab_name == "new_order":
            panel = NewOrderPanel(self.content_frame, self)
            panel.main_frame.pack(fill=BOTH, expand=True)
        else:
            # Placeholder for other tabs
            placeholder = ttk_bs.Label(
                self.content_frame,
                text=f"{tab_name.replace('_', ' ').title()} - Coming Soon",
                font=('Segoe UI', 18, 'bold')
            )
            placeholder.pack(expand=True)
        
        self.current_tab = tab_name
    
    def run(self):
        """Run the application"""
        logger.info("Starting Coffee Shop POS Application")
        self.root.mainloop()

def main():
    """Main entry point"""
    app = POSApplication()
    app.run()

if __name__ == "__main__":
    main()
