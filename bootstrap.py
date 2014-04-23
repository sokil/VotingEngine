from app import app

# Run app
if __name__ == "__main__":
    app.run(port=app.config['PORT'])

