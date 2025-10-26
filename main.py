def main():
    print("=" * 50)
    print("Welcome to the App!")
    print("=" * 50)
    print("\nPlease select an option:")
    print("1. View Data")
    print("2. Add New Entry")
    print("3. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            print("\n📊 Viewing data...")
            # Add your data viewing logic here
            break
        elif choice == "2":
            print("\n➕ Adding new entry...")
            # Add your entry logic here
            break
        elif choice == "3":
            print("\n👋 Thanks for using the app. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.\n")

if __name__ == "__main__":
    main()
