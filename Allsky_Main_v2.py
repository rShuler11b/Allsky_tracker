from db_utils import init_db
from menu import display_menu
from server import start_flask_server
import cv2

if __name__ == '__main__':
    init_db()
    start_flask_server()
    display_menu()
