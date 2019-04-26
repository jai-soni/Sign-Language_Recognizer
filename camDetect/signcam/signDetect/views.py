from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
from django.core.files.base import ContentFile
import cv2
from keras.preprocessing import image
import requests

KERAS_REST_API_URL = "http://localhost:5000/predict"

def index(request):
	context = {}
	return render(request, 'test.html', context)

def get_cropped_image(img):
	x, y, w, h = 400, 80, 200, 200
#     cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 3)
	imgCrop = img[y:y+h, x:x+w]
	return imgCrop

def get_thres(img):
	# convert to grayscale
	grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     applying gaussian blur
	value = (5, 5)
	blurred = cv2.GaussianBlur(grey, value, 0)

#     thresholdin: Otsu's Binarization method
	_, thresh = cv2.threshold(blurred, 127, 255,
							   cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
	return thresh

img_bck = 0
alpha = {}
alpha['count'] = 0
alpha['letter'] = ""
sentence = ""
sentence_all=[]

def get_sentence():
	# print("Inside A :",sentence)
	return sentence

def get_sentence_all():
	# print("Inside B :",sentence_all)
	return sentence_all
def set_sentence(s):
	global sentence
	sentence=s
def set_sentence_all(s_list):
	global sentence_all
	sentence_all = s_list

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
		
		#-------------------------------------------------------------------------------------------------------#
		sentence = get_sentence()
		sentence_all = get_sentence_all()
		img = cv2.imread("image.jpg")
		try:
			img_cropped = get_cropped_image(img)
			thresh = get_thres(img_cropped)
			contours= cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[1]
			contour = max(contours, key = cv2.contourArea)
			img_name= "gesture.jpg"
			if len(contours) > 0:
				if cv2.contourArea(contour) < 12000:
					# try:
					cv2.imwrite(img_name, thresh)
					pred=""
					# try:
					image = open("gesture.jpg", "rb").read()
					payload = {"image": image}
					r = requests.post(KERAS_REST_API_URL, files=payload).json()
					if r["success"]:
					# loop over the predictions and display them
						pred = r['predictions'][0]['label']
						print("--Pred : ",pred)
						print("sentence :",sentence)
						print("sentence_all :",sentence_all)
						print("len:",str(len(sentence_all)))
						#-----------------------------------
						# if(alpha['letter'] == pred):
						# 	alpha['count'] = alpha['count'] + 1
						# 	alpha['letter'] = pred
						# else:
						# 	alpha['count'] = 0
						# 	alpha['letter'] = pred
						# print(alpha)
						# if(alpha['count']>2):
						# 	alpha['count'] = 0
							# return HttpResponse("Hello")
							# return HttpResponse(alpha['letter'])
						#------------------------------------

						if len(sentence_all)>2 and pred == sentence_all[-2] and pred == sentence_all[-1]:
							print("Inside C-----------")
							if pred =="STOP":
								if not "STOP" in sentence: 
									sentence = sentence + pred
									set_sentence(sentence)
								return HttpResponse(sentence)
							elif pred.lower() =="OK GOOGLE".lower():
								sentence="Ok Google , "
								sentence_all=[]
								set_sentence(sentence)
								set_sentence_all(sentence_all)
								print("Inside D--------")
							else:
								sentence = sentence + pred
								print("Sentence Forming : ",sentence)
								set_sentence(sentence)
						else:
							sentence_all.append(pred)
							set_sentence_all(sentence_all)
							return HttpResponse(pred)	
						# except:
						# 	return HttpResponse("")
					# except Exception as e:
					# 	pred = "--"
					# 	print("Something Happened :",e)
					# 	return HttpResponse("")
		except :
			print("Image not read")
	return HttpResponse("")
	if request.method == "GET":
		return HttpResponse("hello")