from datetime import timedelta
import os

import certifi
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from BlockList import BlockList
from db import mongo
from resources.TravelPlan import blp as TravelPlanBlueprint
from resources.user import blp as UserBlueprint
from resources.place import blp as PlaceBlueprint
from resources.stop import blp as StopBlueprint
from resources.day import blp as DayBlueprint
from resources.transportation import blp as TransportationBlueprint
from resources.chatbot import blp as ChatbotBlueprint
from urllib.parse import quote_plus


# Load environment variables from .env file
load_dotenv()


app = Flask(__name__)


# Configure the app with environment variables
mongo_uri = os.getenv("MONGODB_URI")
app.config["MONGODB_HOST"] = f"{mongo_uri}?tlsCAFile={quote_plus(certifi.where())}"


app.config["API_TITLE"] = "Travel test API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_JSON_PATH"] = "api-spec.json"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False



# Initialize MongoDB
mongo.init_app(app)
# Initialize JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key")

jwt = JWTManager(app)


# Define a callback function to check if the token is in the blocklist
@jwt.token_in_blocklist_loader
def check_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in BlockList


# Initialize API and register blueprints
api = Api(app)

# Configure API with JWT authentication
api.spec.components.security_scheme(
    "BearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
)
api.spec.options["security"] = [{"BearerAuth": []}]

api.register_blueprint(UserBlueprint)
api.register_blueprint(PlaceBlueprint)
api.register_blueprint(StopBlueprint)
api.register_blueprint(TransportationBlueprint)
api.register_blueprint(DayBlueprint)
api.register_blueprint(TravelPlanBlueprint)
api.register_blueprint(ChatbotBlueprint)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
