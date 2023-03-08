
# Image RESTful API

## API for HexOcean recruitment process.
API for storing images and generating thumbnails.
##
Django: 4.1.7  
Django REST Framework: 3.14  
PostgreSQL: 15.2
##
This app was created using Docker containers.
To run it type "docker-compose up" in the command line.
##
During the first boot, there will be created an admin account and 3 tiers (Basic, Premium, Enterprise).  
Global caching is set to 15 seconds in settings file.
##
### Authorization required!
Token-based authentication with required prefix "Token"  
Name: Authorization  
In: header
##
### Available endpoints:
- **POST -> api/user/token/**
	 - Request body:
         - username (string)
         - password (string)
   - Response:
      - Status code: 200
      - Response body: {"token": "string"}

- **GET -> api/user/image/**
   - Response:
      - Status code: 200
      - Response body: [{"id": 0, "image": "string"}]
- **POST -> api/user/image/**
   - Request body: image (string ($binary))
   - Response:
      - Status code: 201
      - Response body: {"id": 0, "image": "string"}
- **GET -> api/user/image/{id}/**
	 - Request body:
         - id (integer (path))
   - Response:
      - Status code: 200
      - Response body: {"id": 0, "image": "string"}
- **DELETE -> api/user/image/{id}/**
   - Request body:
      - id (integer (path))
   - Response:
      - Status code: 204
      
- **GET -> api/user/thumbnail/**
   - Response:
      - Status code: 200
      - Response body: [{"id": 0, "image_id": 0, "height": 0, "thumbnail": "string"}]
- **GET -> api/user/thumbnail/{id}/**
	 - Request body:
         - id (integer (path))
   - Response:
      - Status code: 200
      - Response body: {"id": 0, "image_id": 0, "height": 0, "thumbnail": "string"}
- **DELETE -> api/user/thumbnail/{id}/**
	 - Request body:
       - id (integer (path))
   - Response:
      - Status code: 204
      
- **GET -> api/user/link/{id}/**
	 - Request body:
         - id (integer (path))
         - time (integer (query))
   - Response:
      - Status code: 200
      - Response body: {"url": "string", "expires_in": 0}
      
- **GET -> api/schema/**
	 - Request body:
         - id (string (query))
         - lang (string (query))
   - Response:
      - Status code: 200
