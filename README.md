# Coffee Shop POS System

A modern Point of Sale (POS) system built with Python, Tkinter, and ttkbootstrap, designed specifically for coffee shops.

## Features

- **Modern UI**: Clean, responsive interface using ttkbootstrap
- **Lazy Loading**: Efficient loading of images, data, and UI components
- **Product Management**: Categorized products with customization options
- **Order Management**: Easy order creation, modification, and processing
- **Payment Processing**: Support for multiple payment methods
- **Real-time Updates**: Live order totals and inventory tracking
- **Dummy Data**: Pre-populated with coffee shop products and sample data

## Screenshots

The application features a modern design with:
- Sidebar navigation
- Product grid with images
- Order summary panel
- Real-time calculations

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd POS_v1.0
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python start_pos.py
   ```
   
   Or run specific versions directly:
   - `python simple_pos.py` - Basic functionality
   - `python main_fixed.py` - Stable version with core features
   - `python main.py` - Advanced version (may have issues)

## Current Status

✅ **Completed Features:**
- Modern UI with ttkbootstrap
- Product categories (Coffee, Tea, Pastries, Other)
- Product selection and ordering
- Order management (add/remove items)
- Real-time order calculations (subtotal, tax, total)
- Basic payment processing
- SQLite database with dummy data
- Order history storage

🚧 **In Progress:**
- Custom product options (sizes, milk types)
- Multiple payment methods
- Receipt generation
- Inventory management

📋 **Planned:**
- User authentication
- Sales reporting
- Loyalty programs
- Advanced features

## Requirements

- Python 3.8 or higher
- tkinter (usually comes with Python)
- ttkbootstrap
- Pillow (PIL)
- requests
- sqlite3 (built-in)

## Project Structure

```
POS_v1.0/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── modules/
│   ├── __init__.py
│   └── new_order_tab.py   # New order interface
├── database/
│   ├── __init__.py
│   └── db_manager.py      # Database operations
├── coffee_pos.db          # SQLite database (created automatically)
└── README.md
```

## Usage

1. **Start the application**: Run `python main.py`
2. **Navigate**: Use the sidebar icons to switch between different sections
3. **Create orders**: Click on products to add them to the current order
4. **Customize items**: Select product options like milk type, size, etc.
5. **Process payment**: Click "Charge" to complete the order

## Database

The application uses SQLite for data storage with the following main tables:
- `products` - Product catalog
- `orders` - Order history
- `order_items` - Individual order items
- `customers` - Customer information
- `inventory` - Stock management
- `users` - Staff accounts

## Lazy Loading Features

- **Images**: Product images are loaded asynchronously from Unsplash
- **UI Components**: Tabs and panels are loaded only when accessed
- **Data**: Product lists support infinite scroll with pagination
- **Modules**: Python modules are imported only when needed

## Customization

### Adding Products
Products can be added by modifying the dummy data in `database/db_manager.py` or through the admin interface.

### Changing Themes
The application uses ttkbootstrap themes. You can change the theme by modifying the `themename` parameter in `main.py`.

### Custom Product Images
Replace Unsplash URLs in the database with your own product images.

## Development

### Adding New Features
1. Create new modules in the `modules/` directory
2. Add database tables in `db_manager.py`
3. Register new tabs in the main application

### Testing
- Dummy data is automatically generated for testing
- The application includes sample orders, customers, and inventory

## Troubleshooting

**Images not loading**: Check internet connection for Unsplash images
**Database errors**: Delete `coffee_pos.db` to regenerate with fresh dummy data
**Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

## Future Enhancements

- Receipt printing
- Barcode scanning
- Advanced reporting
- Multi-location support
- Cloud synchronization
- Customer loyalty programs

## License

This project is created for educational and commercial use.