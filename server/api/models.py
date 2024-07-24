from mongoengine import Document, IntField, StringField, DateTimeField, BooleanField, EmailField, ListField, DictField, FloatField

################################################################
#No.1
LEVELS = (
    'Root',
    'Admin', #register
    'Staff',
    'Manager',
    'Cashier',
    'Stocker',
    'Gate', #admin create
    'Supporter' #root create
)

USER_STATUS = (
    'Registered',
    'Verified', #verify by phone number
    'Approved', #root approve
    'Suspend',
    'Invited'
)

SERVICE_PACK = (
    'Free',
    'Basic',
    'Premium',
    'Subscription'
)

class History(Document):
    imagePath           =  StringField()
    timeCreate          =  DateTimeField()
    idNumber            =  StringField()
    fullName            =  StringField()
    dateOfBirth         =  StringField()
    gender              =  StringField()
    nationality         =  StringField()
    placeOfOrigin       =  StringField()
    placeOfResidence    =  StringField()
    isDeleted           =  BooleanField(default = False)   

################################################################

class Annotation(Document):
    imagePath              =  StringField()
    timeCreate             =  DateTimeField()
    text                   =  StringField()
    checked                =  BooleanField(default = False)   
    isDeleted              =  BooleanField(default = False)   

################################################################

class User(Document):    
    email               =  StringField(unique=True) #require with admin
    fullname            =  StringField()
    fullname_ascii      =  StringField()
    position            =  StringField()
    building_pk         =  StringField()
    buildingName        =  StringField()
    password            =  StringField(required=True)
    phone               =  StringField()
    orgName             =  StringField(default="")
    addressOrg          =  StringField()
    phoneOrg            =  StringField()
    level               =  StringField(choices=LEVELS)
    status              =  StringField(choices=USER_STATUS)
    servicePack         =  StringField(choices=SERVICE_PACK)
    owner               =  StringField(required=True) #email of owner
    timeCreate          =  DateTimeField()
    timeRegister        =  DateTimeField()
    timeUpdate          =  DateTimeField()
    numGateAccount      =  IntField(default=0)
    numGateAccountAdded =  IntField(default=0)
    numPerson           =  IntField(default=0)
    countPerson         =  IntField(default=0) #num person has image
    suspendReason       =  StringField()
    references          =  StringField()
    secretkey           =  StringField()
    permissions         =  ListField(StringField())
    currentPersonIdx    =  IntField(default=0)
    bankCode            =  StringField()
    bankName            =  StringField()
    bankNumber          =  StringField()
    showInfo            =  BooleanField(default = False)
    isDeleted           =  BooleanField(default = False)            

################################################################

class Level(Document):
    levelID             =  StringField(required=True)
    levelName           =  StringField(required=True)

################################################################

class SearchOption(Document):
    optionID            =  StringField(required=True)
    optionName          =  StringField(required=True)
    admin               =  BooleanField(default=True)
    smod                =  BooleanField(default=False)
    mod                 =  BooleanField(default=False)
    staff               =  BooleanField(default=False)
    partner             =  BooleanField(default=False)
    guest               =  BooleanField(default=False)
  
################################################################
GENDERS = (
    'Male',
    'Female',
    'undefined',
    'Nam',
    'Nữ',
    'Chưa biết'
)
STATE = (
    'Checked_in',
    'Checked_out',
    'Visitor',
    'Khách vào',
    'Khách ra',
    'Vãng lai',
    'Vào đúng',
    'Vào trễ',
    'Nghỉ đúng',
    'Nghỉ sớm',
    'Về đúng',
    'Về sớm'    
)
PERSON_TYPE = (
    'Guest',
    'Staff',
    'Khách',
    'Nhân viên'
)

class Person(Document):
    personID            =  StringField()
    fullName            =  StringField(default="Khách mới")
    fullName_ascii      =  StringField()
    dirName             =  StringField()
    email               =  StringField()
    birthday            =  DateTimeField()
    cmnd                =  StringField()
    issuedDate          =  DateTimeField() #CMND
    address             =  StringField(default="")
    note                =  StringField()
    dateCreate          =  DateTimeField(required=True)
    firstTimeAppear     =  DateTimeField()
    lastTimeAppear      =  DateTimeField()
    gender              =  StringField(choices=GENDERS, default='Chưa biết')
    phone               =  StringField()
    totalAppear         =  IntField(default=0)    
    group_pk            =  StringField()
    groupName           =  StringField()
    owner               =  StringField(required=True) #email
    orgName             =  StringField()    
    lastestImgPath      =  StringField() #to remove because has avatar
    avatar              =  StringField()  
    cardID              =  StringField()
    building_pk         =  StringField()
    buildingName        =  StringField()    
    timeUpdate          =  DateTimeField()
    userUpdate          =  StringField()
    timeAddTemplate     =  DateTimeField()
    state               =  StringField(choices=STATE, default='Vãng lai')
    personType          =  StringField(choices=PERSON_TYPE, default='Khách')
    startShift          =  StringField() #hh:mm
    endShift            =  StringField() #hh:mm
    relaxes             =  ListField(StringField())
    isDeleted           =  BooleanField(default = False)
    
################################################################
#No.5
class Appear(Document):
    person_pk           =  StringField(required=True)
    person_id           =  StringField()
    fullName            =  StringField(default='Khách mới')
    fullName_ascii      =  StringField()
    birthday            =  DateTimeField()
    phone               =  StringField()
    timeAppear          =  DateTimeField(required=True)
    timeCheckout        =  DateTimeField()
    imagePath           =  StringField(required=True)
    personExist         =  BooleanField(default=False)
    client_pk           =  StringField()
    group_pk            =  StringField()
    groupName           =  StringField()
    gate                =  StringField()
    owner               =  StringField(required=True)
    distance            =  FloatField()
    percent             =  IntField()
    elapsed             =  FloatField()
    gender              =  StringField(choices=GENDERS, default='Chưa biết') #to retrain model
    state               =  StringField(choices=STATE, default='Vãng lai')
    numSecond           =  IntField() #total second between login - logout
    lastAppear_pk       =  StringField() #pk of last checkin
    stage               =  IntField()
    shift_id            =  IntField()
    timeUpdate          =  DateTimeField()
    userUpdate          =  StringField()
    checked_out         =  BooleanField(default=False)
    personType          =  StringField(choices=PERSON_TYPE, default='Khách')    
    similarPath         =  StringField() #path to most similar image
    isDeleted           =  BooleanField(default = False)

################################################################
#No.6
class LoginSession(Document):
    token               =  StringField()
    email               =  StringField(required=True)
    level               =  StringField(required=True)
    fullname            =  StringField()
    loginTime           =  DateTimeField(required=True)
    logoutTime          =  DateTimeField()
    platform            =  StringField()
    orgName             =  StringField()
    owner               =  StringField()
    purpose             =  StringField()
    permissions         =  ListField(StringField())
    validTo             =  DateTimeField()
    isDeleted           =  BooleanField(default=False)

################################################################
#No.7

class Client(Document):    
    clientName          =  StringField()
    UID                 =  StringField(required=True)
    os                  =  StringField(required=True)
    platform            =  StringField(required=True)
    note                =  StringField(max_length=1000)
    timeUpdate          =  DateTimeField()
    allow               =  BooleanField(default=False)
    isDeleted           =  BooleanField(default=False)


################################################################

class Notification(Document):    
    notifyType          =  StringField(required=True)
    content             =  StringField(required=True)
    link                =  StringField(default = ' ')
    dateCreate          =  DateTimeField(required=True)
    userSend            =  StringField(required=True)
    userReceive         =  StringField(required=True)
    status              =  StringField(default="unseen")
    isDeleted           =  BooleanField(default=False)


################################################################

class PersonGroup(Document):
    name                =  StringField(required=True)
    alert               =  BooleanField(required=True) #alert when appear
    ignore              =  BooleanField()
    timeUpdate          =  DateTimeField()
    owner               =  StringField(required=True) #email
    userUpdate          =  StringField() #email
    bgColor             =  StringField()
    isDeleted           =  BooleanField(default=False)

################################################################

PHONE_STATUS = (
    'New',
    'Đã cấp quyền',
    'Đã khóa',
)

class Phone(Document):
    phoneUDID           =  StringField(max_length=200, required=True)
    name                =  StringField(required=True) 
    owner               =  StringField()    
    userUsing           =  StringField()
    appVersion          =  StringField()
    timeCreate          =  DateTimeField(required=True)
    timeUpdate          =  DateTimeField()
    lastRequestDate     =  DateTimeField()
    status              =  StringField(choices=PHONE_STATUS, default="New")
    userUpdate          =  StringField()
    isDeleted           =  BooleanField(default=False)

################################################################

class ChartValue(Document):
    owner               =  StringField(required=True)
    dateSummary         =  StringField(required=True) #dd/MM/yyyy
    dateRecord          =  DateTimeField()
    countOldAppear      =  IntField(required=True)
    countNewAppear      =  IntField(required=True)
    #isDeleted           =  BooleanField(default=False) #dont need 

################################################################
class Shift(Document):
    owner               =  StringField(required=True)
    startShift1         =  StringField(required=True) #hh:mm
    endShift1           =  StringField(required=True) #hh:mm
    startShift2         =  StringField(required=True) #hh:mm
    endShift2           =  StringField(required=True) #hh:mm
    startShift3         =  StringField(required=True) #hh:mm
    endShift3           =  StringField(required=True) #hh:mm
    dateCreate          =  DateTimeField(required=True)
    dateModify          =  DateTimeField(required=True)
    isDeleted           =  BooleanField(default=False)

################################################################

class Label(Document):
    labelIndex          =  IntField(required=True)
    labelName           =  StringField(required=True)
    dateModify          =  DateTimeField()
    isDeleted           =  BooleanField(default=False)

################################################################

ACTIVITIES = (
    'Thêm khách hàng',
    'Cập nhật khách hàng',
    'Xóa khách hàng',
    'Gộp khách hàng',
    'Xóa ảnh khách hàng',
    'Xuất report khách hàng'
    'Xuất report lượt vào'
)

class Activity(Document):
    email               =  StringField(required=True)
    activity            =  StringField(required=True)
    value               =  StringField(required=True)
    product_pk          =  StringField(require = True)
    changes             =  ListField(DictField())
    oldvalue            =  StringField(require = True)
    currentvalue        =  StringField(require = True)
    unit                =  StringField()
    timeCreate          =  DateTimeField(required=True)
    isDeleted           =  BooleanField(default=False)


################################################################

LOGS = (
    'Thêm lượt vào thất bại',
    'Thêm khách hàng thất bại',
    'Cập nhật khách hàng thất bại',
    'Xóa khách hàng thất bại',
    'Gộp khách hàng thất bại',
    'Xóa ảnh khách hàng thất bại',
    'Xuất report khách hàng thất bại'
    'Xuất report lượt vào thất bại'
)

class Log(Document):
    activity            =  StringField(required=True)
    exception           =  StringField(required=True)
    timeCreate          =  DateTimeField(required=True)
    isDeleted           =  BooleanField(default=False)

################################################################

class Option(Document):
    key                 =  StringField(required=True)
    note                =  StringField()
    value               =  StringField()
    owner               =  StringField()

################################################################

class Building(Document):
    name                =  StringField(required=True)
    address             =  StringField()
    timeUpdate          =  DateTimeField()
    isDeleted           =  BooleanField(default=False)

################################################################

class Route(Document):
    name                =  StringField()
    NFClist             =  StringField()
    NFCnames            =  StringField()
    building_pk         =  StringField()
    buildingName        =  StringField()
    isDeleted           =  BooleanField(default = False)

################################################################

class Patrol(Document):
    building_pk         =  StringField()
    buildingName        =  StringField()
    route_pk            =  StringField()
    routeName           =  StringField()
    email               =  StringField()
    NFCnames            =  StringField()
    timeList            =  StringField()    
    startTime           =  DateTimeField()
    finishTime          =  DateTimeField()
    receivedTime        =  DateTimeField()
    duration            =  IntField() #minute
    isDeleted           =  BooleanField(default=False)


################################################################

class Group(Document):
    groupID             =  StringField()
    name                =  StringField()
    timeUpdate          =  DateTimeField()
    isDeleted           =  BooleanField(default=False)

################################################################

PRODUCT_STATUS = (
    'Đang bán',
    'Ngưng bán',
)

class Product(Document):
    barcode             =  StringField()
    name                =  StringField()
    cost                =  IntField()
    price               =  IntField()
    revenue             =  IntField()
    building_pk         =  StringField()
    buildingName        =  StringField()
    changelogs          =  ListField(DictField())
    costs               =  ListField(DictField()) #TODO: delete    
    prices              =  ListField(DictField()) #TODO: delete  
    amounts             =  ListField(DictField()) #TODO: delete    
    inAmounts           =  ListField(DictField()) #TODO: delete  
    outAmounts          =  ListField(DictField()) #TODO: delete  
    histories           =  ListField(DictField()) #cost, price, inAmount and outAmount
    amount              =  IntField() #newest amount
    initInventory       =  IntField()
    inventoryChecked    =  BooleanField(default=False)
    name_ascii          =  StringField()
    author              =  StringField()
    destroyer           =  StringField() #email
    author_pk           =  StringField(required=True)
    authorEmail         =  StringField(required=True)
    authorPhone         =  StringField()
    authorName          =  StringField()
    authorName_ascii    =  StringField()
    avatar              =  StringField()
    imagePaths          =  ListField(StringField())
    thumbPaths          =  ListField(StringField())
    brand_pk            =  StringField()
    brand               =  StringField()
    unit_pk             =  StringField()
    unit                =  StringField()
    detail              =  StringField()
    status              =  StringField(choices=PRODUCT_STATUS)
    timeCreate          =  DateTimeField(required=True)
    timeUpdate          =  DateTimeField()
    isDeleted           =  BooleanField(default=False)

################################################################

class Phase(Document):
    building_pk         =  StringField()
    buildingName        =  StringField()
    type                =  StringField()
    dateCreate          =  DateTimeField()
    isDeleted           =  BooleanField(default=False)

################################################################

class TempPrice(Document):
    barcode             =  StringField()
    name                =  StringField()
    price1              =  FloatField()
    price2              =  FloatField()
    store               =  StringField()
    isDeleted           =  BooleanField(default=False)

################################################################

class TempProduct(Document):
    STT                 =  IntField()
    barcode             =  StringField()
    name                =  StringField()
    unit                =  StringField()
    amount              =  FloatField()
    store               =  StringField()
    isDeleted           =  BooleanField(default=False)

################################################################

class ProfitAlert(Document):
    price               =  IntField()
    percentMin          =  IntField()
    percentMax          =  IntField()
    isDeleted           =  BooleanField(default=False)