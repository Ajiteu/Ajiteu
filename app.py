"""로컬 실행: python app.py"""

from ajiteu import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
