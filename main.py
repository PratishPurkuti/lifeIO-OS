from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    # Explicitly set template and static folders
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, 'app', 'templates')
    static_dir = os.path.join(base_dir, 'app', 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    
    # Extensions
    CORS(app)

    # Blueprints
    from app.routes.base_routes import base_bp
    from app.routes.auth_routes import auth_bp
    
    from app.routes.activity_routes import activity_bp
    
    from app.routes.sleep_routes import sleep_bp
    from app.routes.finance_routes import finance_bp
    from app.routes.stats_routes import stats_bp
    
    app.register_blueprint(base_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(sleep_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(stats_bp)






    return app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )

