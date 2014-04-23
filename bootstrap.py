# Run app
if __name__ == "__main__":
    from app import app
    app.run(port=app.config['PORT'])

