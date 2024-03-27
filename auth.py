"""Handles Token authentication for private endpoints
"""

# import os
import jwt
import json
from datetime import datetime
from fastapi import Request


# Denied Log
with open("denied.json") as fd:
    denied = json.load(fd)

def set_up():
    """Sets up configuration for the app"""

    with open("config.json", "r") as f:
        config = json.load(f)

    return config["AUTH0"]

def log_denied_request(request: Request, endpoint_name: str):
    """request: Request\n
    endpoint_name: str"""
    print("Hello from `log_denied_request`")
    # Log who sends the request
    ip = request.client.host
    denied.append(
        {
            "Request": endpoint_name,
            "ip": ip,
            "time": str(datetime.now()),
            "headers": dict(request.headers),
            "method": request.method,
            "url": str(request.url),
            "cookies": request.cookies
        }
)
    with open("denied.json", "a") as json_file:
        json.dump(denied, json_file, indent=4, separators=(",", ": "))

    print("Wrote to denied.json")

class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token
        self.config = set_up()

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return payload

