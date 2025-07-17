"""
New Order Tab Module
Implements the main POS interface for creating orders
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
from typing import Dict, List, Optional
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO
import logging
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class LazyImageLoader:
    """Handles lazy loading of product images from Unsplash"""
    
    def __init__(self):
        self.cache = {}
        self.loading_image = None
        self._create_loading_image()
    
    def _create_loading_image(self):
        """Create a placeholder loading image"""
        # Create a simple placeholder
        img = Image.new('RGB', (150, 150), color='#e9ecef')
        self.loading_image = ImageTk.PhotoImage(img)
    
    def load_image_async(self, url: str, callback, size=(150, 150)):
        """Load image asynchronously from URL"""
        if url in self.cache:
            callback(self.cache[url])
            return
        
        def load():
            try:
                response = requests.get(url, timeout=5)
                img = Image.open(BytesIO(response.content))
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.cache[url] = photo
                callback(photo)
            except Exception as e:
                logger.error(f"Failed to load image from {url}: {e}")
                callback(self.loading_image)
        
        threading.Thread(target=load, daemon=True).start()
    
    def get_loading_image(self):
        """Get the loading placeholder image"""
        return self.loading_image

class ProductCard:
    """Individual product card component"""
    
    def __init__(self, parent, product_data: Dict, image_loader: LazyImageLoader, on_add_callback):
        self.product_data = product_data
        self.image_loader = image_loader
        self.on_add_callback = on_add_callback
        self.photo = None
        
        self._create_card(parent)
        self._load_image()
    
    def _create_card(self, parent):
        """Create the product card UI"""
        self.frame = ttk_bs.Frame(parent, style="ProductCard.TFrame", padding=10)
        
        # Product image placeholder
        self.image_label = ttk_bs.Label(
            self.frame,
            image=self.image_loader.get_loading_image(),
            cursor="hand2"
        )
        self.image_label.pack(pady=(0, 10))
        self.image_label.bind("<Button-1>", self._on_click)
        
        # Product name
        name_label = ttk_bs.Label(
            self.frame,
            text=self.product_data['name'],
            font=('Segoe UI', 11, 'bold'),
            cursor="hand2"
        )
        name_label.pack()
        name_label.bind("<Button-1>", self._on_click)
        
        # Product price
        price_label = ttk_bs.Label(
            self.frame,
            text=f"${self.product_data['price']:.2f}",
            font=('Segoe UI', 10),
            bootstyle="success",
            cursor="hand2"
        )
        price_label.pack()
        price_label.bind("<Button-1>", self._on_click)
    
    def _load_image(self):
        """Load the product image"""
        def on_image_loaded(photo):
            self.photo = photo
            self.image_label.configure(image=photo)
        
        self.image_loader.load_image_async(
            self.product_data['image_url'],
            on_image_loaded
        )
    
    def _on_click(self, event=None):
        """Handle product card click"""
        self.on_add_callback(self.product_data)

class ScrollableProductGrid:
    """Scrollable grid for product cards with lazy loading"""
    
    def __init__(self, parent, image_loader: LazyImageLoader, on_add_callback):
        self.parent = parent
        self.image_loader = image_loader
        self.on_add_callback = on_add_callback
        self.products = []
        self.loaded_products = 0
        self.products_per_page = 6
        
        self._create_scrollable_frame()
        self._setup_lazy_loading()
    
    def _create_scrollable_frame(self):
        """Create scrollable frame for products"""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.parent, highlightthickness=0)
        self.scrollbar = ttk_bs.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk_bs.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel (Windows and Linux/Mac compatibility)
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling"""
            if event.delta:
                # Windows
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            else:
                # Linux/Mac
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
            self._check_load_more()
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", _on_mousewheel)    # Linux
        self.canvas.bind("<Button-5>", _on_mousewheel)    # Linux
        
        # Bind scroll events for lazy loading
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollbar.bind("<B1-Motion>", self._on_scroll)
    
    def _on_canvas_configure(self, event):
        """Handle canvas configuration changes"""
        self._check_load_more()
    
    def _on_scroll(self, event):
        """Handle scrollbar dragging"""
        self._check_load_more()
    
    def _setup_lazy_loading(self):
        """Setup lazy loading for products"""
        # Load initial products
        self._load_more_products()
    
    def _check_load_more(self):
        """Check if we need to load more products"""
        if self.loaded_products >= len(self.products):
            return
        
        # Check if we're near the bottom
        canvas_height = self.canvas.winfo_height()
        scroll_top = self.canvas.canvasy(0)
        scroll_bottom = scroll_top + canvas_height
        content_height = self.scrollable_frame.winfo_reqheight()
        
        if scroll_bottom > content_height * 0.8:  # 80% scrolled
            self._load_more_products()
    
    def _load_more_products(self):
        """Load more products into the grid"""
        if not self.products:
            return
        
        start_idx = self.loaded_products
        end_idx = min(start_idx + self.products_per_page, len(self.products))
        
        for i in range(start_idx, end_idx):
            product = self.products[i]
            
            # Calculate grid position
            row = self.loaded_products // 3
            col = self.loaded_products % 3
            
            # Create product card
            card = ProductCard(
                self.scrollable_frame,
                product,
                self.image_loader,
                self.on_add_callback
            )
            card.frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            self.loaded_products += 1
        
        # Configure grid weights
        for i in range(3):
            self.scrollable_frame.columnconfigure(i, weight=1)
    
    def set_products(self, products: List[Dict]):
        """Set the products to display"""
        self.products = products
        self.loaded_products = 0
        
        # Clear existing products
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Load initial batch
        self._load_more_products()

class NewOrderTab:
    """Main new order tab implementation"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.db = DatabaseManager()
        self.image_loader = LazyImageLoader()
        self.current_order = []
        self.order_number = 123
        self.current_category = "Coffee"
        
        self._create_interface()
        self._load_initial_data()
    
    def _create_interface(self):
        """Create the main interface"""
        self.main_frame = ttk_bs.Frame(self.parent)
        
        # Header
        self._create_header()
        
        # Main content area
        content_frame = ttk_bs.Frame(self.main_frame)
        content_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Left side - Products
        self._create_products_section(content_frame)
        
        # Right side - Order summary
        self._create_order_section(content_frame)
        
        return self.main_frame
    
    def _create_header(self):
        """Create the header section"""
        header_frame = ttk_bs.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Title
        title_label = ttk_bs.Label(
            header_frame,
            text="New Order",
            font=('Segoe UI', 24, 'bold')
        )
        title_label.pack(side=LEFT)
        
        # User info
        user_frame = ttk_bs.Frame(header_frame)
        user_frame.pack(side=RIGHT)
        
        user_label = ttk_bs.Label(
            user_frame,
            text=self.app.current_user["name"],
            font=('Segoe UI', 14)
        )
        user_label.pack(side=RIGHT, padx=(10, 0))
        
        avatar_label = ttk_bs.Label(
            user_frame,
            text="👤",
            font=('Arial', 20)
        )
        avatar_label.pack(side=RIGHT)
    
    def _create_products_section(self, parent):
        """Create the products section"""
        products_frame = ttk_bs.Frame(parent)
        products_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 20))
        
        # Search bar
        search_frame = ttk_bs.Frame(products_frame)
        search_frame.pack(fill=X, pady=(0, 20))
        
        search_entry = ttk_bs.Entry(
            search_frame,
            font=('Segoe UI', 11)
        )
        search_entry.pack(fill=X)
        
        # Add placeholder text manually
        search_entry.insert(0, "Search menu items")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, 'end') if search_entry.get() == "Search menu items" else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search menu items") if search_entry.get() == "" else None)
        
        # Category tabs
        self._create_category_tabs(products_frame)
        
        # Products grid
        products_container = ttk_bs.Frame(products_frame)
        products_container.pack(fill=BOTH, expand=True)
        
        self.product_grid = ScrollableProductGrid(
            products_container,
            self.image_loader,
            self._add_to_order
        )
    
    def _create_category_tabs(self, parent):
        """Create category tabs"""
        tab_frame = ttk_bs.Frame(parent)
        tab_frame.pack(fill=X, pady=(0, 20))
        
        categories = ["Coffee", "Tea", "Pastries", "Other"]
        
        for category in categories:
            btn = ttk_bs.Button(
                tab_frame,
                text=category,
                command=lambda c=category: self._switch_category(c),
                bootstyle="outline-primary" if category != self.current_category else "primary"
            )
            btn.pack(side=LEFT, padx=(0, 10))
    
    def _create_order_section(self, parent):
        """Create the order summary section"""
        order_frame = ttk_bs.Frame(parent, width=350)
        order_frame.pack(side=RIGHT, fill=Y)
        order_frame.pack_propagate(False)
        
        # Order header
        order_header = ttk_bs.Frame(order_frame)
        order_header.pack(fill=X, pady=(0, 20))
        
        order_title = ttk_bs.Label(
            order_header,
            text=f"Order #{self.order_number}",
            font=('Segoe UI', 18, 'bold')
        )
        order_title.pack()
        
        # Order items
        self.order_items_frame = ttk_bs.Frame(order_frame)
        self.order_items_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        # Order totals
        self._create_order_totals(order_frame)
        
        # Charge button
        charge_btn = ttk_bs.Button(
            order_frame,
            text="Charge",
            bootstyle="success",
            command=self._process_payment
        )
        charge_btn.pack(fill=X, pady=(10, 0))
    
    def _create_order_totals(self, parent):
        """Create order totals section"""
        totals_frame = ttk_bs.Frame(parent)
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
        
        ttk_bs.Label(
            total_frame,
            text="Total",
            font=('Segoe UI', 14, 'bold')
        ).pack(side=LEFT)
        
        self.total_label = ttk_bs.Label(
            total_frame,
            text="$0.00",
            font=('Segoe UI', 14, 'bold')
        )
        self.total_label.pack(side=RIGHT)
    
    def _load_initial_data(self):
        """Load initial product data"""
        products = self.db.get_products_by_category(self.current_category)
        self.product_grid.set_products(products)
        self._update_order_display()
    
    def _switch_category(self, category):
        """Switch product category"""
        self.current_category = category
        products = self.db.get_products_by_category(category)
        self.product_grid.set_products(products)
        
        # Update tab buttons (simplified - could be enhanced)
        logger.info(f"Switched to category: {category}")
    
    def _add_to_order(self, product):
        """Add product to current order"""
        # Check if product already in order
        for item in self.current_order:
            if item['product']['id'] == product['id']:
                item['quantity'] += 1
                break
        else:
            # Add new item
            self.current_order.append({
                'product': product,
                'quantity': 1,
                'customizations': []
            })
        
        self._update_order_display()
    
    def _update_order_display(self):
        """Update the order display"""
        # Clear current items
        for widget in self.order_items_frame.winfo_children():
            widget.destroy()
        
        # Add order items
        for item in self.current_order:
            self._create_order_item(item)
        
        # Update totals
        self._update_totals()
    
    def _create_order_item(self, item):
        """Create an order item widget"""
        item_frame = ttk_bs.Frame(self.order_items_frame, style="OrderItem.TFrame")
        item_frame.pack(fill=X, pady=2)
        
        # Quantity and name
        left_frame = ttk_bs.Frame(item_frame)
        left_frame.pack(side=LEFT, fill=X, expand=True)
        
        qty_name = ttk_bs.Label(
            left_frame,
            text=f"{item['quantity']}x {item['product']['name']}",
            font=('Segoe UI', 10, 'bold')
        )
        qty_name.pack(anchor=W)
        
        # Customizations (if any)
        if item.get('customizations'):
            custom_text = ", ".join([c['name'] for c in item['customizations']])
            custom_label = ttk_bs.Label(
                left_frame,
                text=custom_text,
                font=('Segoe UI', 9),
                foreground='gray'
            )
            custom_label.pack(anchor=W)
        
        # Price and remove button
        right_frame = ttk_bs.Frame(item_frame)
        right_frame.pack(side=RIGHT)
        
        price = item['product']['price'] * item['quantity']
        price_label = ttk_bs.Label(
            right_frame,
            text=f"${price:.2f}",
            font=('Segoe UI', 10)
        )
        price_label.pack(side=RIGHT, padx=(10, 0))
        
        remove_btn = ttk_bs.Button(
            right_frame,
            text="🗑",
            width=3,
            command=lambda: self._remove_from_order(item)
        )
        remove_btn.pack(side=RIGHT)
    
    def _remove_from_order(self, item):
        """Remove item from order"""
        self.current_order.remove(item)
        self._update_order_display()
    
    def _update_totals(self):
        """Update order totals"""
        subtotal = sum(item['product']['price'] * item['quantity'] for item in self.current_order)
        tax = subtotal * 0.08
        total = subtotal + tax
        
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.tax_label.configure(text=f"${tax:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
    
    def _process_payment(self):
        """Process the payment"""
        if not self.current_order:
            return
        
        # TODO: Implement payment processing
        logger.info("Processing payment...")
        
        # Clear order after successful payment
        self.current_order.clear()
        self.order_number += 1
        self._update_order_display()
    
    def pack(self, **kwargs):
        """Allow the tab to be packed"""
        return self.main_frame.pack(**kwargs)
