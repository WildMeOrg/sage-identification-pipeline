import os 
import time
import httpx
import json
from functools import wraps

from .utils import json_dump_data
from .common import make_base_ui

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
async def post_target_image(client, image_path):
  with open(image_path, 'rb') as imageData:
    result = await client.post('/api/upload/image/', files = { 'image': imageData })
    return result.json()['response']

@sage_process(verbose = True)
async def fetch_image_uuid(client, image_int):
  result = await client.get('/api/image/uuid/', params = { 'gid_list': [image_int]})
  json_result = result.json()
  return json_result['response'][0]['__UUID__']

@sage_process(verbose = True)
async def fetch_image_size(client, image_int):
  result = await client.get('/api/image/size/', params = { 'gid_list': [image_int]})
  json_result = result.json()
  return json_result['response'][0]

@sage_process(verbose = True)
async def kickoff_detection(client, q, uuid):
  data = json_dump_data({'image_uuid_list': [{'__UUID__': uuid}], 'model_tag': q.args.detection_model_tag, 'sensitivity': q.args.sensitivity, 'nms_thresh': q.args.nms })
  result = await client.post('/api/engine/detect/cnn/lightnet/', data = data)
  return result.json()['response']

@sage_process(verbose = True)
async def get_detection_results(client, q, job_id):
  result = await client.get('/api/engine/job/result/', params = {'jobid': job_id})
  json_result = result.json()
  results_list = json_result['response']['json_result']['results_list'][0]
  annotation_list = [{'top': x['xtl'], 'left': x['ytl'], 'width': x['width'], 'height': x['height'], 'theta': x['theta'], 'uuid': x['uuid']['__UUID__'], 'id': x['id']} for x in results_list]
  return annotation_list

@sage_process(verbose = True)
async def kickoff_classification(client, q, annotations):
  annot_uuid_list = [{'__UUID__': x['uuid']} for x in annotations]
  data = json_dump_data({'annot_uuid_list': annot_uuid_list, 'model_tag': q.args.classification_model_tag, 'algo': 'densenet' })
  result = await client.post('/api/engine/labeler/cnn/', data = data)
  json_result = result.json()
  return json_result['response']

@sage_process(verbose = True)
async def get_classification_results(client, q, job_id):
  result = await client.get('/api/engine/job/result/', params = {'jobid': job_id})
  json_result = result.json()
  return json_result['response']['json_result']

@sage_process(verbose = True)
async def kickoff_identification(client, q, annotation):
  data = json_dump_data({'annot_uuid': {'__UUID__': annotation['uuid']}, 'database_imgsetid': 570 }) # repeat for each one 
  result = await client.post('/api/engine/review/query/chip/best/', data = data)
  json_result = result.json()
  return json_result['response']

@sage_process(verbose = True)
async def get_identification_results(client, q, job_id):
  result = await client.get('/api/engine/job/result/', params = {'jobid': job_id})
  json_result = result.json()
  return json_result['response']['json_result']['extern']

async def poll_status(client, job_id, max_attempts = 12):
  print(f'Running poll status function with job id {job_id}')
  attempt_count = 1
  while attempt_count < max_attempts + 1:
    result = await client.get('/api/engine/job/status/', params = { 'jobid': job_id })
    json_result = result.json()
    status = json_result['response']['jobstatus']
    if (status == 'completed'):
      print(f'  Attempt {attempt_count}: complete')
      print(f'  Result: {json_result}')
      return json_result
    print(f'  Attempt {attempt_count}: not complete')
    attempt_count += 1
    time.sleep(3) # wait 3 seconds before polling again 
  print('  Maximum number of attempts exceeded. Returning None.')
  return  None

async def run_pipeline(q, local_image_path):
  print('...starting pipeline')
  async with httpx.AsyncClient(base_url=api_prefix) as client:

    image_int = await post_target_image(client, local_image_path)
    image_uuid = await fetch_image_uuid(client, image_int)
    image_size = await fetch_image_size(client, image_int)

    q.app.image_size = image_size
    q.app.upload_complete = True
    q.app.detection_in_progress = True
    await make_base_ui(q)

    detection_job_id = await kickoff_detection(client, q, image_uuid)
    detection_completed = await poll_status(client, detection_job_id)
    annotations = await get_detection_results(client, q, detection_job_id)

    q.app.detection_complete = True
    q.app.detection_in_progress = False
    q.app.classification_in_progress = True
    q.app.annotations = annotations
    await make_base_ui(q)

    classification_job_id = await kickoff_classification(client, q, annotations)
    classification_completed = await poll_status(client, classification_job_id)
    classification_results = await get_classification_results(client, q, classification_job_id)

    q.app.classification_results = classification_results
    q.app.classification_complete = True
    q.app.classification_in_progress = False
    q.app.identification_in_progress = True
    await make_base_ui(q)

    identification_results = []
    for annotation in annotations[:3]:
      identification_job_id = await kickoff_identification(client, q, annotation)
      identification_completed = await poll_status(client, identification_job_id, 120)
      job_results = await get_identification_results(client, q, identification_job_id)
      identification_results.append(job_results)

    q.app.identification_results = identification_results
    q.app.identification_complete = True
    q.app.identification_in_progress = False
    await make_base_ui(q)

