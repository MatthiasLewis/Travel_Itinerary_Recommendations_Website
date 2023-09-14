from flask_restful import Api
from main import Travel,app
from flask_jwt_extended import JWTManager
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_cors import CORS

CORS(app)
api = Api(app)

app.config["DEBUG"] = True
app.config["JWT_SECRET_KEY"] = "secret_key" #JWT token setting

# Swagger setting
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Awesome Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        securityDefinitions={
            "bearer": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
            }
        },
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

api.add_resource(Travel, "/Travel", methods=["get","post"])
docs.register(Travel)

if __name__ == '__main__':
    # jwt = JWTManager().init_app(app)
    app.run(host="127.0.0.1",port=5000,debug=True)
