from web.views.views import CheckToken


def glassify(request):
    permissions = ["Root", "Admin", "all"]
    return CheckToken(request, 'glassify.html', permissions)

def landmark(request):
    permissions = ["Root", "Admin", "all"]
    return CheckToken(request, 'landmark.html', permissions)

def ml_model(request):
    permissions = ["Root", "Admin"]
    return CheckToken(request, 'ml_model.html', permissions)

def image_classification(request):
    args = {'fullscreen' : True}
    permissions = ["all", "guest"]
    return CheckToken(request, 'image_classification.html', permissions, args)

def facemask(request):
    permissions = ["Root", "Admin", "all"]
    return CheckToken(request, 'facemask.html', permissions)

def welcome(request):
    permissions = ["Root", "Admin", "Gate", "Supporter"]
    return CheckToken(request, 'welcome.html', permissions)