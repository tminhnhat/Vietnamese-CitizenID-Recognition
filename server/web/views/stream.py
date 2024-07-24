import json
import time
from django.http import StreamingHttpResponse
from api.views.systeminfo import GetRealtimeInfo

def stream_systeminfo(request):
    def event_stream():
        while True:
            time.sleep(1)
            result = GetRealtimeInfo()
            yield 'data: ' + json.dumps(result) + '\n\n'
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')