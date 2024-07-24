from .notfound import notfound

from .views import index, login, logout, user, \
    changepassword,\
    download,\
    database,\
    duplicate,\
    notification, profile, config, dashboard,\
    client,\
    systeminfo,\
    option,\
    log,\
    register,\
    phase,\
    Redirect, \
    GoogleSearchConsole, \
    idcard
        
    
from .diag import compare, draw_landmark, checkmedia, face_direction, brightness
from .acme_page import terms, price, faq, userguide
from .stream import stream_systeminfo
from .demo_page import glassify, landmark, ml_model, image_classification,\
    facemask, welcome
from .product_page import  products, compareproduct, compareprice, inventory, setupprofit, check_cashier,\
    stock