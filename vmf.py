import sys
import dotenv
from utils import connect_vm


if __name__ == "__main__":
    dotenv.load_dotenv()
    url = None
    try:
        url = sys.argv[1]
    except IndexError:
        url = input("Enter url to fetch: ")
    connect_vm(url)
