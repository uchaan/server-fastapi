MongoDB
=========

## 1. Shell

MongoDB shell 열기
```sh
$ mongo
```

MongoDB 프로세스 중지
```sh
$ sudo systemctl stop mongod
```

MongoDB 프로세스 재시작
```sh
sudo systemctl restart mogod
```

MongoDB DB 열람, 조작 예시
```sh
$ mongo
$ show dbs
$ use crayon
$ db
$ show collections
$ db.users.find()
$ db.users.drop()
```

## 2. Compass (GUI application)

[Compass 다운로드](https://www.mongodb.com/try/download/compass)

다운받아서 crayon 서버에 연결

* host: 127.0.0.1:27017
* SSH: crayon 서버



