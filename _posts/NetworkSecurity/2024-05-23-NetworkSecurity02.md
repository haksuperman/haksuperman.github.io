---
title: "[Network Security] 네트워크 스캐닝 공격"      # 글 제목
date: 2024-05-23 22:48:00 +0900 # 작성 시간
categories: [SECURITY, NETWORK SECURITY]        # [대분류, 소분류]
tags: [security, network, nmap, nslookup, ping, tcp 하프오픈 스캔, traceroute, tracert, wireshark, 스캐닝, scanning]     # 태그 (반드시 소문자로 시작 권장)
---
스캔을 통해 서비스를 제공하는 서버의 작동 여부와 제공하고 있는 서비스를 확인할 수 있다. 스캐닝에 사용하는 프로토콜은 ICMP(3계층), TCP(4계층), UDP(4계층)로 나눌 수 있다.

## 1\. 네트워크 스캐닝 개요
-   개요
    -   스캐닝은 네트워크를 통해 제공하고 있는 서비스, 포트, HOST 정보 등을 알아내는 것을 의미
    -   TCP 기반의 프로토콜의 질의(Request) 응답(Response) 메커니즘
    -   대표적인 스캔 프로그램으로는 nmap
-   목적
    -   열려 있는 포트 확인
    -   제공하는 서비스 확인
    -   동작 중인 Daemon의 버전
    -   운영체제 종류 및 버전
    -   취약점

★ 인터넷을 하기 위해서는 MAC 주소, IP 주소, Port 주소를 알아야 통신이 가능함

-   MAC(하드웨어 주소) : 이더넷으로 물리적으로 내장되어 있는 고유한 주소 -> 2계층
-   IP(논리적인 주소) : 3계층
-   Port(논리적인 주소) : 4계층

★ PC가 서버를 찾아가는 방법

-   IP 주소(3계층)를 사용
-   동일 네트워크 안에서의 주소 구분은 MAC 주소(2계층) 사용
-   하나의 서버 안에서 HTTP(80), HTTPS(443), SSH(22), FTP(20,21) 등의 포트 주소를 사용

## 2\. 네트워크 스캐닝 절차

활동 범위 결정 -> 네트워크 목록 수집 -> DNS 질의 -> 네트워크 정찰

#### 1) 활동 범위 결정

공개 되어 있는 정보를 수집해 내가 쓸만한 데이터로 만드는 과정(OSINT)

\* OSINT : 공개된 정보를 수집하는 행위

#### 2) 네트워크 목록 수집

실제 핑이 나가지는 않지만 해당 웹 사이트에서 사용하는 주소 확인 가능<br>
(DB서버의 주소는 별도 행위가 필요)<br>
이외 대표적으로 nmap이라는 도구를 이용해 스캐닝 작업 가능!
![image](https://blog.kakaocdn.net/dna/daXvUK/btsHy0EX7FM/AAAAAAAAAAAAAAAAAAAAAA7b4-QVrt9QSLlTCVot11PzAYu7NolMtS2arGpZ-JGj/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=S1iSh77r%2BySunUoL9Nx7ldsfiwU%3D)

#### 3) DNS 질의

**nslookup**
nslookup 명령으로 dns 질의(역질의도 가능)
![image](https://blog.kakaocdn.net/dna/k9lbR/btsHA1BVopF/AAAAAAAAAAAAAAAAAAAAAHMsRh-L-5GikTSuTptocKf083sjQnfeDG_W_kIXx0QG/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=VDzQiwUz1VBZJikopx38GxKg%2FbQ%3D)

**dig(Domain Information Groper)**
-   nslookup에 대비 유연성 및 편의성, 출력의 명료성을 가진 DNS 쿼리 도구
-   별도 설치 필요
-   dig \[도메인명\]

**Whois Service**
-   등록자 및 도메인 이름
-   관리자 연락처
-   레코드 생성시기와 업데이트 시기
-   주 DNS 서버와 보조 DNS 서버  
    \-> 보다 다양한 정보 획득 가능
- whois에서 kisec.com 질의 했을 때 결과
![image](https://blog.kakaocdn.net/dna/bgr7rn/btsHAOJzuxJ/AAAAAAAAAAAAAAAAAAAAABStZBFpVUt1-p-K0OWL-5hDeOvIr2p7wa7hGQkmgt2i/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=0xSnvRRnvEHGNOZaZdfZNDFKErM%3D)

**intodsn.com**

-   도메인 레코드 정보 조회
    -   MX, SOA, NS 등 확인
    -   DNS 변경 이력 정보 확인

#### 4) 네트워크 정찰

**Tracert, Traceroute**

-   경로 추적
-   Tracert(Windows)
-   Traceroute(Unix/Linux)  
    \-> traceroute 자체는 7계층, 명령어들이 사용하는 프로토콜은 ICMP 3계층
- Windows 11에서 tracert 명령으로 8.8.8.8 질의 결과
![image](https://blog.kakaocdn.net/dna/IDSJ6/btsHy6dQfMy/AAAAAAAAAAAAAAAAAAAAAC5ctRPCvCKBeH5uI51FWc-lhncv96Fp9CeMy9j5GIA7/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=T568LMJXsqKqR48VdHpEscshla0%3D)
\-> 8.8.8.8로 가는 경로 추적(경로 중 있는 라우터들의 주소 출력, 최대 30개의 라우터를 거쳐 갈 수 있음)

**VisualRoute**

-   traceroute, tracert 보다 속도가 빠름
-   traceroute, tracert 보다 알아보기 쉬움

## 3\. 네트워크 스캐닝 종류

-   Ping & ICMP 스캔
    -   Ping은 네트워크와 시스템이 정상적으로 동작하는지 확인
    -   Echo Request와 Echo Reply를 이용한 방법
    -   ICMP(Internet Control Messaging Protocol)를 사용
-   오픈 스캔(Open Scan)
    -   TCP 3-Way-Handshake를 이용해 정상적인 연결을 바탕으로 Open된 포트 정보를 추출
    -   TCP connect 스캔  
        (Open된 포트의 경우 target 시스템에서 SYN/ACK 패킷이 응답/  
        Clouse된 포트의 경우 target 시스템에서 RST/ACK 패킷이 응답)
-   하프-오픈 스캔(Half-Open Scan)
    -   TCP 3-Way-Handshake 방식의 연결을 비정상적으로 종료하는 방식
        -   표적 시스템 로그에 기록되는 것을 피할 수 있으나 방화벽이나 IDS에는 탐지
        -   TCP 하프 오픈 스캔 : SYN을 보낸 후 표적에서 SYN/ACK 응답이 오면 표적 HOST가 살았다고 추측, 응답으로 ACK를 보내는 대신 RST를 보내 세션을 성립시키지 않도록 하여 로그를 남기지 않음
-   스텔스 스캔(Stealth Scan)
    -   세션을 완전히 성립하지 않고 공격 대상 시스템의 포트 활성화 여부를 알아내는 스캔
    -   시스템 세션 연결 관련된 로그가 남지 않음
    -   ACK, NULL, X-MAS 스캔 등이 존재
    -   X-MAS 스캔 : 모든 flag를 보내거나, FIN, PSH, URG 플래그를 보내는 스캔
    -   ACK or FIN 스캔 : ACK 또는 FIN 플래그를 보내는 스캔
    -   NULL 스캔 : flag를 하나도 포함하지 않는 패킷을 보내는 스캔
-   UDP 스캔
    -   대상 HOST에 UDP 패킷을 보냈을 때 닫힌 포트는 ICMP\_PORT\_UNREACHABLE 응답
    -   열린 포트는 아무 응답이 없는 방법을 이용
    -   더보기
        
        TCP와 UDP의 장점을 합친 QUIC라는 프로토콜도 존재함  
        (구글에서 서비스하는 대부분의 서비스들이 QUIC 프로토콜을 사용함 -> 유튜브를 와이어샤크로 캡쳐하면 QUIC로 확인됨)
        
-   TCP 스캔
    -   TCP 오픈스캔
        -   포트가 열렸을 때 : (1) Attacker \[SYN\]  /  (2) Victim \[SYN+ACK\]  /  (3) Attacker \[ACK\]
        -   포트가 닫혔을 때 : (1) Attacker \[SYN\]  /  (2) Victim \[RST+ACK\]
    -   TCP 하프오픈 스캔
        -   포트가 열렸을 때 : (1) Attacker \[SYN\]  /  (2) Victim \[SYN+ACK\]  /  (3) Attacker \[RST\]
        -   포트가 닫혔을 때 : (1) Attacker \[SYN\]  /  (2) Victim \[RST+ACK\]
        -   흔적을 남기지 않기 위해 RST 패킷을 보내 연결을 끊음!