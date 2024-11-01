from db_utils import init_db
from menu import display_menu
from Flask_server import start_flask_server
import cv2

if __name__ == '__main__':
    init_db()
    start_flask_server()
    display_menu()
