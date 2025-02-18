# # run.py
# from app import create_app
# import os

# app = create_app()

# if __name__ == '__main__':
#     port = int(os.environ.get('FLASK_RUN_PORT', 8080))
#     # Remove debug mode for production
#     app.run(host='0.0.0.0', port=port, debug=False)
# run.py
from app import create_app  # Import your application factory

app = create_app()  # Create the application instance