import os
import re
import json
import cv2
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from paddleocr import PaddleOCR
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from api.apps import printt

from lib.TGMT.TGMTthread import ThreadWithReturnValue

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ocr = None
detector = None

class Extractor:

    def __init__(self):

        self.config = Cfg.load_config_from_name('vgg_seq2seq')
        self.config['weights'] = os.path.join(CURRENT_DIR, "seq2seqocr.pth")
        self.config['cnn']['pretrained'] = False
        self.config['device'] = 'cpu'

        if (ocr == None):
            self.ocr = PaddleOCR(lang='en')
        else:
            self.ocr = ocr
        if (detector == None):
            self.detector = Predictor(self.config)
        else:
            self.detector = detector

        # result = {'ID_number':'',
        #              'Name':'',
        #              'Date_of_birth':'',
        #              'Gender':'',
        #              'Nationality':'',
        #              'Place_of_origin':'',
        #              'Place_of_residence':''}
        
    ####################################################################################################
        
    def Detection(self, frame):
        annotations = self.ocr.ocr(frame, rec=True, cls=False)
        return annotations[0]

    ####################################################################################################

    def WarpAndSave(self, frame, fileName, top_left, top_right, bottom_right, bottom_left):

        w, h, cn = frame.shape
        padding = 4.0
        padding = int(padding * w / 640)

        # All points are in format [cols, rows]
        pt_A = top_left[0], top_left[1]
        pt_B = bottom_left[0], bottom_left[1]
        pt_C = bottom_right[0], bottom_right[1]
        pt_D = top_right[0], top_right[1]

        # Here, I have used L2 norm. You can use L1 also.
        width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
        width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
        maxWidth = max(int(width_AD), int(width_BC)) 
    
        height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
        height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
        maxHeight = max(int(height_AB), int(height_CD))

        input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
        output_pts = np.float32([[0, 0],
                                [0, maxHeight - 1],
                                [maxWidth - 1, maxHeight -1],
                                [maxWidth - 1, 0]])

    # Compute the perspective transform M
        M = cv2.getPerspectiveTransform(input_pts,output_pts)

        matWarped = cv2.warpPerspective(frame,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)
        cv2.imwrite(fileName, matWarped)

        return True

    ####################################################################################################
    
    def WarpAndRec(self, frame, top_left, top_right, bottom_right, bottom_left):
        w, h, cn = frame.shape
        padding = 4.0
        padding = int(padding * w / 640)

        box = []
        # All points are in format [cols, rows]
        pt_A = top_left[0]-padding, top_left[1]-padding
        pt_B = bottom_left[0]-padding, bottom_left[1]+padding
        pt_C = bottom_right[0]+padding, bottom_right[1]+padding
        pt_D = top_right[0]+padding, top_right[1]-padding

        # Here, I have used L2 norm. You can use L1 also.
        width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
        width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
        maxWidth = max(int(width_AD), int(width_BC)) 
        
        height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
        height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
        maxHeight = max(int(height_AB), int(height_CD))

        input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
        output_pts = np.float32([[0, 0],
                                [0, maxHeight - 1],
                                [maxWidth - 1, maxHeight -1],
                                [maxWidth - 1, 0]])

        # Compute the perspective transform M
        M = cv2.getPerspectiveTransform(input_pts,output_pts)

        matWarped = cv2.warpPerspective(frame,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)
        # cv2.imwrite(fileName, matWarped)
        
        s = self.detector.predict(Image.fromarray(matWarped))

        box.append(pt_A)
        box.append(pt_D)
        box.append(pt_C)
        box.append(pt_B)

        return [s,box]
    
    ####################################################################################################

    def GetInformationAndSave(self, _results, _idnumber, _idnumberbox):
        printt("---------------------------------")
        printt(_results)
        #string = '{"ID_number": "09219802508", "Name": "", "Date_of_birth": "", "Gender": "", "Nationality": "", "Place_of_origin": "", "Place_of_residence": "", "ID_number_box": [[208.0, 171.0], [495.0, 177.0], [495.0, 201.0], [208.0, 195.0]]}'
        #result = json.loads(string)
        
        result = {}
        result['ID_number']          = _idnumber
        result['Name']               = ''
        result['Date_of_birth']      = ''
        result['Gender']             = ''
        result['Nationality']        = ''
        result['Place_of_origin']    = ''
        result['Place_of_residence'] = ''
        result['ID_number_box']      = _idnumberbox

        regex_dob = r'[0-9][0-9]/[0-9][0-9]'
        regex_residence = r'[0-9][0-9]/[0-9][0-9]/|[0-9]{4,10}|Date|Demo|Dis|Dec|Dale|fer|ting|gical|ping|exp|ver|pate|cond|trị|đến|không|Không|Có|Pat|ter|ity'


        for i,res in enumerate(_results):
            s = res[0]

            printt(s)
            if re.search(r'tên|name',s):
                # result['ID_number']                   = result[i+1].split(':|;|,|\\.|\s+')[-1].strip()
                # ID_number                             = result[i+1] if re.search(r'[0-9][0-9][0-9]',(re.split(r':|[.]|\s+',result[i+1][0]))[-1].strip()) else (result[i+2] if re.search(r'[0-9][0-9][0-9]',result[i+2][0]) else result[i+3])
                # result['ID_number']                   = (re.split(r':|[.]|\s+',ID_number[0]))[-1].strip()
                # result['ID_number_box']               = ID_number[1]

                Name                                    = _results[i+1] if (not re.search(r'[0-9]', _results[i+1][0])) else _results[i+2]
                result['Name']                          = Name[0].title()
                result['Name_box']                      = Name[1] if Name[1] else []

                if (result['Date_of_birth']  == ''):
                    DOB                                 = _results[i-2] if re.search(regex_dob, _results[i-2][0]) else []
                    result['Date_of_birth']             = (re.split(r':|\s+', DOB[0]))[-1].strip() if DOB else ''
                    result['Date_of_birth_box']         = DOB[1] if DOB else []
                continue

            if re.search(r'sinh|birth|bith',s) and (not result['Date_of_birth']):
                if re.search(regex_dob, s):
                    DOB                                 = _results[i]

                elif re.search(regex_dob,_results[i-1][0]):
                    DOB                                 = _results[i-1]   

                elif re.search(regex_dob,_results[i+1][0]): 
                    DOB                                 = _results[i+1]  

                else:
                    DOB                                 =  []

                result['Date_of_birth']                 = (re.split(r':|\s+',DOB[0]))[-1].strip() if DOB else ''
                result['Date_of_birth_box']             = DOB[1] if DOB else []

                if re.search(r"Việt Nam", _results[i+1][0]):
                    result['Nationality']               = 'Việt Nam'
                    result['Nationality_box']           = _results[i+1][1]

                continue

            if re.search(r'Giới|Sex',s):
                Gender                                  = _results[i]
                result['Gender']                        = 'Nữ' if re.search(r'Nữ|nữ',Gender[0]) else 'Nam'
                result['Gender_box']                    = Gender[1] if Gender[1] else []
                # continue

            if re.search(r'Quốc|tịch|Nat',s):
                if (not re.search(r'ty|ing', re.split(r':|,|[.]|ty|tịch', s)[-1].strip()) and (len(re.split(r':|,|[.]|ty|tịch', s)[-1].strip()) >= 3)):
                    Nationality                         = _results[i]

                elif not re.search(r'[0-9][0-9]/[0-9][0-9]/', _results[i+1][0]):
                    Nationality                         = _results[i+1]

                else:
                    Nationality                         = _results[i-1]

                result['Nationality']                   = re.split(r':|-|,|[.]|ty|[0-9]|tịch', Nationality[0])[-1].strip().title()
                result['Nationality_box']               = Nationality[1] if Nationality[1] else []

                for s in re.split(r'\s+',result['Nationality']):
                    if len(s) < 3:
                        result['Nationality']           = re.split(s, result['Nationality'])[-1].strip().title()
                if re.search(r'Nam', result['Nationality']):
                    result['Nationality'] = 'Việt Nam'

                continue

            if re.search(r'Quê|origin|ongin|ngin|orging',s):
                PlaceOfOrigin                           = [_results[i], _results[i+1]] if not re.search(r'[0-9]{4}', _results[i+1][0]) else []
                if PlaceOfOrigin:
                    if len(re.split(r':|;|of|ging|gin|ggong',PlaceOfOrigin[0][0])[-1].strip()) > 2:
                        result['Place_of_origin']           = ((re.split(r':|;|of|ging|gin|ggong', PlaceOfOrigin[0][0]))[-1].strip() + ', ' + PlaceOfOrigin[1][0]) 
                    else:
                        result['Place_of_origin']           = PlaceOfOrigin[1][0]
                    result['Place_of_origin_box']           = PlaceOfOrigin[1][1]
                continue

            if re.search(r'Nơi|trú|residence', s):
                vals2 = "" if (i+2 > len(_results)-1) else _results[i+2] if len(_results[i+2][0]) > 5 else _results[-1]
                vals3 = "" if (i+3 > len(_results)-1) else _results[i+3] if len(_results[i+3][0]) > 5 else _results[-1]

                if ((re.split(r':|;|residence|ence|end',s))[-1].strip() != ''): 

                    if (vals2!='' and not re.search(regex_residence, vals2[0])):
                        PlaceOfResidence                = [_results[i], vals2]
                    elif (vals3!='' and not re.search(regex_residence, vals3[0])):
                        PlaceOfResidence                = [_results[i], vals3]
                    elif not re.search(regex_residence, _results[-1][0]):
                        PlaceOfResidence                = [_results[i], _results[-1]]
                    else:
                        PlaceOfResidence                = [_results[-1],[]]
                    
                else:
                    PlaceOfResidence                    = [vals2,[]] if (vals2 and not re.search(regex_residence, vals2[0])) else [_results[-1],[]]

                printt('PlaceOfResidence: {}'.format(PlaceOfResidence))
                if PlaceOfResidence[1]:
                    result['Place_of_residence']        = re.split(r':|;|residence|sidencs|ence|end', PlaceOfResidence[0][0])[-1].strip() + ' ' + str(PlaceOfResidence[1][0]).strip()
                    result['Place_of_residence_box']    = PlaceOfResidence[1][1]

                else:
                    result['Place_of_residence']        = PlaceOfResidence[0][0]                                                                                                           
                    result['Place_of_residence_box']    = PlaceOfResidence[0][1] if PlaceOfResidence else []
                continue

            elif (i == len(_results)-1):
                if result['Place_of_residence'] == '':
                    if not re.search(regex_residence, _results[-1][0]):
                        PlaceOfResidence                = _results[-1]
                    elif not re.search(regex_residence, _results[-2][0]):
                        PlaceOfResidence                = _results[-2]  
                    else: 
                        PlaceOfResidence                = []

                    result['Place_of_residence']            = PlaceOfResidence[0] if PlaceOfResidence else ''
                    result['Place_of_residence_box']        = PlaceOfResidence[1] if PlaceOfResidence else []
                if result['Gender'] == '':
                    result['Gender_box']                    = []
                if result['Nationality'] == '':
                    result['Nationality_box']               = []
                if result['Name'] == '':
                    result['Name_box']                      = []
                if result['Date_of_birth'] == '':
                    result['Date_of_birth_box']             = []
                if result['Place_of_origin'] == '':
                    result['Place_of_origin_box']           = []

            else:
                continue

        with open('extracted_infomation.json','w',encoding='utf-8') as f:
            f.write(json.dumps(result, indent=4, ensure_ascii=False))
            f.close()
    
        return result
    
####################################################################################################

idcard_extractor = Extractor()
# info = idcard_extractor.GetInformationAndSave("extracted_result")
# print(info)

if __name__ == '__main__': 

    img_path ='./20211019_090832.jpg'
    frame = cv2.imread(img_path)
    # annotations = idcard_extractor.Detection(img_path)
    # extracted_result=[]

    # threads = []
    # for i, box in enumerate(annotations):

    #     top_left     = (int(box[0][0]), int(box[0][1]))
    #     top_right    = (int(box[1][0]), int(box[1][1]))
    #     bottom_right = (int(box[2][0]), int(box[2][1]))
    #     bottom_left  = (int(box[3][0]), int(box[3][1]))

    #     t = ThreadWithReturnValue(target=idcard_extractor.WarpAndRec, args=(frame,top_left, top_right, bottom_right, bottom_left))
    #     threads.append(t)
    
    # for t in threads:
    #     t.start()   

    # for t in threads:
    #     extracted_result.append(t.join())

    info = idcard_extractor.GetInformationAndSave("extracted_result")
    print(info)
