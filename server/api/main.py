from django.conf import settings
from lib.TGMT.TGMTfile import *

def OnReady():  
    MkDir(os.path.join(settings.MEDIA_ROOT))
