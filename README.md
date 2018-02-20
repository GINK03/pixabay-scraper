# pixabay scraper
pixabayの画像のスクレイパーです  

ロシアにあるサービスっぽいですが、CDSなどでインフラが強力で太いです  

常識と倫理を守って利用しましょう  

## requrements
```console
python3.6
requests==2.18.1
numpy==1.14.0
Pillow==5.0.0
beautifulsoup4==4.6.0
```

## start
```console
$ python3 pixabay_downloader.py
```

## resume
何らかの影響でプログラムがクラッシュした場合、復元できます
```console
$ python3 recover.py
$ python3 pixabay_downloader.py --recover
```
