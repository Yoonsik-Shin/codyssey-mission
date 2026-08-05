# 내 컴퓨터에 개발자용 '작업실' 꾸미기

## 프로젝트 개요(미션 목표 요약)

이 미션은 개발 환경을 직접 구성하고, 터미널·Docker·Git/GitHub를 실제로 다루며 개발 워크스테이션을 만드는 과정을 기록하는 과제입니다.

핵심 목표는 다음과 같습니다.
- 터미널의 기본 조작 방식과 절대 경로/상대 경로, 파일 권한 개념을 이해한다.
- Docker를 설치하고, 이미지와 컨테이너의 차이를 이해하며, 컨테이너를 실행/관리한다.
- Dockerfile을 기반으로 커스텀 이미지를 만들고, 포트 매핑으로 웹 서버 접속을 검증한다.
- 바인드 마운트와 볼륨을 통해 "실시간 반영"과 "데이터 영속성"을 직접 확인한다.
- Git 사용자 설정과 GitHub 저장소 연동을 통해 로컬 버전 관리와 원격 협업의 흐름을 이해한다.

이 과정을 통해 단순히 도구를 설치하는 수준을 넘어, 왜 그 도구들이 필요한지와 어떤 역할을 하는지 설명할 수 있는 기반을 쌓는 것이 목적입니다.

## 실행 환경(OS/쉘/터미널, Docker 버전, Git 버전)
- 활용한 Shell 환경
```bash
$ echo $0
# -zsh
```
- 활용한 컴퓨터 프로세서 
```bash
# CPU(프로세서)의 정확한 명칭을 확인할 때 사용
$ sysctl -n machdep.cpu.brand_string
# Intel(R) Core(TM) i5-8600 CPU @ 3.10GHz
```
- 활용한 컴퓨터 사양
```bash
# 모델 식별자, 프로세서 이름, 코어 개수, 메모리 등 핵심 하드웨어 정보
$ system_profiler SPHardwareDataType
# Hardware:
#     Hardware Overview:
#       Model Name: iMac
#       Model Identifier: iMac19,1
#       Processor Name: 6-Core Intel Core i5
#       Processor Speed: 3.1 GHz
#       Number of Processors: 1
#       Total Number of Cores: 6
#       L2 Cache (per Core): 256 KB
#       L3 Cache: 9 MB
#       Memory: 32 GB
#       System Firmware Version: 2094.80.5.0.0
#       OS Loader Version: 583~2317
#       SMC Version (system): 2.46f12
#       Serial Number (system): C02ZM0CKJV3Y
#       Hardware UUID: DDBE3D73-BD14-550E-96D1-F6AC52D86509
#       Provisioning UDID: DDBE3D73-BD14-550E-96D1-F6AC52D86509
```
- 사용한 OS 정보
```bash
# 현재 설치된 macOS의 버전 정보를 확인
$ sw_vers
# ProductName:		macOS
# ProductVersion:   15.7.4
# BuildVersion:		24G517
```
- 사용한 Docker 버전
```bash
$ docker --version
# Docker version 28.5.2, build ecc6942
```
- 사용한 Git 버전
```bash
# 현재 설치된 git 버전 확인
$ git --version
# git version 2.53.0
```

## 수행 항목 체크리스트(터미널/권한/Docker/Dockerfile/포트/볼륨/Git/GitHub)

- [x] 터미널 기본 조작 및 디렉터리 구조 정리
  - 현재 위치 확인, 목록 확인(숨김 파일 포함), 이동, 생성, 복사, 이동/이름 변경, 삭제
- [x] 파일 내용 확인 및 빈 파일 생성 실습
- [x] 파일/디렉터리 권한 확인 및 변경 실습
  - `ls -l`, `chmod` 등을 사용해 권한 의미와 변경 전/후 비교 기록
- [x] Docker 실행 환경 점검
  - `docker --version`, `docker info`(또는 동등 점검)로 Docker 엔진 상태 확인
- [x] Docker 기본 운영 명령 실습
  - `docker images`, `docker ps`, `docker ps -a`, `docker logs`, `docker stats` 실행 및 결과 기록
- [x] 컨테이너 실행 실습
  - `hello-world` 컨테이너 실행 성공 확인
  - `ubuntu` 컨테이너 실행 후 내부 명령(`ls`, `echo` 등) 수행 확인
- [x] 컨테이너 종료/유지 방식 관찰
  - `attach`/`exec` 차이를 직접 확인하고 간단히 정리
- [x] Dockerfile 기반 커스텀 이미지 제작
  - 기존 베이스 이미지를 선택하고 커스텀 포인트 적용
  - `docker build` 및 `docker run`으로 실행 성공 확인
- [x] 포트 매핑 및 접속 검증
  - `-p <host_port>:<container_port>`로 외부 접속 확인
  - `curl` 또는 브라우저 접속 결과 기록
- [x] 바인드 마운트 반영 검증
  - 호스트 파일 변경 후 컨테이너에서 반영 여부 확인
- [x] Docker 볼륨 생성 및 영속성 검증
  - 볼륨 생성, 컨테이너 연결, 컨테이너 삭제 후에도 데이터 유지 여부 확인
- [x] Git 사용자 정보 및 기본 브랜치 설정
  - `git config --list` 결과를 기록하고 브랜치 설정 완료
- [x] GitHub 저장소 연동 및 VSCode 연결
  - GitHub 로그인/저장소 연동 증거를 문서에 첨부
- [x] 보안/개인정보 보호 점검
  - 민감 정보가 문서, 로그, 스크린샷에 노출되지 않도록 주의

## 검증 방법(어떤 명령으로 무엇을 확인했는지) + 결과 위치 링크

아래 항목은 터미널에서 직접 수행한 명령과 그 결과를 확인하는 기준입니다.

1. 터미널 조작 검증
   - 확인 명령: `pwd`, `ls -la`, `mkdir`, `cp`, `mv`, `rm`, `cat`, `touch`
   - 확인 내용: 현재 위치, 숨김 파일 포함 목록, 디렉터리 생성/복사/이동/삭제, 파일 내용 확인, 빈 파일 생성
   - 결과 위치: 본 문서 하단의 `수행 로그(발췌)` 코드블록

2. 권한 실습 검증
   - 확인 명령: `ls -l`, `chmod 755`, `chmod 644`, `stat`
   - 확인 내용: 파일/디렉터리 권한이 변경 전/후에 어떻게 달라지는지 확인
   - 결과 위치: 본 문서 하단의 `권한 실습 로그`

3. Docker 설치/점검 검증
   - 확인 명령: `docker --version`, `docker info`, `docker images`, `docker ps`, `docker ps -a`
   - 확인 내용: Docker 엔진 상태, 이미지 목록, 실행 중/종료된 컨테이너 상태 확인
   - 결과 위치: 본 문서 하단의 `Docker 운영/검증 로그`

4. 컨테이너 동작 검증
   - 확인 명령: `docker run hello-world`, `docker run -it ubuntu bash`, `docker exec`, `docker logs`
   - 확인 내용: 컨테이너가 정상 실행되고, 내부 명령으로 결과를 확인할 수 있는지 검증
   - 결과 위치: 본 문서 하단의 `컨테이너 실행 실습 로그`

5. Dockerfile/포트 매핑 검증
   - 확인 명령: `docker build -t <image-name> .`, `docker run -d -p <host_port>:<container_port> ...`, `curl http://localhost:<host_port>`
   - 확인 내용: 커스텀 이미지가 빌드되고 컨테이너가 포트 매핑을 통해 외부에서 접근 가능한지 확인
   - 결과 위치: 본 문서 하단의 `Dockerfile 빌드/실행 로그` 및 `포트 매핑 접속 증거`

6. 바인드 마운트/볼륨 검증
   - 확인 명령: `docker run -v ...`, `docker volume create`, `docker exec ...`, `docker rm -f ...`
   - 확인 내용: 호스트 변경이 컨테이너에 반영되는지, 볼륨에 저장된 데이터가 컨테이너를 삭제한 뒤에도 유지되는지 확인
   - 결과 위치: 본 문서 하단의 `바인드 마운트 검증 로그` 및 `볼륨 영속성 검증 로그`

7. Git/GitHub 연동 검증
   - 확인 명령: `git config --list`, `git branch`, `git remote -v`
   - 확인 내용: 사용자 정보, 기본 브랜치, 저장소 원격 연결이 정상적으로 설정되었는지 확인
   - 결과 위치: 본 문서 하단의 `Git/GitHub 연동 로그`

## 수행 로그
- 현재 위치 확인
```bash
$ pwd
# /Users/aaa9460994/codyssey-mission
```

- 숨김 파일 포함 목록 확인
```bash
$ ls -la
# total 8
# drwxr-xr-x   5 aaa9460994  aaa9460994  160  8  5 15:54 .
# drwxr-x---+ 22 aaa9460994  aaa9460994  704  8  5 16:29 ..
# drwxr-xr-x  12 aaa9460994  aaa9460994  384  8  5 16:00 .git
# drwxr-xr-x   4 aaa9460994  aaa9460994  128  8  5 15:54 E1
# -rw-r--r--   1 aaa9460994  aaa9460994   19  8  5 15:54 README.md
```

### 권한 실습 로그
- 파일 생성
```bash
$ touch codyssey.txt
$ ls
# codyssey.txt    E1              README.md
```

-  파일 권한 확인
```bash
ls -l codyssey.txt
# -rw-r--r--  1 aaa9460994  aaa9460994  0  8  5 16:35 codyssey.txt
```

- 권한 변경
```bash
$ chmod 755 codyssey.txt
```

- 변경 후 권한 확인
```bash
$ ls -l codyssey.txt    
# -rwxr-xr-x  1 aaa9460994  aaa9460994  0  8  5 16:35 codyssey.txt
```

### Docker 운영/검증 로그
- Docker 버전 확인
```bash
$ docker --version
# Docker version 28.5.2, build ecc6942
```

- Docker 정보 확인
```bash
$ docker info
#Client:
# Version:    28.5.2
# Context:    orbstack
# Debug Mode: false
# Plugins:
#  buildx: Docker Buildx (Docker Inc.)
#    Version:  v0.29.1
#    Path:     /Users/aaa9460994/.docker/cli-plugins/docker-buildx
#  compose: Docker Compose (Docker Inc.)
#    Version:  v2.40.3
#    Path:     /Users/aaa9460994/.docker/cli-plugins/docker-compose
#
#Server:
# Containers: 0
#  Running: 0
#  Paused: 0
#  Stopped: 0
# Images: 0
# Server Version: 28.5.2
# Storage Driver: overlay2
#  Backing Filesystem: btrfs
#  Supports d_type: true
#  Using metacopy: false
#  Native Overlay Diff: true
#  userxattr: false
# Logging Driver: json-file
# Cgroup Driver: cgroupfs
# Cgroup Version: 2
# Plugins:
#  Volume: local
#  Network: bridge host ipvlan macvlan null overlay
#  Log: awslogs fluentd gcplogs gelf journald json-file local splunk syslog
# CDI spec directories:
#  /etc/cdi
#  /var/run/cdi
# Swarm: inactive
# Runtimes: io.containerd.runc.v2 runc
# Default Runtime: runc
# Init Binary: docker-init
# containerd version: 1c4457e00facac03ce1d75f7b6777a7a851e5c41
# runc version: d842d7719497cc3b774fd71620278ac9e17710e0
# init version: de40ad0
# Security Options:
#  seccomp
#   Profile: builtin
#  cgroupns
# Kernel Version: 6.17.8-orbstack-00308-g8f9c941121b1
# Operating System: OrbStack
# OSType: linux
# Architecture: x86_64
# CPUs: 6
# Total Memory: 15.67GiB
# Name: orbstack
# ID: dd433b50-4a17-4e57-b2a9-8da414eb88a0
# Docker Root Dir: /var/lib/docker
# Debug Mode: false
# Experimental: false
# Insecure Registries:
#  ::1/128
#  127.0.0.0/8
# Live Restore Enabled: false
# Product License: Community Engine
# Default Address Pools:
#   Base: 192.168.97.0/24, Size: 24
#   Base: 192.168.107.0/24, Size: 24
#   Base: 192.168.117.0/24, Size: 24
#   Base: 192.168.147.0/24, Size: 24
#   Base: 192.168.148.0/24, Size: 24
#   Base: 192.168.155.0/24, Size: 24
#   Base: 192.168.156.0/24, Size: 24
#   Base: 192.168.158.0/24, Size: 24
#   Base: 192.168.163.0/24, Size: 24
#   Base: 192.168.164.0/24, Size: 24
#   Base: 192.168.165.0/24, Size: 24
#   Base: 192.168.166.0/24, Size: 24
#   Base: 192.168.167.0/24, Size: 24
#   Base: 192.168.171.0/24, Size: 24
#   Base: 192.168.172.0/24, Size: 24
#   Base: 192.168.181.0/24, Size: 24
#   Base: 192.168.183.0/24, Size: 24
#   Base: 192.168.186.0/24, Size: 24
#   Base: 192.168.207.0/24, Size: 24
#   Base: 192.168.214.0/24, Size: 24
#   Base: 192.168.215.0/24, Size: 24
#   Base: 192.168.216.0/24, Size: 24
#   Base: 192.168.223.0/24, Size: 24
#   Base: 192.168.227.0/24, Size: 24
#   Base: 192.168.228.0/24, Size: 24
#   Base: 192.168.229.0/24, Size: 24
#   Base: 192.168.237.0/24, Size: 24
#   Base: 192.168.239.0/24, Size: 24
#   Base: 192.168.242.0/24, Size: 24
#   Base: 192.168.247.0/24, Size: 24
#   Base: fd07:b51a:cc66:d000::/56, Size: 64
#
# WARNING: DOCKER_INSECURE_NO_IPTABLES_RAW is set
```

- Docker 로그 확인
```bash
$ docker logs --tail 10 kind_cerf
# 192.168.215.1 - - [05/Aug/2026:08:21:08 +0000] "GET / HTTP/1.1" 200 88 "-" "curl/8.7.1" "-"
# 192.168.215.1 - - [05/Aug/2026:08:35:40 +0000] "GET / HTTP/1.1" 200 88 "-" "curl/8.7.1" "-"
```

- Docker 리소스 상태 확인
```bash
$ docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}'
# NAME        CPU %     MEM USAGE / LIMIT     NET I/O
# kind_cerf   0.00%     4.934MiB / 15.67GiB   3.02kB / 1.62kB
```

### 컨테이너 실행 실습 로그
- hello-world 컨테이너 실행
```bash
$ docker run hello-world
# Unable to find image 'hello-world:latest' locally
# latest: Pulling from library/hello-world
# 4f55086f7dd0: Pull complete 
# Digest: sha256:7f4da0fc94bcece205a8c0b6f4d11c8196924654ffe5c4d1aa439b7f632048b2
# Status: Downloaded newer image for hello-world:latest
# 
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
# 
# To generate this message, Docker took the following steps:
#  1. The Docker client contacted the Docker daemon.
#  2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
#     (amd64)
#  3. The Docker daemon created a new container from that image which runs the
#     executable that produces the output you are currently reading.
#  4. The Docker daemon streamed that output to the Docker client, which sent it
#     to your terminal.
# 
# To try something more ambitious, you can run an Ubuntu container with:
#  $ docker run -it ubuntu bash
# 
# Share images, automate workflows, and more with a free Docker ID:
#  https://hub.docker.com/
# 
# For more examples and ideas, visit:
#  https://docs.docker.com/get-started/
```

- ubuntu 컨테이너 실행 후 내부 명령어 실행
```bash
$ docker run -it ubuntu bash

'root@4dcbb70572c4:/#' $ ls
#bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
'root@4dcbb70572c4:/#' $ echo "Hello, Docker!"
# Hello, Docker!
'root@4dcbb70572c4:/#' $ exit
# exit
```

### Dockerfile 빌드/실행 로그
- Docker 이미지 빌드
```bash
$ docker build -t codyssey_e1_1_img ./E1/1
```

-  빌드된 이미지 확인
```bash
$ docker images
# REPOSITORY          TAG       IMAGE ID       CREATED         SIZE
# codyssey_e1_1_img   latest    7655c9899874   2 minutes ago   62.4MB
#ubuntu              latest    86a1a31fdd84   11 days ago     100MB
# hello-world         latest    e2ac70e7319a   4 months ago    10.1kB
```

- 컨테이너 실행
```bash
$ docker run -d -p 8080:80 codyssey_e1_1_img
# 6c88309f8ca2126082ecf6778052b95373ab02283bc589d60ce0abcd6bc2d305
```

- 실행 중인 컨테이너 확인
```bash
$ docker ps
# CONTAINER ID   IMAGE               COMMAND                   CREATED          STATUS          PORTS                                     NAMES
# 6c88309f8ca2   codyssey_e1_1_img   "/docker-entrypoint.…"   11 seconds ago   Up 11 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   kind_cerf
```

### 포트 매핑 접속 증거
- curl을 이용한 접속 확인
```bash
$ curl http://localhost:8080
# <!doctype html>
# <html>
#   <body>
#     <h1>Hello from Docker + Nginx</h1>
#   </body>
# </html>%               
```

### 바인드 마운트 검증 로그
- 호스트의 파일을 컨테이너에 바인드 마운트
```bash
$ docker run -v /Users/aaa9460994/codyssey-mission/E1/1/data:/data -it ubuntu bash
```
- 컨테이너 내부에서 파일 생성
```bash
'root@51ff914800b8:/#' $ echo "Hello, World!" > /data/hello.txt
```

- 컨테이너 종료 후 호스트에서 파일 확인
```bash
$ exit
# exit
$ cat /Users/aaa9460994/codyssey-mission/E1/1/data/hello.txt      
# Hello, World!
```

### 볼륨 영속성 검증 로그
- Docker 볼륨 생성
```bash
$ docker volume create codyssey-volume
# codyssey-volume
```

- 볼륨이 생성되었는지 확인
```bash
$ docker volume ls
# DRIVER    VOLUME NAME
# local     codyssey-volume
```

- 컨테이너 실행 시 볼륨 연결
```bash
$ docker run -d --name codyssey-container -v codyssey-volume:/data ubuntu sleep infinity
# 9a843ec5e35503e870a8d1869ba2431c884870c09c9a9bbcae144b27bfce4839
```

- 컨테이너 내부에서 데이터 생성
```bash
$ docker exec -it codyssey-container bash
# root@9a843ec5e355:/# echo "Persistent Data" > /data/data.txt
# root@9a843ec5e355:/# exit
```

- 컨테이너 삭제
```bash
$ docker rm -f codyssey-container
```

- 볼륨에 데이터가 남아있는지 확인
```bash
$ docker run -it --rm -v codyssey-volume:/data ubuntu cat /data/data.txt
# Persistent Data
```

### Git/GitHub 연동 로그
- Git 사용자 정보 확인
```bash
$ git config --list
# credential.helper=osxkeychain
# core.repositoryformatversion=0
# core.filemode=true
# core.bare=false
# core.logallrefupdates=true
# core.ignorecase=true
# core.precomposeunicode=true
# remote.origin.url=https://github.com/Yoonsik-Shin/codyssey-mission.git
# remote.origin.fetch=+refs/heads/*:refs/remotes/origin/*
# branch.master.remote=origin
# branch.master.merge=refs/heads/master
# branch.master.vscode-merge-base=origin/master
# branch.feature/E1/1.vscode-merge-base=origin/master
```

- 기본 브랜치 확인
```bash
$ git branch
# * feature/E1/1
#  master
```

- 원격 저장소 확인
```bash
$ git remote -v
# origin  https://github.com/Yoonsik-Shin/codyssey-mission.git (fetch)
# origin  https://github.com/Yoonsik-Shin/codyssey-mission.git (push)
```

- GitHub/VSCode 연동 증거
  - `git remote -v` 결과로 원격 저장소가 GitHub 리포지토리로 연결되어 있음을 확인
  - `git branch` 결과로 현재 작업 브랜치가 `feature/E1/1`로 설정되어 있음을 확인
  - VS Code의 Source Control 탭에서 동일 저장소가 연결된 상태로 관리되고 있음을 확인

## 트러블슈팅

### 트러블슈팅 1: `docker run hello-world` 후 컨테이너가 바로 종료되는 현상
- 문제: `docker ps -a` 또는 `docker ps -al`에서 `hello-world` 컨테이너가 `Exited (0)` 상태로 보이며, 계속 실행 중인 것으로 표시되지 않음
- 원인 가설: `hello-world` 이미지는 화면에 인사 메시지를 출력하고 즉시 종료하는 일회성 프로그램이기 때문임
- 확인: `docker run hello-world`의 출력 결과를 확인하면, 컨테이너가 메시지를 출력한 뒤 프로세스가 끝났다는 사실을 확인할 수 있음
- 해결/대안: 해당 이미지는 계속 대기하는 서버가 아니라, 실행 후 종료하는 동작을 수행하는 이미지이므로 정상적인 동작임. 계속 실행 중인 컨테이너를 확인하려면 `docker run -it ubuntu bash`처럼 쉘을 유지하거나, `nginx`처럼 장시간 실행되는 이미지로 실습을 이어가면 됨

이처럼 `hello-world`는 실행 후 결과를 출력하고 종료하는 구조라서, `docker ps -a`에서 `Exited (0)` 상태로 보이는 것이 정상입니다.

### 트러블슈팅 2: `COPY index.html` 단계에서 빌드가 실패한 문제
- 문제: `docker build -t codyssey_e1_1_img ./E1/1` 실행 시 `COPY index.html /usr/share/nginx/html/index.html` 단계에서 `"/index.html": not found` 오류가 발생함
- 원인 가설: 빌드 컨텍스트에 정상적인 `index.html` 파일이 없거나, 파일명이 의도와 다르게 생성되어 Docker가 해당 파일을 찾지 못하는 상태일 가능성이 있음
- 확인: `ls -lb E1/1` 명령으로 파일명을 점검했고, 실제로 파일명이 앞에 공백이 붙은 잘못된 이름으로 생성되어 있던 상태를 확인함
- 해결/대안: 잘못된 파일명을 정상적인 `index.html`로 정리한 뒤, 다시 `docker build -t codyssey_e1_1_img ./E1/1` 명령을 실행해 빌드가 정상 완료되는 것을 확인함

빌드 수정 후 확인 결과:
```bash
$ docker build -t codyssey_e1_1_img ./E1/1
# [+] Building 4.9s (7/7) FINISHED
# => [2/2] COPY index.html /usr/share/nginx/html/index.html
# => exporting to image
```

이 오류는 "파일이 없는 문제"처럼 보이지만, 실제로는 빌드 컨텍스트의 파일명/경로 불일치가 원인이었기 때문에, 파일명을 점검하는 과정이 중요함을 알 수 있습니다.

### 트러블슈팅 3: 컨테이너 이름 충돌로 `docker run`이 실패한 문제
- 문제: `docker run -d -v codyssey-volume:/data --name codyssey-container ubuntu` 실행 시 다음 메시지가 출력됨
```bash
# docker: Error response from daemon: Conflict. The container name "/codyssey-container" is already in use by container "a277cc87e74119ff3f2f0d14d512ecc2c20a4e59aee64b079128491a717d49e5". You have to remove (or rename) that container to be able to reuse that name.
```
- 원인 가설: 동일한 이름의 컨테이너가 이미 존재하기 때문에 Docker가 새로 생성하려는 컨테이너 이름을 중복으로 판단한 상태임
- 확인: `docker ps -a --filter name=codyssey-container` 또는 `docker ps -a`를 실행해 기존 컨테이너가 실제로 남아 있는지 확인함
- 해결/대안: 기존 컨테이너를 삭제한 뒤(`docker rm -f codyssey-container`) 다시 실행하거나, 다른 이름으로 새 컨테이너를 생성해 실습을 이어감 (`--name codyssey-container-2` 등)

즉, 이 오류는 볼륨 자체의 문제가 아니라, 컨테이너 이름이 이미 사용 중이어서 발생한 충돌이므로 이름을 정리하거나 삭제해야 함을 확인할 수 있습니다.


### 트러블슈팅 4: `docker exec` 실행 시 컨테이너가 바로 종료되어 들어가지 못한 문제
- 문제: `docker exec -it codyssey-container bash` 실행 시 `container ... is not running` 오류가 출력됨
- 원인 가설: `ubuntu` 이미지를 `-d` 옵션으로 실행했지만, 기본 실행 프로세스가 없어서 컨테이너가 곧바로 종료된 상태임
- 확인: `docker ps -a`로 상태를 확인하면 `Exited` 상태로 남아 있는 것을 확인할 수 있음
- 해결/대안: `docker exec`는 실행 중인 컨테이너에만 붙을 수 있으므로, `sleep infinity` 또는 `bash`로 컨테이너가 계속 유지되도록 재실행해야 함

예시:
```bash
$ docker run -d --name codyssey-container -v codyssey-volume:/data ubuntu sleep infinity
$ docker exec -it codyssey-container bash
```

또는 대화형으로 바로 진입:
```bash
$ docker run -it --name codyssey-container -v codyssey-volume:/data ubuntu bash
```

이 오류는 볼륨 문제라기보다, `docker exec` 대상이 이미 종료 상태였기 때문에 발생한 것입니다.

### Dockerfile 커스텀 포인트
- 선택한 베이스 이미지: `nginx:alpine`
- 이유: 경량화된 웹 서버 이미지라 정적 페이지를 빠르게 띄우고 포트 매핑 검증을 수행하기 적합함
- 적용한 커스텀 포인트
  - `COPY index.html /usr/share/nginx/html/index.html`: 기본 HTML 페이지를 교체해 내가 만든 정적 콘텐츠를 브라우저에서 보이도록 구성
  - `EXPOSE 80`: 컨테이너 내부에서 Nginx가 사용하는 기본 포트를 명시
  - `CMD ["nginx", "-g", "daemon off;"]`: Nginx를 포그라운드로 실행해 컨테이너가 종료되지 않도록 유지
