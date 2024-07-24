from rest_framework.decorators import api_view
from api.apps import *
from api.views.common import QueryHistorys
from api.models import History
from api.excel_utils import *
from datetime import timedelta

####################################################################################################

def CalcAttendance(person, history):
    VNtime = GetVNtime()

    attendanceStatus = "Vào đúng"
    intervalMinutes = 2
    timeHistory = history.timeHistory + timedelta(hours=7)
    startShiftTime = ShiftToDate(person.startShift)
    endShiftTime = ShiftToDate(person.endShift)

    earlyHistorys = History.objects(person_id=person.personID, timeHistory__gte=VNtime+timedelta(-7), timeHistory__lt=VNtime, isDeleted=False)

    if(timeHistory < startShiftTime): #vào trước ca
        attendanceStatus = "Vào đúng"
    elif(startShiftTime < timeHistory and timeHistory < startShiftTime + timedelta(minutes=30)): #vào lúc bắt đầu ca
        if(timeHistory  < startShiftTime + timedelta(minutes=intervalMinutes)): #vào đúng ca
            attendanceStatus = "Vào đúng"
        else:
            attendanceStatus = "Vào trễ"
    elif(IsInRelaxSlot(person, history)):
        if(person.state in ["Vào đúng", "Vào trễ"]):
            attendanceStatus = "Nghỉ đúng"
    elif(timeHistory > endShiftTime + timedelta(minutes=-30)):
        attendanceStatus = "Về sớm"
    elif(endShiftTime < timeHistory): #giờ về
        attendanceStatus = "Về đúng"    
    else: #giờ làm
        if(len(earlyHistorys) == 0):
            attendanceStatus = "Vào trễ"
        else:        
            attendanceStatus = "Nghỉ sớm"
    
    return attendanceStatus

####################################################################################################
        
def IsBeginShift(person, beginHour):
    startShift = person.startShift
    _beginHour = beginHour.strftime("hh:mm")
    return _beginHour == startShift

####################################################################################################

def IsInRelaxSlot(person, history):
    if(person.relaxes == None or len(person.relaxes) == 0):
        return False

    timeHistory = history.timeHistory + timedelta(hours=7)
    for relax in person.relaxes:    
        timeBeginRelax = ShiftToDate(relax.split(" - ")[0])
        timeEndRelax = ShiftToDate(relax.split(" - ")[1], 59)

        if(timeBeginRelax <= timeHistory and timeHistory < timeEndRelax):
            return True
    
    return False

####################################################################################################

def ShiftToDate(shift, second=0):
    splitted = shift.split(":")
    VNtime = GetVNtime()
   
    hour = int(splitted[0])
    min = int(splitted[1])
    shiftTime = VNtime.replace(hour=hour, minute=min, second=second)
    return shiftTime

####################################################################################################

@api_view(["POST"])
def ReportExcelAttendance(request):
    try:
        _token = GetParam(request, "token")
        jwt = api.auth.decode(_token)
                                
        historyList = QueryHistorys(request, jwt)

        if(len(historyList) == 0):
            return ErrorResponse("Không tìm thấy lượt ra vào")


        #excel part
        wb = Workbook()
        ws = wb.active
        fontTitle = Font(b=True, size=20)
        
        ws["A1"] ="DANH SÁCH LƯỢT RA VÀO"  
        
        border = Border()
        al = Alignment(horizontal="center", vertical="center")
        

        ws["B3"] = "Từ ngày"
        ws["B4"] = "Đến ngày"

        ws["C3"] = GetParam(request, "fromDate")
        ws["C4"] = GetParam(request, "toDate")

        style = NamedStyle(name="highlight")
        style_range(ws, "D3:D6", style)        

        column_list = ["STT", "MÃ SỐ", "HỌ TÊN", "PHÂN LOẠI", "SỐ ĐIỆN THOẠI",  "TRẠNG THÁI", "GIỜ VÀO", "GIỜ RA"]
        maxColumn = chr(ord('A') + len(column_list) - 1)
        style_range_merge(ws, "A1:" + maxColumn + "1", border=border, fill=None, font=fontTitle, alignment=al)
        
        ws.append(column_list)
        index = 1

        
        for history in historyList:
            state = "Khách vào"
            if(history.personType == "Staff"):
                if(history.state == "Checked_in"):
                    state = "Nhân viên đi vào"
                else:
                    state = "Nhân viên ra về"

            row = []
            row.append(index)
            row.append("P" + str(history.person_id))
            row.append(history.fullName) 
            row.append("Nhân viên" if history.personType in ["Staff", "Nhân viên"] else "Khách")
            row.append(history.phone)
            row.append(state)
            row.append((history.timeHistory + datetime.timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S"))
            if(history.timeCheckout != None):
                row.append((history.timeCheckout + datetime.timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S"))
            else:
                row.append("")

            ws.append(row)

            index = index + 1

        for col in ws.columns:
            max_length = 0
            for cell in col:
                if cell.coordinate in ws.merged_cells: # not check merge_cells
                    continue
                try: # Necessary to avoid error on empty cells
                    lengthOfCell = GetMaxLengthOfCell(str(cell.value))
                    if lengthOfCell > max_length:
                        max_length = lengthOfCell
                except:
                    pass
            
            if(max_length > 60): max_length = 60
            ws.column_dimensions[col[0].column].width = max_length + 6



        table1_max_row = 7 + len(historyList)
        create_table(ws, "Table1", "A7:" + maxColumn +"{}".format(table1_max_row))

        
        respond = createHttpRespond(wb)
        return respond
    except Exception as e: 
        return ErrorResponse(str(e))