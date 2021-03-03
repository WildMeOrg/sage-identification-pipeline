import requests
import os 

from .utils import safe_request

api_prefix = 'https://demo.dyn.wildme.io'

def fetch_db_numbers():
  result = safe_request(request_job = requests.get, url=f'{api_prefix}/api/core/db/numbers/')
  json = result.json()
  print(json)
  imageCount = json['response']['images']
  annotationCount = json['response']['annotations']
  nameCount = json['response']['names']
  print(imageCount)
  print(annotationCount)
  print(nameCount)

def post_target_image():
  filename='/Volumes/dev/wave-0.12.1-darwin-amd64/data/f/3028f5eb-8c3c-48fb-8be3-0a157469f764/154773829_10160676684692785_6544825338980507531_o.jpg'
  imageData = open(filename, 'rb').read()
  result = safe_request(request_job = requests.post, url=f'{api_prefix}/api/upload/image', params={'image': imageData})
  # print(result)


