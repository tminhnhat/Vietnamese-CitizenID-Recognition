from web.views.views import CheckToken


def faq(request):
    permissions = ["all",]
    return CheckToken(request, 'faq.html', permissions)

def price(request):
    permissions = ["all"]
    return CheckToken(request, 'price.html', permissions)

def terms(request):
    permissions = ["all"]
    return CheckToken(request, 'terms.html', permissions)

def userguide(request):
    permissions = ["all"]
    return CheckToken(request, 'userguide.html', permissions)