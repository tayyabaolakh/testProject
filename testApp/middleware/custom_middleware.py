from math import remainder
from async_timeout import timeout
from ..models import LogsModel
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
import redis
from redis_rate_limit import RateLimit, TooManyRequests

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.http import response
from django.http import HttpResponse
# from ratelimit import time_bucketed
# from ratelimit import gcra
# from ratelimit import limits, RateLimitException
import traceback
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

    def __init__(self, get_response=None):
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
            redis_middleware(logs_data["ip_address"])
            
            # Task 3
            # group = Group.objects.get(name=request.user.groups.all()[0])
            # user_gorup_middleware(logs_data["ip_address"], group)


        except Exception as e:
            pass

        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        print("heyyy")
        if exception:
            # Format your message here
            message = "**{url}**\n\n{error}\n\n````{tb}````".format(
                url=request.build_absolute_uri(),
                error=repr(exception),
                tb=traceback.format_exc()
            )
            # Do now whatever with this message
            # e.g. requests.post(<slack channel/teams channel>, data=message)
            
        return HttpResponse("Error processing the request.", status=500)
    

# Task 1
def pythonLogging(user_ip, timestamp):
    f = open("logs.txt", "a")
    f.write("IP: "+user_ip+", Time: "+str(timestamp)+"\n")
    f.close()
    

# Task 2
def redis_middleware(user_ip):
    
    try:
        r = get_connection()
        total_calls = 0
        
        if r.get(user_ip) is not None:
            total_calls = r.get(user_ip)
            print("Tayyab")
            print(total_calls)
            if int(total_calls) >= 5:
                raise KeyError()
                # process_exception(self, request, exception)
                # return HttpResponse("Error processing the request.", status=500)
            
            else:
                total_calls = int(total_calls) + 1
                print("total_calls in nested else: ", total_calls)
                remaining_key_time =  r.ttl(user_ip)
                r.set(user_ip, total_calls, ex=remaining_key_time)
        else:
            total_calls = int(total_calls) + 1

        r.set(user_ip, total_calls, ex=60)
        
    except Exception as e:
        print("Exception Raised")
        # process_exception(self, request, exception)
        # return HttpResponse("Error processing the request.", status=500)
    

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
    
    
    
def process_exception(self, request, exception):
    print("heyyy")
    if exception:
        # Format your message here
        message = "**{url}**\n\n{error}\n\n````{tb}````".format(
            url=request.build_absolute_uri(),
            error=repr(exception),
            tb=traceback.format_exc()
        )
        # Do now whatever with this message
        # e.g. requests.post(<slack channel/teams channel>, data=message)
        
    return HttpResponse("Error processing the request.", status=500)