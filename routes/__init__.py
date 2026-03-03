from .auth import auth_bp
from .devices import devices_bp
from .physical import physical_bp
from .stats import stats_bp
from .check import check_bp
from .department import department_bp


def register_blueprints(app):
    """注册所有蓝图"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(physical_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(check_bp)
    app.register_blueprint(department_bp)
