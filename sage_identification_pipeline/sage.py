import requests
import os 
import time
from functools import wraps

from .utils import safe_request, json_dump_data

api_prefix = 'https://demo.dyn.wildme.io'

def sage_process(verbose = False):
  def sage_process_decorator(func):
    @wraps(func)
    async def handle_func(*args, **kwargs):
      try:
        if verbose:
          print(f'Running Sage function {func.__name__}')
          print(f'  Args: {args}')
          print(f'  Kwargs: {kwargs}')
          result = await func(*args, **kwargs)
          print(f'  Result: {result}')
        return result
      except Exception as error:
        print(f'Sage function {func.__name__} failed')
        print(error)
        return None
    return handle_func
  return sage_process_decorator

@sage_process(verbose = True)
async def post_target_image(image_path):
  with open(image_path, 'rb') as imageData:
    r = requests.post(f'{api_prefix}/api/upload/image/', files = { 'image': imageData })
    return r.json()['response']

@sage_process(verbose = True)
async def fetch_image_uuid(image_int):
  result = safe_request(request_job = requests.get, url=f'{api_prefix}/api/image/uuid/?gid_list=[{image_int}]')
  json = result.json()
  return json['response'][0]['__UUID__']

@sage_process(verbose = True)
async def fetch_image_size(image_int):
  result = safe_request(request_job = requests.get, url=f'{api_prefix}/api/image/size/?gid_list=[{image_int}]')
  json = result.json()
  return json['response'][0]

@sage_process(verbose = True)
async def kickoff_detection(q, uuid):
  data = json_dump_data({'image_uuid_list': [{'__UUID__': uuid}], 'model_tag': q.args.detection_model_tag, 'sensitivity': q.args.sensitivity, 'nms_thresh': q.args.nms })
  result = safe_request(request_job = requests.get, url=f'{api_prefix}/api/engine/detect/cnn/lightnet/', data = data)
  return result.json()['response']

@sage_process(verbose = True)
async def get_detection_results(q, job_id):
  result = safe_request(request_job = requests.get, url=f'{api_prefix}/api/engine/job/result/?jobid={job_id}')
  json = result.json()
  print(json)
  return json

async def run_pipeline(q, local_image_path):
  print('...starting pipeline')
  image_int = await post_target_image(local_image_path)

  image_uuid = await fetch_image_uuid(image_int)

  image_size = await fetch_image_size(image_int)
  
  job_id = await kickoff_detection(q, image_uuid)

  completed = await poll_status(job_id)

  detection_results = await get_detection_results(q, job_id)

  q.app.detection_complete = True
  if (not detection_result['has_assignments']):
    q.app.annotations = None
    return None
  q.app.annotations = ...
  await kickoff_classification()

async def poll_status(job_id, max_attempts = 5):
  print(f'Running poll status function with job id {job_id}')
  attempt_count = 1
  while attempt_count < max_attempts + 1:
    result = safe_request(request_job = requests.get, url=f'{api_prefix}/api/engine/job/status/?jobid={job_id}')
    json = result.json()
    status = json['response']['jobstatus']
    if (status == 'completed'):
      print(f'  Attempt {attempt_count}: complete')
      print(f'  Result: {json}')
      return json
    print(f'  Attempt {attempt_count}: not complete')
    attempt_count += 1
    time.sleep(3) # wait 3 seconds before polling again 
  print('  Maximum number of attempts exceeded. Returning None.')
  return  None
