from web.views.views import CheckToken


def compare(request):
    permissions = ["Root"]
    return CheckToken(request, 'compare.html', permissions)

def draw_landmark(request):
    permissions = ["Root"]
    return CheckToken(request, 'draw_landmark.html', permissions)

def checkmedia(request):
    permissions = ["Root"]
    return CheckToken(request, 'checkmedia.html', permissions)

def face_direction(request):
    permissions = ["Root"]
    return CheckToken(request, 'face_direction.html', permissions)

def brightness(request):
    permissions = ["Root"]
    return CheckToken(request, 'brightness.html', permissions)