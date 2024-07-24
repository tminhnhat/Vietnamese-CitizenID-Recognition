from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import hashlib
import datetime, time
#from datetime import timezone
from mongoengine.queryset.visitor import Q
from dateutil.parser import parse
from api.apps import *
from django.conf import settings as raspango
from django.core.files.storage import FileSystemStorage
from lib.TGMT.TGMTfile import *
from lib.TGMT.TGMTimage import *
from api.views.loginsession import *
import shutil
#import cv2
import django
import platform
import psutil
# import wmi
