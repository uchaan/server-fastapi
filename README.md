server-v3
=========
##### (Last update: 2022.06.11)


## 1. Environment
- Ubuntu 20.04.3 LTS
- Python 3.8.10

**********

## 2. Setup 

### 2.1 환경변수 설정
.env 파일에서 서버 동작에 필요한 값 설정 

### 2.2 python 가상환경 세팅 
```sh
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```
*********

## 3. 서버 실행
### 3.1 crayon 서버에 crayon 계정으로 접속했을 경우
```sh
$ start_production
```
(포트 번호 등 설정 바꾸려면 ~/.bashrc 에서 alias 수정)

### 3.2 새 환경에서 실행하는 경우
```sh
$ source ~/crayon-server-v2/.venv/bin/activate
$ cd ~/crayon-server-v2
$ tmux new -s session_name -n window_name
$ tmux ls
$ tmux attach-session -t {SESSION_NAME}
$ uvicorn app.main.app --host={HOST} --port {PORT}
# reload 모드
$ uvicorn app.main.app --reload --host={HOST} --port {PORT}
```

********


## 4. API 문서 (Swagger UI)
- http://{HOST}:{PORT}/docs

********

## 5. 기타

### 5.1 Google Cloud Storage (agora recording 저장소)
* 버킷 이름: crayon-cloud-recording
* recording/{date}/ 에 저장됨
* e.g. crayon-cloud-recording/recording/20220604/


### 5.2 MongoDB
(2022.06.11) 현재 Firestore 사용 중. 추후 MongoDB 이전 예정

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

### 5.3 NGINX
(2022.06.11) 현재 production 은 uvicorn 으로만 돌아가는 중. 추후 NGINX + gunicorn 으로 이전 계획

crayon 서버 nginx 환경
- NGINX 1.18.0

```sh
$ sudo apt-get install nginx
```

- NGINX reverse proxy config file
```sh
/etc/nginx/sites-available/crayon-server.conf
```

- log, error 파일 디렉토리 생성 (.conf 에서 변경가능)
```bash
$ mkdir /var/log/nginx/crayon-server/
```
- sites-enabled 에 심볼릭링크 만들어줘야 프록시 설정 적용됨
```sh
ln -s /etc/nginx/sites-available/crayon-server.conf /etc/nginx/sites-enabled/crayon-server.conf 
```

nginx + gunicorn 서버 실행

```sh
(.venv) $ gunicorn -k uvicorn.workers.UvicornWorker --access-logfile ./logs/gunicorn-access.log app.main:app --bind 0.0.0.0:8008 --workers 12 --daemon 
```
args:
- `--workers`: 코어 개수
- `--bind`: 0.0.0.0:{port#}
- `--access-logfile`: Gunicorn 로그파일

프로세스 실행 확인
```sh
$ ps -ef | grep gunicorn
```

프로세스 종료
```sh
$ pkill gunicorn
```
1. gunicorn 으로 main.py 실행시킴. (다른 포트로 여러개 생성)
2. nginx -t 로 nginx 시작 가능 여부 테스트. 
3. 2 에서 에러없으면 sudo systemctl restart nginx 로 nginx 재시작. 
4. http://{domain}:{nginx-webserver-portnum}/docs 로 프록시 잘 실행되는지 확인







