#from flask import Blueprint

#auth_bp = Blueprint('auth', __name__)
#courses_bp = Blueprint('courses', __name__)
#forums_bp = Blueprint('forums', __name__)
#calendar_bp = Blueprint('calendar', __name__)
#assignments_bp = Blueprint('assignments', __name__)

# Import the routes here for blueprints
from .auth import auth_bp
from .courses import courses_bp
from .forums import forums_bp
from .calendar import calendar_bp
from .assignments import assignments_bp
