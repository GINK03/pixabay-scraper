import requests
import json
import base64
import os
import glob
import concurrent.futures 
import sys


GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
API_KEY = os.environ['GOOGLE']
def goog_cloud_vison(image_content):
    api_url = GOOGLE_CLOUD_VISION_API_URL + API_KEY
    req_body = json.dumps({
        'requests': [{
            'image': {
                'content': image_content.decode()
            },
            'features': [{
                'type': 'LABEL_DETECTION',
                'maxResults': 100,
            }]
        }]
    })
    res = requests.post(api_url, data=req_body)
    return res.json()

def img_to_base64(filepath):
    with open(filepath, 'rb') as img:
        img_byte = img.read()
    return base64.b64encode(img_byte)

def mapper( name ):
  try:
    save_name = 'vision/' + name.split('/').pop().replace('.jpg', '').replace('.png', '') + '.json'
    if os.path.exists(save_name) is True:
      print('Already Scaned', name)
      return None
    img = img_to_base64(name)
    res_json = goog_cloud_vison(img)
    raw_obj = json.dumps( res_json, indent=2 ) 
    open(save_name, 'w').write( raw_obj )
    print(name)
    print(raw_obj)
  except Exception as e:
    print(e) 

if '--scan' in sys.argv:
  names = [name for name in glob.glob('minimize/*.jpg')]
  #[mapper(name) for name in names]
  with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
    executor.map( mapper, names )

if '--minimize' in sys.argv:
  from concurrent.futures import ProcessPoolExecutor
  from PIL import Image
  def _minimize(name):
    try:
      save_name = 'minimize/' + name.split('/').pop()
      try:
        img = Image.open(name)
      except OSError as e:
        return
      size = img.size
      maxx = max( [size[0], size[1]] )
      bairitsu = maxx/224
      resize = (int(size[0]/bairitsu), int(size[1]/bairitsu))
      try:
        img = img.resize( resize )
      except OSError as e:
        return
      img.save(save_name)
    except Exception as e:
      print('Some Deep Error as', e)
  names = [name for name in glob.glob('./imgs/*')]
  with ProcessPoolExecutor(max_workers=16) as exe:
    exe.map( _minimize, names)

if '--remove' in sys.argv:
  for name in glob.glob('vision/*'):
    try:
      o = json.loads(open(name).read())
    except json.decoder.JSONDecodeError as e:
      print(e)
      os.remove(name)
      continue
    if o.get('error') is not None:
      os.remove(name)
      print( o )

if '--remove_text' in sys.argv:
  for name in glob.glob('vision/*'):
    try:
      o = json.loads(open(name).read())
    except json.decoder.JSONDecodeError as e:
      #print(e)
      os.remove(name)
      continue
    try:
      descs = []
      for obj in o['responses'][0]['labelAnnotations']:
        descs.append(obj['description'])
      #print( descs )
      if 'text' in descs and 'font' in descs:
        #print(name)
        os.remove(name)
        jpeg = name.split('/').pop().replace('.json', '')
        img = glob.glob('./imgs/{}.jpg'.format(jpeg))[0]
        mini = glob.glob('./minimize/{}.jpg'.format(jpeg))[0]
        os.remove(img);os.remove(mini)
        print('shuld be clean ', img, mini)
    except Exception as e:
      print(e)
      #print(o)
      ...
