from src.database import Database
from src.ui import ParkingUI

def main():
    # Initialize database
    database = Database()

    # Initialize UI and start the application
    app = ParkingUI(database)
    app.run()

if __name__ == "__main__":
    main()