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
import hashlib

SEED_EXIST          = True
SEED_NO_EXIST       = False
HEADER = {"Accept-Language": "ja,en-US;q=0.9,en;q=0.8", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36","Accept": "*/*", "Connection": "keep-alive" } 
# set default state to scrape web pages in Amazon Kindle
def get_html(url):
  request = urllib.request.Request(url=url, headers=HEADER)
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

def get_image(link, src, tags):
  HEADER['Referer'] = link
  request = urllib.request.Request(url=src, headers=HEADER)
  request.add_header('Referer', link)
  opener = urllib.request.build_opener()
  con = opener.open(request).read()
  name = hashlib.sha256(bytes(link, 'utf8')).hexdigest()
  open('imgs/{}.jpg'.format(name), 'wb').write(con)
  open('metas/{}.json'.format(name), "w").write( json.dumps({'name':name, 'tags': tags, 'link':link, 'src':src }) )
  print("発見した画像", tags, link, src)

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
  try:
    name = hashlib.sha256(bytes(link, 'utf8')).hexdigest()
    if os.path.exists('htmls/{}'.format(name)) is True:
      return [], []
    html, title, soup = get_html(link)
    open('htmls/{}'.format(name), 'w').write( html.decode() )
    if soup is None:
      return link, []
    internal_links = analyzing(link, soup)
    open('links/{}'.format(name), 'w').write( '\n'.join(internal_links) )
    return link, internal_links
  except Exception as e:
    print('Some Deep Error Occured', e)
    return link, []

if __name__ == '__main__':
  seed = 'https://pixabay.com/ja/%E3%83%90%E3%83%A9-%E3%83%94%E3%83%B3%E3%82%AF-%E3%83%94%E3%83%B3%E3%82%AF%E3%81%AE%E3%83%90%E3%83%A9-%E6%BA%80%E9%96%8B%E3%81%AE%E3%83%90%E3%83%A9-%E8%8A%B1-%E3%83%90%E3%83%A9%E3%81%AE%E5%92%B2%E3%81%8F-2892821/'
  links = {seed}
  while True:
    _links = set()
    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as executor:
      for _, ilinks in executor.map( _map, links):
        for ilink in ilinks:
          _links.add(ilink)
    links = _links
          
