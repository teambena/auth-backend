from flask import make_response
from app import config
import logging


class HttpError():
    status_code = 500
    def __init__(self, message, status_code=None, payload=None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['code'] = self.status_code
        rv['message'] = self.message
        return rv
    
    def abort(self):
        # return jsonify(self.to_dict()), self.status_code
        return make_response(str(self.message)), self.status_code


def BadRequest(message = "Bad Request"):
    return HttpError(message, 400).abort()

def Unauthorized(message = "Unauthorized"):
    return HttpError(message, 401).abort()

def AccessForbidden(message = "Access forbidden"):
    return HttpError(message, 403).abort()

def ResourceNotFound(message = "Page or record not found"):
    return HttpError(message, 404).abort()

def InternalServerError(ex = "Internal server error"):
    print("\n===================== Exception StackTrace =====================")
    logging.exception(ex, exc_info=True) 
    print("===================== End of Exception StackTrace =====================\n")
    message = str(ex)
    if not config.DEBUG:
        message = "Error processing request..."
    return HttpError(message, 500).abort()
