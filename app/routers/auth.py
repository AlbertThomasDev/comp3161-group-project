from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# @auth_bp.route("/login", methods=['POST'])
@auth_bp.route("/login")
def login():
    print("\nOn login page") 
    return "<h1>Success</h1><p>This sis the login page</p>"

@auth_bp.route("/register", methods=['POST'])
def register():
    pass

