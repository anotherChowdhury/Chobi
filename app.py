from myappmain import app
from views import *

if __name__ == '__main__':
    app.run()























from functools import wraps

import jwt
from flask import request, make_response, jsonify


#########token functions###################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return make_response(jsonify({
                "msg": "Token is Missing"
            }), 404)

        try:
            data = jwt.decode(token, 'topSecret')
            print(data)
        except:
            return make_response(jsonify({
                "msg": "Token is Invalid"
            }), 403)
        return f(*args, **kwargs)

    return decorated









