import json
import math
from api.apps import *

def Paging(request, objects):
    _contentPerPage = GetParam(request, 'contentPerPage')
    _pageNum = GetParam(request, 'pageNum')

    if(_contentPerPage == None or _contentPerPage == "" or _contentPerPage == "0" or _contentPerPage == 0):
        _contentPerPage = 50
    else:
        _contentPerPage = int(_contentPerPage)

    if(_pageNum == None or _pageNum == ""):
        _pageNum = 1
    else:
        _pageNum = int(_pageNum)

    totalObjects = objects.count()
    if(totalObjects == 0):
        num_pages = 0
    else:        
        if(_contentPerPage == 1):
            num_pages = totalObjects
        else:
            num_pages = math.ceil(totalObjects/_contentPerPage)


    has_next = True if _pageNum < num_pages else False
    has_previous = True if _pageNum > 1 else False


    offset = (_pageNum - 1) * _contentPerPage
    if(offset > totalObjects):
        offset = 0

    objects = objects.skip(offset).limit(_contentPerPage)
    objects = json.loads(objects.to_json())

    if(totalObjects == 0):
        _pageNum = 0
        
    obj = {
        "num_pages" : num_pages,
        "currentPage" : _pageNum,
        "totalObject" : totalObjects,
        "has_next" : has_next,
        "has_previous" : has_previous,
        "objects" : objects
    }
    return obj