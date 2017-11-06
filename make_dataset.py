import json
import pickle
from PIL import Image
import numpy as np
import glob
import random
import sys
import os
from gzip import compress
if '--make_tag_index' in sys.argv:
  dss = []
  for name in glob.glob('./vision/*.json'):
    o = json.loads( open( name ).read() )

    # 画像が大きすぎなど
    if o.get('error')  is not None:
      continue
    # 画像が解析不能なの　
    try: 
      ds = dict([(ds['description'], ds['score']) for ds in o['responses'].pop()['labelAnnotations']] )
    except Exception as e:
      continue
    dss.append( ds )

  tags_freq = {}
  for ds in dss:
    for tag in ds.keys():
      if tags_freq.get(tag) is None:
        tags_freq[tag] = 0
      tags_freq[tag] += 1

  # 5000を超えるので、5000個にタグを限定
  tags = []
  for tag, freq in sorted( tags_freq.items(), key=lambda x:x[1]*-1)[:5000]:
    print( tag, freq )
    tags.append( tag )
  #random.shuffle( tags )

  tag_index = {}
  for idx, tag in enumerate(tags):
    tag_index[tag] = idx

  open('tag_index.json','w').write( json.dumps( tag_index, indent=2 ) )


def _make_pair(name):
  tag_index = json.loads( open('tag_index.json','r').read() )
  try:
    filename = name.split('/').pop().replace('.json', '') 
    pkl_save_name = 'dataset/{}.pkl'.format(name.split('/').pop().replace('.json', ''))
    if os.path.exists(pkl_save_name):
      return
    try:
      img = Image.open(glob.glob('./imgs/{}.*'.format(filename)).pop())
    except OSError as e:
      print( e )
      return
    print( name )
    img = img.convert('RGB')  
    target_size = (224,224) 
    w, h = img.size
    if w > h :
      blank = Image.new('RGB', (w, w))
    if w <= h :
      blank = Image.new('RGB', (h, h))
    blank.paste(img, (0, 0) )
    blank = blank.resize( target_size )
    X = np.asanyarray(blank)
    X = X / 255.0
    y = [0.0]*5000
    try:
      obj  = json.loads( open(name).read() )
      obj = dict([(ds['description'], ds['score']) for ds in obj['responses'].pop()['labelAnnotations']] )
    except Exception as e:
      print( e, obj )
      return
    for tag, score in obj.items():
      #print( tag, score )
      if tag_index.get(tag) is None:
        continue
      y[ tag_index[tag] ] = score
    #print( [ y2 for y2 in y if y2 != 0.0 ] )
    open('dataset/{}.pkl'.format(name.split('/').pop().replace('.json', '')), 'wb').write( compress(pickle.dumps( (X, y) )) )
  except Exception as e:
    print( e )

import concurrent.futures 
if '--make_pair' in sys.argv:
  names = [name for name in glob.glob('./vision/*.json')]
  with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
    executor.map( _make_pair, names)
