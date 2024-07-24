
import psutil
from rest_framework.decorators import api_view
from mongoengine.queryset.visitor import Q
from dateutil.parser import parse
from api.apps import *
from api.models import Option
from django.conf import settings
from lib.TGMT.TGMTfile import *
from lib.TGMT.TGMTimage import *
from api.views.loginsession import *
import shutil

####################################################################################################

def GetSystemInfo():
    result = {}
    try:        
        is_built_with_cuda = False
        is_gpu_available = False
        error = ""

        total, used, free = shutil.disk_usage("/")
        gpuInfo = ""
        listGPU = []

        # local_device_protos = device_lib.list_local_devices()
        # for x in local_device_protos:
        #     if(x.device_type == 'GPU'):
        #         gpuInfo = x.physical_device_desc

        dlib_use_cuda = False
        try:            
            dlib_use_cuda = dlib.DLIB_USE_CUDA
        except Exception as e:
            pass

        result = {
            "tf_built_with_cuda" : is_built_with_cuda,
            "tf_gpu_available" : len(listGPU) > 0,
            "num_gpu_available" : len(listGPU),
            "totalDiskSize" : (total // (2**30)),
            "usedDiskSize" : (used // (2**30)),
            "freeDiskSize" : (free // (2**30)),
            # "tf_version" : tf.__version__,
            #"keras_version" : keras.__version__,
            "gpuInfo" : gpuInfo,
            "DLIB_USE_CUDA" : dlib_use_cuda,
            "error" : error,
        }
    
        return result
    except Exception as e:
        printt(str(e))
        return result

####################################################################################################

def GetRealtimeInfo():
    result = {}
    try:        
        mem = dict(psutil.virtual_memory()._asdict())

        cpu_temperature = 0

        result = {           
            "cpu_usage" : str(psutil.cpu_percent()) + "%",
            "RAM_used" :  str(round(mem['used'] / (2**30), 2)) + "GB (" + str(mem['percent']) + "%" + ")",
            "CPU_temp" : str(cpu_temperature) + "*C",
            "server_time" : utcnow().strftime("%Y-%m-%d_%H-%M-%S") 
        }
    
    except Exception as e:
        result = {
            "error" : str(e)
        }
    return result

####################################################################################################

@api_view(["POST"])           
def IsServerRunning(request):
    try:
        return SuccessResponse("running")
    except Exception as e:
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])           
def BackupDB(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)

        RequireLevel(jwt, ["Root"])

        VNtime = GetVNtime()
        dirName = VNtime.strftime("%Y-%m-%d_%H-%M-%S")

        MkDir("/var/idcard/backup_db/" + dirName)

        _command = "mongodump --host localhost --port 27017  --username vohungvi --password viscomsolution"
        _command += " --out /var/idcard/backup_db/" + dirName + " --db attendance"
        _command = "echo " + settings.OS_PASSWORD + " | sudo -S " + _command
        os.system(_command)

        return SuccessResponse("Backup thành công lúc: " + VNtime.strftime("%d/%m/%Y %H:%M:%S"))
    except Exception as e:
        return ErrorResponse(str(e))
