# simple-benchmark

* uwsgi+gevent

  ```shell
  uwsgi --ini app.ini
  ```

* sanic

  ```shell
  python3 app.py
  ```

* koa

  ```shell
  nodejs app.js
  ```

* go

  ```shell
  go build app.go
  ./app
  ```

## wrk cmd

```shell
wrk -t4 -c100 -d30s -T30s http://localhost:3000/
```