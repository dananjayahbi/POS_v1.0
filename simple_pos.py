"""
Simplified POS Application for testing
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import sqlite3
import os
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class SimplePOSApp:
    """Simplified POS Application"""
    
    def __init__(self):
        self.root = ttk_bs.Window(themename="flatly")
        self.root.title("Coffee Shop POS - Simple Version")
        self.root.state('zoomed')
        
        # Create database
        self.init_database()
        
        # Create UI
        self.create_ui()
    
    def init_database(self):
        """Initialize simple database"""
        conn = sqlite3.connect("simple_pos.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                price REAL
            )
        """)
        
        # Insert sample data if empty
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            products = [
                ("Espresso", "Coffee", 2.50),
                ("Latte", "Coffee", 3.50),
                ("Cappuccino", "Coffee", 3.50),
                ("Americano", "Coffee", 3.00),
                ("Earl Grey", "Tea", 2.75),
                ("Green Tea", "Tea", 2.50),
                ("Croissant", "Pastries", 2.00),
                ("Muffin", "Pastries", 2.50)
            ]
            
            cursor.executemany(
                "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
                products
            )
        
        conn.commit()
        conn.close()
    
    def create_ui(self):
        """Create the user interface"""
        main_frame = ttk_bs.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header = ttk_bs.Label(
            main_frame,
            text="Coffee Shop POS",
            font=('Segoe UI', 24, 'bold')
        )
        header.pack(pady=(0, 20))
        
        # Content area
        content_frame = ttk_bs.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True)
        
        # Left side - Products
        self.create_products_section(content_frame)
        
        # Right side - Order
        self.create_order_section(content_frame)
        
        # Initialize order
        self.current_order = []
        self.update_order_display()
    
    def create_products_section(self, parent):
        """Create products section"""
        products_frame = ttk_bs.LabelFrame(parent, text="Products", padding=10)
        products_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # Category buttons
        category_frame = ttk_bs.Frame(products_frame)
        category_frame.pack(fill=X, pady=(0, 10))
        
        categories = ["All", "Coffee", "Tea", "Pastries"]
        for category in categories:
            btn = ttk_bs.Button(
                category_frame,
                text=category,
                command=lambda c=category: self.filter_products(c)
            )
            btn.pack(side=LEFT, padx=(0, 5))
        
        # Products grid
        self.products_frame = ttk_bs.Frame(products_frame)
        self.products_frame.pack(fill=BOTH, expand=True)
        
        self.load_products()
    
    def create_order_section(self, parent):
        """Create order section"""
        order_frame = ttk_bs.LabelFrame(parent, text="Current Order", padding=10, width=300)
        order_frame.pack(side=RIGHT, fill=Y)
        order_frame.pack_propagate(False)
        
        # Order items
        self.order_items_frame = ttk_bs.Frame(order_frame)
        self.order_items_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Totals
        totals_frame = ttk_bs.Frame(order_frame)
        totals_frame.pack(fill=X, pady=(0, 10))
        
        ttk_bs.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky=W)
        self.subtotal_label = ttk_bs.Label(totals_frame, text="$0.00")
        self.subtotal_label.grid(row=0, column=1, sticky=E)
        
        ttk_bs.Label(totals_frame, text="Tax (8%):").grid(row=1, column=0, sticky=W)
        self.tax_label = ttk_bs.Label(totals_frame, text="$0.00")
        self.tax_label.grid(row=1, column=1, sticky=E)
        
        ttk_bs.Label(totals_frame, text="Total:", font=('Segoe UI', 11, 'bold')).grid(row=2, column=0, sticky=W)
        self.total_label = ttk_bs.Label(totals_frame, text="$0.00", font=('Segoe UI', 11, 'bold'))
        self.total_label.grid(row=2, column=1, sticky=E)
        
        totals_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk_bs.Frame(order_frame)
        button_frame.pack(fill=X)
        
        ttk_bs.Button(
            button_frame,
            text="Clear Order",
            command=self.clear_order,
            bootstyle="secondary"
        ).pack(fill=X, pady=(0, 5))
        
        ttk_bs.Button(
            button_frame,
            text="Process Payment",
            command=self.process_payment,
            bootstyle="success"
        ).pack(fill=X)
    
    def load_products(self, category="All"):
        """Load products from database"""
        # Clear existing products
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        conn = sqlite3.connect("simple_pos.db")
        cursor = conn.cursor()
        
        if category == "All":
            cursor.execute("SELECT * FROM products ORDER BY category, name")
        else:
            cursor.execute("SELECT * FROM products WHERE category = ? ORDER BY name", (category,))
        
        products = cursor.fetchall()
        conn.close()
        
        # Create product buttons in grid
        row = 0
        col = 0
        for product_id, name, category, price in products:
            btn = ttk_bs.Button(
                self.products_frame,
                text=f"{name}\n${price:.2f}",
                command=lambda p=(product_id, name, price): self.add_to_order(p),
                width=15
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(3):
            self.products_frame.columnconfigure(i, weight=1)
    
    def filter_products(self, category):
        """Filter products by category"""
        self.load_products(category)
    
    def add_to_order(self, product):
        """Add product to order"""
        product_id, name, price = product
        
        # Check if item already in order
        for item in self.current_order:
            if item['id'] == product_id:
                item['quantity'] += 1
                break
        else:
            # Add new item
            self.current_order.append({
                'id': product_id,
                'name': name,
                'price': price,
                'quantity': 1
            })
        
        self.update_order_display()
    
    def remove_from_order(self, product_id):
        """Remove product from order"""
        self.current_order = [item for item in self.current_order if item['id'] != product_id]
        self.update_order_display()
    
    def update_order_display(self):
        """Update the order display"""
        # Clear current display
        for widget in self.order_items_frame.winfo_children():
            widget.destroy()
        
        # Add order items
        for item in self.current_order:
            item_frame = ttk_bs.Frame(self.order_items_frame)
            item_frame.pack(fill=X, pady=2)
            
            # Item info
            info_text = f"{item['quantity']}x {item['name']}"
            ttk_bs.Label(item_frame, text=info_text).pack(side=LEFT)
            
            # Price
            item_total = item['price'] * item['quantity']
            ttk_bs.Label(item_frame, text=f"${item_total:.2f}").pack(side=RIGHT)
            
            # Remove button
            ttk_bs.Button(
                item_frame,
                text="×",
                width=3,
                command=lambda pid=item['id']: self.remove_from_order(pid)
            ).pack(side=RIGHT, padx=(5, 0))
        
        # Update totals
        subtotal = sum(item['price'] * item['quantity'] for item in self.current_order)
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
        """Process the payment"""
        if not self.current_order:
            return
        
        # Simple success message
        success_window = ttk_bs.Toplevel(self.root)
        success_window.title("Payment Processed")
        success_window.geometry("300x150")
        
        ttk_bs.Label(
            success_window,
            text="Payment Processed Successfully!",
            font=('Segoe UI', 14, 'bold')
        ).pack(expand=True)
        
        ttk_bs.Button(
            success_window,
            text="OK",
            command=success_window.destroy
        ).pack(pady=10)
        
        # Clear order
        self.clear_order()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimplePOSApp()
    app.run()
