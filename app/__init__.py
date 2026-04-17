from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register blueprints here
    from app.routers import auth_bp, courses_bp, calendar_bp, forums_bp, assignments_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(courses_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(forums_bp)
    app.register_blueprint(assignments_bp)

    return app


