from frontend.website import website
from backend.database import create_db

if __name__ == "__main__":
    create_db()
    website.run(debug=True)

