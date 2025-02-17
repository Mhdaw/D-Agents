from flask import Flask
#from app.config import Config  
#from app.routes import research_routes, financial_routes, news_routes, social_media_routes, study_routes

from app.routes.smolagents_routes import web_routes
def create_app(): #config_class=Config
    app = Flask(__name__)
    #app.config.from_object(config_class) # Load configuration from the class

    # Register Blueprints
    #app.register_blueprint(research_routes.research_bp)
    #app.register_blueprint(financial_routes.financial_bp)
    #app.register_blueprint(news_routes.news_bp)
    #app.register_blueprint(social_media_routes.social_media_bp)
    #app.register_blueprint(study_routes.study_bp)

    app.register_blueprint(web_routes.web_routes_bp)

    @app.route('/')
    def hello_world():
        return 'Hello, Agents Backend!'

    return app