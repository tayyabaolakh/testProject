# from ..models import LogsModel
from genericpath import exists
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils import timezone
import redis
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
# ---------------------------------

redis_config = {
    "host": "redis-18134.c283.us-east-1-4.ec2.cloud.redislabs.com",
    "port": "18134",
    "db": "0",
    "password": "wR8XBMk1q4ALATZZkWhxjisDo6ltmJ6Z",
    "decode_responses": True
}

def get_connection():
    return redis.Redis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"], password=redis_config["password"], decode_responses=redis_config["decode_responses"])
        

class LogsMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.create()

        logs_data = dict()
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        logs_data["ip_address"] = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        logs_data["timestamp"] = timezone.now()

        try:
            # Task 1
            pythonLogging(logs_data["ip_address"], logs_data["timestamp"])
            
            # Task 2
            redis_middleware(logs_data["ip_address"], request)
            
            # Task 3
            if request.user is exists:
                group = Group.objects.get(name=request.user.groups.all()[0])
                user_gorup_middleware(logs_data["ip_address"], group)

            else:
                group = "Gold"
                user_gorup_middleware(logs_data["ip_address"], group)

        except Exception as e:
            raise e

        response = self.get_response(request)
        return response
    

# Task 1
def pythonLogging(user_ip, timestamp):
    f = open("logs.txt", "a")
    f.write("IP: "+user_ip+", Time: "+str(timestamp)+"\n")
    f.close()
    

# Task 2
def redis_middleware(user_ip, request):
    
    try:
        r = get_connection()
        total_calls = 0
        
        if r.get(user_ip) is not None:
            total_calls = r.get(user_ip)
            if int(total_calls) >= 5:
                raise PermissionDenied
            
            else:
                total_calls = int(total_calls) + 1
                remaining_key_time =  r.ttl(user_ip)
                r.set(user_ip, total_calls, ex=remaining_key_time)
        else:
            total_calls = int(total_calls) + 1

        r.set(user_ip, total_calls, ex=60)
        
    except Exception as e:
        raise e
        # pass
    

# Task 3
def user_gorup_middleware(user_ip, group):
    if group != '':
        if group == 'Gold':
            access_endpoints(user_ip, 10)
        elif group == 'Silver':
            access_endpoints(user_ip, 5)
        elif group == 'Bronze':
            access_endpoints(user_ip, 2)
    else:
        print("User undefined")


def access_endpoints(user_ip, time):
    try:
        r = get_connection()
        total_calls = 0
        
        if r.get(user_ip) is not None:
            total_calls = r.get(user_ip)
            if int(total_calls) >= time:
                raise PermissionDenied
            
            else:
                total_calls = int(total_calls) + 1
                remaining_key_time =  r.ttl(user_ip)
                r.set(user_ip, total_calls, ex=remaining_key_time)
        else:
            total_calls = int(total_calls) + 1

        r.set(user_ip, total_calls, ex=60)
        
    except Exception as e:
        return HttpResponse(status=201)
    