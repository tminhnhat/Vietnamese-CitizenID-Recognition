from rest_framework.decorators import api_view
import json
from api.models import User, Patrol, Route
from api.apps import *
import datetime
from dateutil.parser import parse
from api.excel_utils import *
from lib.TGMT.TGMTpaging import Paging

####################################################################################################

@api_view(["POST"])
def FinishPatrol(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)

        _route_pk = RequireParamExist(request, "route_pk", "tuyến tuần tra")
        _route_name = request.POST.get("route_name")
        _NFCnames = request.POST.get("NFCnames")
        _timeList = request.POST.get("timeList")    
        startTime = GetParam(request, "startTime")
        startTime = parse(startTime)
        finishTime = GetParam(request, "finishTime")
        finishTime = parse(finishTime)

        _duration = (finishTime - startTime).seconds

        route = Route.objects.get(pk=_route_pk, isDeleted=False)

        patrol = Patrol(building_pk = route.building_pk,
            buildingName = route.buildingName,
            routeName = route.name,            
            NFCnames = _NFCnames,
            timeList = _timeList,
            email = loginSession["email"],            
            receivedTime = utcnow(),
            duration = _duration)

        patrol.save()

        return SuccessResponse("Tuần tra " + _route_name + " thành công")
    except Exception as e: 
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def GetPatrolList(request):
    try:
        _token = GetParam(request, "token")
        loginSession = api.auth.decode(_token)
                    
        _route_pk = request.POST.get("route_pk")
        _fromDateStr = RequireParamExist(request, "fromDate", "từ ngày")
        _toDateStr = RequireParamExist(request, "toDate", "đến ngày")
        _user_id = request.POST.get("user_id")
        

        _fromDate = parse(_fromDateStr) + datetime.timedelta(hours=-7) 
        _toDate = parse(_toDateStr) +  datetime.timedelta(days=1) + datetime.timedelta(hours=-7) 

        if(_fromDate == None or _toDate == None):
            return ErrorResponse("Thiếu ngày")

        patrols = Patrol.objects(receivedTime__gte=_fromDate, receivedTime__lt=_toDate, isDeleted=False )
        if(_route_pk != None and _route_pk != "all" and _route_pk != "" ):
            patrols = patrols(route_pk = _route_pk)
        

        if(_user_id != None and _user_id != "" and _user_id != "all"):
            patrols = patrols(user_id=_user_id)

        _order_by = GetParam(request, "order_by")
        if(_order_by != None and _order_by in ["receivedTime", "-receivedTime"]):
            patrols = patrols.order_by(_order_by)

        respond = Paging(request, patrols)
        return ObjResponse(respond)
    except Exception as e: 
        return ErrorResponse(str(e))

####################################################################################################

@api_view(["POST"])
def PatrolReportExcel(request):
    try:
        _token = request.POST.get("token")
        loginSession = api.auth.decode(_token)
                                
        _route_name = request.POST.get("route_name")
        _building_id = request.POST.get("building_id")
        _fromDateStr = request.POST.get("fromDate")
        _toDateStr =request.POST.get("toDate")
        if(_fromDateStr == None or _fromDateStr == "" or
            _toDateStr == None or _toDateStr == ""):
            return ErrorResponse("Thiếu ngày")

        _fromDate =parse(_fromDateStr) + datetime.timedelta(hours=-7) 
        _toDate = parse(_toDateStr) +  datetime.timedelta(days=1) + datetime.timedelta(hours=-7) 

        if(_fromDate == None or _toDate == None):
            return ErrorResponse("Thiếu ngày")

        if(_route_name != None and _route_name != ""):
            patrols = Patrol.objects(time__gte=_fromDate, time__lt=_toDate, building_id = _building_id, route_name = _route_name)
        else:
            patrols = Patrol.objects(time__gte=_fromDate, time__lt=_toDate, building_id = _building_id)

        #excel part
        wb = Workbook()
        ws = wb.active
        bold = Font(b=True)
        style = NamedStyle(name="highlight")
        style.font = bold

        ws["A1"] ="BÁO CÁO TUẦN TRA"  
        border = Border()
        al = Alignment(horizontal="center", vertical="center")
        style_range_merge(ws, "A1:F1", border=border, fill=None, font=bold, alignment=al)

        ws["C3"] ="Từ ngày"
        ws["D3"] =_fromDate.strftime("%d-%m-%Y")
        ws["C4"] = "Tuyến"
        ws["D4"] = _route_name if _route_name != None and _route_name != "" else "Tất cả"
        ws["C5"] ="Bãi xe"
        ws["D5"] = _building_id

        ws["E3"] ="Đến ngày"
        ws["E3"].style = style
        ws["F3"] = _toDate.strftime("%d-%m-%Y")
        style_range(ws, "C3:C6", style)

        #table 1
        # data = [
        #     ["Apples", 10000, 5000, 8000, 6000],
        #     ["Pears",   2000, 3000, 4000, 5000],
        #     ["Bananas", 6000, 6000, 6500, 6000],
        #     ["Oranges",  500,  300,  200,  700],
        # ]
        
        ws.append(["STT", "NGÀY GIỜ", "TUYẾN TUẦN TRA", "CHECKPOINT", "VÀO LÚC", "SỐ PHÚT", "NHÂN VIÊN/VỊ TRÍ"])
        #data = []
        index = 1
        for patrol in patrols:
            timeVN = patrol.time + datetime.timedelta(hours=7) 
            patrol_row = []
            patrol_row.append(index)
            patrol_row.append(timeVN.strftime("%d-%m-%Y %H:%M")) 
            patrol_row.append(patrol.route_name)
            patrol_row.append(patrol.NFCnames.replace(",", "\n"))
            patrol_row.append(patrol.timeList.replace(",", "\n"))
            patrol_row.append(patrol.duration)
            patrol_row.append(patrol.user_id + "/" + patrol.role_id)

            #data.append()
            
            ws.append(patrol_row)
            ws["D"+ str(index + 7)].alignment = Alignment(wrapText=True)
            ws["E"+ str(index + 7)].alignment = Alignment(wrapText=True)
            index = index + 1

        for col in ws.columns:
            max_length = 0
            for cell in col:
                if cell.coordinate in ws.merged_cells: # not check merge_cells
                    continue
                try: # Necessary to avoid error on empty cells
                    cellValue = cell.value.split("\n")[0]
                    if len(str(cellValue)) > max_length:
                        max_length = len(cellValue)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[col[0].column].width = adjusted_width


        patrol_len = len(patrols)
        table1_max_row = 7 + patrol_len
        create_table(ws, "Table1", "A7:G{}".format(table1_max_row))

        respond = createHttpRespond(wb)

        return respond
    except Exception as e: 
        print(str(e))
        return ErrorResponse("Có lỗi " + str(e))
