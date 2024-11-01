from db_utils import count_meteors, count_meteors_last_24, count_satellites
from db_utils import custom_query

def display_menu():
    while True:
        print("\n==== Satellite Tracker Menu ====")
        print("1. Total satellites detected")
        print("2. Satellites detected in the last 24 hours")
        print("3. Total meteors detected")
        print("4. Meteors detected in the last 24 hours")
        print("5. Custom SQL query")
        print("6. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            total, _ = count_satellites()
            print(f"Total satellites detected: {total}")
        elif choice == '2':
            _, last_24 = count_satellites()
            print(f"Satellites detected in the last 24 hours: {last_24}")
        elif choice == '3':
            total_meteors = count_meteors()
            print(f"Total meteors detected: {total_meteors}")
        elif choice == '4':
            last_24_meteors = count_meteors_last_24()
            print(f"Meteors detected in the last 24 hours: {last_24_meteors}")
        elif choice == '5':
            custom_query()
        elif choice == '6':
            break
        else:
            print("Invalid option. Please try again.")
