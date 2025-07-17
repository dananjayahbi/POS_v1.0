"""
Startup script for Coffee Shop POS System
Choose between simple and full version
"""

import os
import sys

def main():
    print("Coffee Shop POS System")
    print("=" * 40)
    print("1. Simple POS (Basic functionality)")
    print("2. Full POS (Advanced features - may have issues)")
    print("3. Fixed POS (Stable version with core features)")
    print("4. Exit")
    print()
    
    choice = input("Select version to run (1-4): ").strip()
    
    if choice == "1":
        print("Starting Simple POS...")
        os.system("python simple_pos.py")
    elif choice == "2":
        print("Starting Full POS...")
        os.system("python main.py")
    elif choice == "3":
        print("Starting Fixed POS...")
        os.system("python main_fixed.py")
    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()
