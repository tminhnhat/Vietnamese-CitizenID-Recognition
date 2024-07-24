from django.conf import settings
import jwt,json

def decode(token):
    if(token == None or token == ""):
        raise Exception("Bạn cần phải đăng nhập để thao tác")
    try:        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        return payload
    except jwt.ExpiredSignatureError as e:
        raise Exception("Token hết hạn, vui lòng đăng nhập lại")
        return None
    except Exception as e:
        raise Exception("Sai token")
        return None

def encode(payload):
    jwt_token = {'token': jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')}
    return jwt_token