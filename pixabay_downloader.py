import bs4
import sys
import urllib.request, urllib.error, urllib.parse
import http.client
from socket import error as SocketError
import ssl
import os.path
import argparse
import multiprocessing as mp
import datetime
import pickle as pickle
import plyvel
import re
import json
import random
import signal
import concurrent.futures
import time
from multiprocessing import Process
import http.cookiejar, random
import re
import shutil
import concurrent.futures 

SEED_EXIST          = True
SEED_NO_EXIST       = False
# set default state to scrape web pages in Amazon Kindle
def get_html(url):
  headers = {"Accept-Language": "en-US,en;q=0.5","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Accept": "*/*", "Referer": url,"Connection": "keep-alive" } 
  request = urllib.request.Request(url=url, headers=headers)
  opener = urllib.request.build_opener()
  try:
    html = opener.open(request).read()
  except Exception as e:
    print('Error', e)
    return (None, None, None)
    
  print(url)
  #print(html)
  soup = bs4.BeautifulSoup(html, "html.parser")
  title = (lambda x:str(x.string) if x != None else 'Untitled')(soup.title )
  return (html, title, soup)

def get_image(url, src, tags):
  headers = {"Accept-Language": "en-US,en;q=0.5","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Accept": "*/*","Referer": url, "Connection": "keep-alive"  } 
  request = urllib.request.Request(url=src, headers=headers)
  request.add_header('Referer', url)
  opener = urllib.request.build_opener()
  con = opener.open(request).read()
  """ illsut id """
  linker = src.split('/').pop()
  open('imgs/' + linker, 'wb').write(con)
  open('metas/{}.json'.format(linker), "w").write( json.dumps({'linker':linker + '.jpg', 'tags': tags, 'url':url, 'src':src }) )
  print("発見した画像", tags, url, src)

def analyzing(link, soup):
  for img in soup.find_all('img', {'itemprop': 'contentURL'}):
    src = img.get('src')
    alt = img.get('alt')
    get_image(link, src, alt)
  iternal_links = []
  for link in soup.find_all('a'):
    url = link.get('href')
    if url is None:
      continue
    if 'https:/pixabay.com/' in url or url[0] == '/':
      url = 'https://pixabay.com' + url if url[0] == '/' else url
      iternal_links.append( url )
  return iternal_links

def _map(link):
  #print(link)
  html, title, soup = get_html(link)
  if soup is None:
    return link, []
  internal_links = analyzing(link, soup)
  return link, internal_links

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Process Kindle Referenced Index Score.')
  parser.add_argument('--URL', help='set default URL which to scrape at first')
  parser.add_argument('--depth', help='how number of url this program will scrape')
  parser.add_argument('--mode', help='you can specify mode...')
  parser.add_argument('--refresh', help='create snapshot(true|false)')
  parser.add_argument('--file', help='input filespath')
  parser.add_argument('--active', help='spcific active thread number')

  args_obj = vars(parser.parse_args())
  depth    = (lambda x:int(x) if x else 300)( args_obj.get('depth') )
  mode     = (lambda x:x if x else 'undefined')( args_obj.get('mode') )
  refresh  = (lambda x:False if x=='false' else True)( args_obj.get('refresh') )
  active   = (lambda x:15 if x==None else int(x) )( args_obj.get('active') )
  filename = args_obj.get('file')

  seed = 'https://pixabay.com/ja/%E3%83%90%E3%83%A9-%E3%83%94%E3%83%B3%E3%82%AF-%E3%83%94%E3%83%B3%E3%82%AF%E3%81%AE%E3%83%90%E3%83%A9-%E6%BA%80%E9%96%8B%E3%81%AE%E3%83%90%E3%83%A9-%E8%8A%B1-%E3%83%90%E3%83%A9%E3%81%AE%E5%92%B2%E3%81%8F-2892821/'
  db = plyvel.DB('pixabay.ldb', create_if_missing=True)
  db.put(bytes(seed,'utf8'), pickle.dumps(False))

  while True:
    links = []
    for key, val in db:
      if pickle.loads(val) == False:
        links.append( key.decode('utf8') )

    #for link in links:
    _map(links[0])
    with concurrent.futures.ProcessPoolExecutor(max_workers=200) as executor:
      for _link, ilinks in executor.map( _map, links):
        db.put( bytes(_link, 'utf8'), pickle.dumps(True) )
        for ilink in ilinks:
          if db.get( bytes(ilink, 'utf8')) is None:
            db.put( bytes(ilink, 'utf8'), pickle.dumps(False))
  '''
  while True:
    links =  [ link for link, status in filter(lambda x:x[1] == False, link_status.items()) ]
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
      for ilinks in executor.map( _map, links):
        for ilink in ilinks: 
          if link_status.get(ilink) is None:
            link_status[ilink] = False
      for link in links:
        link_status[link] = True
  '''
