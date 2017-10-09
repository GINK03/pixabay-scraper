
import urllib.request, urllib.error, urllib.parse
import concurrent.futures
import requests
import random
import os
'''
https://images.pexels.com/photos/127723/pexels-photo-127723.jpeg
'''
urls = []
for i in range(500000):
  url = 'https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg'.format(i=i) 
  urls.append( url )
random.shuffle(urls)

def _map(url):
  response = requests.get(url, allow_redirects=False, timeout=5.0)
  save_name = 'download/' + url.split('/').pop()
  void_name = 'voids/' + url.split('/').pop()
  if os.path.exists(save_name):
    return
  if os.path.exists(void_name):
    return
  content = response.content
  if 404 == response.status_code:
    open(void_name, 'w').write('a')
    return
  print( url )
  open(save_name, 'wb').write( content )

with  concurrent.futures.ProcessPoolExecutor(max_workers=756) as executor:
  executor.map( _map, urls)
