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

## 경로·권한·보안 설명
- 절대 경로와 상대 경로
  - 절대 경로는 작업 환경이 어디서 실행되든 항상 같은 위치를 가리키는 경로입니다. 예: `/Users/aaa9460994/codyssey-mission/E1/1/data`
  - 상대 경로는 현재 위치를 기준으로 해석되는 경로입니다. 예: `./E1/1` 또는 `../` 같은 표기
  - Docker 실행 시 호스트 경로를 바인드 마운트로 연결할 때는 재현성을 위해 절대 경로를 많이 사용하고, 저장소 내에서 작업할 때는 상대 경로를 사용해 문서화가 쉬워집니다.
- 파일 권한 숫자 해설
  - `755`는 소유자에게 `rwx`, 그룹과 기타 사용자에게 `r-x` 권한을 부여하는 의미입니다. 실행 파일이나 디렉터리처럼 접근 권한과 실행 권한이 함께 필요할 때 자주 사용합니다.
  - `644`는 소유자에게 `rw-`, 그룹과 기타 사용자에게 `r--` 권한을 부여하는 의미입니다. 일반 텍스트 파일에 주로 사용합니다.
  - 즉, `rwx`는 읽기/쓰기/실행, `rw-`는 읽기/쓰기, `r--`는 읽기만 허용하는 표준 규칙으로 해석합니다.
- 소유자·그룹·기타 사용자의 의미
  - macOS/Linux는 한 컴퓨터 안에 여러 사용자 계정이 존재할 수 있는 다중 사용자 시스템으로 설계되어 있고, 파일 권한은 이 계정 단위로 적용됩니다. 네트워크 접근 여부와는 무관한 개념입니다.
  - 소유자(owner/user): 파일을 생성한 계정. `ls -l` 결과의 세 번째 컬럼에 표시됩니다.
  - 그룹(group): 여러 계정을 묶은 단위로, `ls -l` 결과의 네 번째 컬럼에 표시됩니다. 같은 그룹에 속한 계정들에게 동일한 권한을 부여할 때 사용합니다. 파일의 그룹은 생성 시 소유자의 기본 그룹으로 지정되며, `chgrp`나 `chown user:group`으로 변경할 수 있습니다.
  - 기타(others): 소유자도 아니고 해당 그룹의 멤버도 아닌 나머지 모든 계정입니다.
  - 활용 예: 서버에서 웹서버 프로세스와 배포 계정을 같은 그룹으로 묶어 그룹에 `rw-`를 주고, 기타 권한은 `r--` 또는 `---`로 최소화해 외부 계정의 접근을 차단하는 식으로 사용합니다. `usermod -aG docker $USER`로 계정을 `docker` 그룹에 추가해 `sudo` 없이 Docker 명령을 실행하는 것도 같은 원리입니다.
  - 지금처럼 혼자 쓰는 개인 macOS 환경에서는 사실상 소유자 권한만 체감되고 그룹/기타 권한 차이는 크게 드러나지 않지만, 여러 계정이 접근하는 서버 환경에서는 의미가 뚜렷해집니다.
- Docker 네임스페이스/보안 측면
  - Docker 컨테이너는 호스트 커널 네임스페이스를 분리해 각 컨테이너가 별도의 PID, 네트워크, 마운트 공간을 갖도록 동작합니다.
  - 따라서 하나의 컨테이너가 다른 컨테이너에 직접 접근할 수 없도록 격리되며, 포트 노출은 필요한 경우에만 `-p`로 명시해 외부 접근을 허용하는 방식이 안전합니다.
  - 이 원칙은 호스트 자원의 침범을 줄이고, 동일한 서비스 환경을 여러 번 동일하게 실행하는 재현성에도 도움이 됩니다.
- 바인드 마운트와 볼륨의 차이
  - 볼륨(volume)은 Docker가 직접 만들고 관리하는 저장 공간입니다. `docker volume create`로 생성하며, 실제 데이터는 호스트의 `/var/lib/docker/volumes/<이름>/_data`에 저장되지만 사용자는 호스트 경로를 몰라도 볼륨 이름만으로 다룰 수 있습니다.
  - 바인드 마운트(bind mount)는 호스트의 특정 경로(`-v /host/path:/container/path`)를 컨테이너 경로에 그대로 연결하는 방식입니다. 호스트 파일시스템 구조를 그대로 노출하므로 경로가 실제로 존재해야 하고, 권한 관리도 사용자가 직접 신경 써야 합니다.
  - 핵심 차이는 관리 주체입니다. 바인드 마운트는 호스트가 주도하는 방식이라 호스트에서 파일을 고치면 컨테이너에 즉시 반영되어 개발 중 코드 변경을 실시간으로 확인할 때 적합합니다. 볼륨은 Docker가 주도하는 방식이라 컨테이너를 삭제해도 데이터가 남아 있어(영속성), DB 데이터처럼 컨테이너 생명주기와 무관하게 보존해야 하는 데이터에 적합합니다.
  - 이 문서의 `바인드 마운트 검증 로그`에서는 호스트 변경이 컨테이너에 즉시 반영되는 것을, `볼륨 영속성 검증 로그`에서는 컨테이너를 삭제해도 데이터가 유지되는 것을 각각 확인했습니다.

### 수행 로그
- 현재 위치 확인
```bash
$ pwd
# /Users/aaa9460994/codyssey-mission
```

- 숨김 파일 포함 목록 확인
```bash
# -l: 상세 정보(권한, 소유자, 크기, 수정일) 표시 / -a: 숨김 파일(.으로 시작) 포함
$ ls -la
# total 8
# drwxr-xr-x   5 aaa9460994  aaa9460994  160  8  5 15:54 .
# drwxr-x---+ 22 aaa9460994  aaa9460994  704  8  5 16:29 ..
# drwxr-xr-x  12 aaa9460994  aaa9460994  384  8  5 16:00 .git
# drwxr-xr-x   4 aaa9460994  aaa9460994  128  8  5 15:54 E1
# -rw-r--r--   1 aaa9460994  aaa9460994   19  8  5 15:54 README.md
```

- 이동/이름 변경 및 삭제 실습
```bash
# -p: 중간 경로 디렉터리가 없으면 함께 생성, 이미 있어도 에러 없이 통과
$ mkdir -p E1/1/worklog-demo
$ touch E1/1/worklog-demo/sample.txt

$ ls -la E1/1/worklog-demo
# total 0
# drwxr-xr-x  3 aaa9460994  aaa9460994   96  8  5 18:14 .
# drwxr-xr-x  7 aaa9460994  aaa9460994  224  8  5 18:14 ..
# -rw-r--r--  1 aaa9460994  aaa9460994    0  8  5 18:14 sample.txt

$ mv E1/1/worklog-demo/sample.txt E1/1/worklog-demo/moved.txt

$ ls -la E1/1/worklog-demo
# total 0
# drwxr-xr-x  3 aaa9460994  aaa9460994   96  8  5 18:14 .
# drwxr-xr-x  7 aaa9460994  aaa9460994  224  8  5 18:14 ..
# -rw-r--r--  1 aaa9460994  aaa9460994    0  8  5 18:14 moved.txt

# -r: 디렉터리 내부까지 재귀적으로 삭제 / -f: 확인 프롬프트 없이 강제 삭제
$ rm -rf E1/1/worklog-demo

$ ls -la E1/1
# total 80
# drwxr-xr-x  6 aaa9460994  aaa9460994    192  8  5 18:14 .
# drwxr-xr-x  4 aaa9460994  aaa9460994    128  8  5 15:54 ..
# drwxr-xr-x  3 aaa9460994  aaa9460994     96  8  5 17:59 data
# -rw-r--r--  1 aaa9460994  aaa9460994    111  8  5 17:59 Dockerfile
# -rw-r--r--  1 aaa9460994  aaa9460994     88  8  5 17:59 index.html
# -rw-r--r--  1 aaa9460994  aaa9460994  29379  8  5 18:06 README.md
# (worklog-demo 디렉터리가 목록에서 사라진 것으로 삭제 확인)
```

- 파일 내용 확인 및 빈 파일 생성 실습
```bash
$ cat README.md | head -3
# 내 컴퓨터에 개발자용 '작업실' 꾸미기
#
# ## 프로젝트 개요(미션 목표 요약)
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
# -l: 파일 권한/소유자/크기 등 상세 정보를 한 줄씩 표시
ls -l codyssey.txt
# -rw-r--r--  1 aaa9460994  aaa9460994  0  8  5 16:35 codyssey.txt
```

- 권한 변경
```bash
# 755: 소유자 rwx(7), 그룹 r-x(5), 기타 r-x(5) 부여
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

- Docker 정보 해석
  - `docker info`의 `Server Version: 28.5.2`는 Docker 엔진 자체의 버전을 의미하고, `Operating System: OrbStack`은 실제 엔진이 OrbStack 기반 Linux 환경에서 실행되고 있음을 뜻합니다.
  - `Containers: 0`, `Running: 0`, `Stopped: 0`은 아직 실습용 컨테이너가 없음을 보여주며, 이후 `docker run`으로 컨테이너가 생성되는 구조를 이해하는 데 도움이 됩니다.

- Docker 이미지 목록 확인
```bash
$ docker images
# REPOSITORY          TAG       IMAGE ID       CREATED         SIZE
# codyssey_e1_1_img   latest    7655c9899874   2 minutes ago   62.4MB
# ubuntu              latest    86a1a31fdd84   11 days ago     100MB
# hello-world         latest    e2ac70e7319a   4 months ago    10.1kB
```

- 전체 컨테이너 목록 확인 (`docker ps -a`)
```bash
# -a: 실행 중(Up)인 것뿐 아니라 종료(Exited)된 컨테이너까지 전부 표시
# --format: Go 템플릿으로 출력 컬럼을 원하는 형태로 지정
$ docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
# NAMES              IMAGE               STATUS                           PORTS
# vibrant_dubinsky   ubuntu              Exited (0) 37 minutes ago
# reverent_ride      ubuntu              Exited (127) 39 minutes ago
# kind_cerf          codyssey_e1_1_img   Up 43 minutes                    0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
# brave_satoshi      ubuntu              Exited (0) 58 minutes ago
# amazing_bose       ubuntu              Exited (130) About an hour ago
# hardcore_hugle     hello-world         Exited (0) About an hour ago
# upbeat_lovelace    hello-world         Exited (0) About an hour ago
```

- 컨테이너 삭제 전/후 `docker ps -a` 비교 (삭제 이력 확인)
```bash
# 1) 삭제 전: 데모용 컨테이너 실행
# -d: 백그라운드(detached)로 실행 / --name: 컨테이너 이름 지정
$ docker run -d --name codyssey-demo-cleanup ubuntu sleep infinity
# d41505572c21f5c09e1e00f0dc42de4342b6db4796eff3ff2ef904e460f67e48

$ docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
# NAMES                   IMAGE               STATUS
# codyssey-demo-cleanup   ubuntu              Up Less than a second
# vibrant_dubinsky        ubuntu              Exited (0) 49 minutes ago
# reverent_ride           ubuntu              Exited (127) 51 minutes ago
# kind_cerf               codyssey_e1_1_img   Up 55 minutes
# ...

# 2) 삭제
# -f: 컨테이너가 실행 중이어도 강제로 중지 후 삭제
$ docker rm -f codyssey-demo-cleanup
# codyssey-demo-cleanup

# 3) 삭제 후: 목록에서 codyssey-demo-cleanup이 사라진 것을 확인
$ docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
# NAMES              IMAGE               STATUS
# vibrant_dubinsky   ubuntu              Exited (0) 49 minutes ago
# reverent_ride      ubuntu              Exited (127) 51 minutes ago
# kind_cerf          codyssey_e1_1_img   Up 55 minutes
# ...
```

- Docker 로그 확인
```bash
# --tail 10: 전체 로그 대신 마지막 10줄만 출력
$ docker logs --tail 10 kind_cerf
# 192.168.215.1 - - [05/Aug/2026:08:21:08 +0000] "GET / HTTP/1.1" 200 88 "-" "curl/8.7.1" "-"
# 192.168.215.1 - - [05/Aug/2026:08:35:40 +0000] "GET / HTTP/1.1" 200 88 "-" "curl/8.7.1" "-"
```

- Docker 리소스 상태 확인
```bash
# --no-stream: 실시간 갱신 없이 현재 시점 값만 한 번 출력 / --format: 출력 컬럼 지정
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
# -i: 표준 입력을 열어둠(interactive) / -t: 터미널(tty) 할당, 둘을 합쳐 대화형 쉘 접속
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
# -t: 빌드 결과 이미지에 이름(태그)을 지정 / 마지막 인자는 빌드 컨텍스트(Dockerfile 위치) 경로
$ docker build -t codyssey_e1_1_img ./E1/1
# [+] Building 4.9s (7/7) FINISHED
# => [2/2] COPY index.html /usr/share/nginx/html/index.html
# => exporting to image
```

- 빌드된 이미지 확인
```bash
$ docker images
# REPOSITORY          TAG       IMAGE ID       CREATED         SIZE
# codyssey_e1_1_img   latest    7655c9899874   2 minutes ago   62.4MB
# ubuntu              latest    86a1a31fdd84   11 days ago     100MB
# hello-world         latest    e2ac70e7319a   4 months ago    10.1kB
```

- 컨테이너 실행
```bash
# -d: 백그라운드 실행 / -p host:container: 호스트 8080 포트를 컨테이너 80 포트로 매핑
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

- HTTP 상태 코드 확인
```bash
# -I: 본문 없이 응답 헤더(HTTP 상태 코드 포함)만 조회
$ curl -I http://localhost:8080
# HTTP/1.1 200 OK
# Server: nginx/1.31.3
# Content-Type: text/html
```

### 바인드 마운트 검증 로그
- 호스트의 파일을 컨테이너에 바인드 마운트
```bash
# -v host_path:container_path: 호스트 디렉터리를 컨테이너 경로에 그대로 연결(바인드 마운트)
# -it: 대화형 쉘로 접속(-i 표준 입력 유지 + -t 터미널 할당)
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

- 볼륨 상세 정보 확인
```bash
$ docker volume inspect codyssey-volume
# Mountpoint: /var/lib/docker/volumes/codyssey-volume/_data
# Name: codyssey-volume
# Driver: local
```

- 컨테이너 실행 시 볼륨 연결
```bash
# -d: 백그라운드 실행 / --name: 컨테이너 이름 지정
# -v volume_name:container_path: 이름 있는 Docker 볼륨을 컨테이너 경로에 연결(named volume)
$ docker run -d --name codyssey-container -v codyssey-volume:/data ubuntu sleep infinity
# 9a843ec5e35503e870a8d1869ba2431c884870c09c9a9bbcae144b27bfce4839
```

- 컨테이너 내부에서 데이터 생성
```bash
# -it: 실행 중인 컨테이너에 대화형 쉘로 접속(-i 표준 입력 유지 + -t 터미널 할당)
$ docker exec -it codyssey-container bash
# root@9a843ec5e355:/# echo "Persistent Data" > /data/data.txt
# root@9a843ec5e355:/# exit
```

- 컨테이너 삭제
```bash
# -f: 실행 중이어도 강제로 중지 후 삭제
$ docker rm -f codyssey-container
```

- 볼륨에 데이터가 남아있는지 확인
```bash
# -it: 대화형 실행 / --rm: 컨테이너 종료 시 자동 삭제(볼륨 자체는 유지됨) / -v: 기존 볼륨 재연결
$ docker run -it --rm -v codyssey-volume:/data ubuntu cat /data/data.txt
# Persistent Data
```

- 볼륨 데이터 백업 대안
  - 컨테이너가 쓰는 볼륨을 `tar`로 압축해 호스트에 백업하거나, 별도의 `ubuntu` 컨테이너를 통해 `/data` 경로만 다시 묶어 보관하는 방식으로 데이터 안전성을 확보할 수 있습니다.

## Git/GitHub 연동 로그
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
# * master
```

- 원격 저장소 확인
```bash
# -v: 원격 저장소 이름과 함께 fetch/push URL을 상세히(verbose) 표시
$ git remote -v
# origin  https://github.com/Yoonsik-Shin/codyssey-mission.git (fetch)
# origin  https://github.com/Yoonsik-Shin/codyssey-mission.git (push)
```

- GitHub 원격 푸시 기록
```bash
$ git push origin master
# Everything up-to-date
```

- GitHub/VSCode 연동 증거
  - `git remote -v` 결과로 원격 저장소가 GitHub 리포지토리로 연결되어 있음을 확인
  - `git branch` 결과로 현재 작업 브랜치가 `master`로 설정되어 있음을 확인
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

### 트러블슈팅 5: 포트 충돌로 컨테이너 실행이 실패한 문제
- 문제: `docker run -d -p 8080:80 codyssey_e1_1_img` 실행 시 이미 사용 중인 포트로 인해 실패하거나 연결이 되지 않음
- 원인 가설: 호스트에서 이미 다른 프로세스가 `8080` 포트를 점유하고 있거나, 이전에 같은 포트로 실행된 컨테이너가 남아 있는 상태일 가능성이 있음
- 확인: `lsof -nP -iTCP:8080 -sTCP:LISTEN` 또는 `docker ps`로 현재 포트 사용자를 확인하고, `docker ps -a`에서 기존 컨테이너 상태를 점검함
- 해결/대안: 포트를 점유한 프로세스를 정리하거나, 다른 host port로 바꿔서 실행 (`-p 8081:80`) 함. 이 과정을 통해 포트 매핑은 단순히 컨테이너의 내부 주소를 공개하는 것이 아니라, 호스트와 컨테이너 사이의 연결 규칙을 정의하는 기능임을 이해할 수 있음

### Dockerfile 커스텀 포인트
- 선택한 베이스 이미지: `nginx:alpine`
- 이유: 경량화된 웹 서버 이미지라 정적 페이지를 빠르게 띄우고 포트 매핑 검증을 수행하기 적합함
- 적용한 커스텀 포인트
  - `COPY index.html /usr/share/nginx/html/index.html`: 기본 HTML 페이지를 교체해 내가 만든 정적 콘텐츠를 브라우저에서 보이도록 구성
  - `EXPOSE 80`: 컨테이너 내부에서 Nginx가 사용하는 기본 포트를 명시
  - `CMD ["nginx", "-g", "daemon off;"]`: Nginx를 포그라운드로 실행해 컨테이너가 종료되지 않도록 유지
