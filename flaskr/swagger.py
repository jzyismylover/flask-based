from flasgger import Swagger

swagger_config = Swagger.DEFAULT_CONFIG
swagger_config['title'] = 'flasgger swagger api'
swagger_config['description'] = 'based on flask, used in blog management'
swagger_config['host'] = 'localhost:5000'

def init_swagger(app):
  Swagger(app, config=swagger_config)