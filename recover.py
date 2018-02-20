from pathlib import Path

import hashlib

import pickle

urls = set()
for name in Path('links/').glob('*'):
  for url in name.open():
    url = url.strip()
    ha  = hashlib.sha256(bytes(url, 'utf8')).hexdigest()

    if Path(f'htmls/{ha}').exists() is False:
      urls.add(url)

pickle.dump(urls, open('urls.pkl', 'wb'))
