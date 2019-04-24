from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
from django.core.files.base import ContentFile
import cv2

def index(request):
    context = {}
    return render(request, 'test.html', context)

@csrf_exempt
def saveImage(request):
	if request.method == "POST":
		image_data = request.body
		received_json_data=json.loads(request.body.decode("utf-8"))
		encoded = received_json_data['data']
		prev_text = received_json_data['text']

		format1, imgstr = encoded.split(';base64,') 
		ext = format1.split('/')[-1] 

		data = base64.b64decode(imgstr)
		with open("image.jpg", "wb") as f:
			f.write(data)
		return HttpResponse("hello")
	if request.method == "GET":
		return HttpResponse("hello")