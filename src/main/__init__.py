from flask import Flask
from .config.settings import Config
from .domain.models import db

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # Tự động tạo bảng vào MySQL
        db.create_all()
        print("--- Database Connected & Tables Created ---")

    # Đăng ký các Controller (Blueprints) tại đây
    # from .controllers.auth_controller import auth_bp
    # app.register_blueprint(auth_bp)

    return app