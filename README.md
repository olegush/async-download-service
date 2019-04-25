# Microservice for download photos

The microservice can to archive files on the fly by request and send them
to user. Archive does not save on server, its downloads asynchronously.

Files download to server via FTP or CMS admin according the structure:
```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```

For creating and downloading an archive user got a link like
`http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`.


## How to install

Python 3.7 and libraries from **requirements.txt** should be installed

```bash
pip install -r requirements.txt
```


## Quickstart

Run **server.py** with arguments:

```bash
python server.py [--logs] [--delay] [--dir]
```

The server will run on port 8080, then open [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
in your browser and click link in the bottom of the page.

For example:
```bash
$ python3.6 server.py --logs 1 --delay 0.01 --dir photos
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
08:29:01,903 INFO: 127.0.0.1 [25/Apr/2019:05:29:01 +0000] "GET / HTTP/1.1" 200 4379 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
08:29:02,409 INFO: 127.0.0.1 [25/Apr/2019:05:29:02 +0000] "GET /favicon.ico HTTP/1.1" 404 172 "http://0.0.0.0:8080/" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
08:29:04,448 INFO: Sending archive 7kna, chunk 5 bytes
08:29:04,459 INFO: Sending archive 7kna, chunk 194 bytes
08:29:04,470 INFO: Sending archive 7kna, chunk 254 bytes
08:29:04,480 INFO: Sending archive 7kna, chunk 60 bytes
08:29:04,490 INFO: Sending archive 7kna, chunk 328 bytes
08:29:04,501 INFO: Sending archive 7kna, chunk 67 bytes
..............
..............
..............
08:29:48,538 INFO: Sending archive 7kna, chunk 369 bytes
08:29:48,548 INFO: Sending archive 7kna, chunk 469 bytes
08:29:48,559 INFO: Sending archive 7kna, chunk 271 bytes
08:29:48,570 INFO: 127.0.0.1 [25/Apr/2019:05:29:04 +0000] "GET /archive/7kna/ HTTP/1.1" 200 1157301 "http://0.0.0.0:8080/" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
```


## How to deploy

```bash
python server.py [--logs] [--delay] [--dir]
```

Then redirect to microservice necessary requests, for example:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```


# Project Goals

The code is written for educational purposes on online-course for
web-developers [dvmn.org](https://dvmn.org/).
