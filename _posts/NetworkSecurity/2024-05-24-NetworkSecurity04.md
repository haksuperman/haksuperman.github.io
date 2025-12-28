---
title: "[Network Security] 배너그래빙(Banner Grabbing)(with. 기본 hping3 명령)"      # 글 제목
date: 2024-05-24 20:31:00 +0900 # 작성 시간
categories: [SECURITY, NETWORK SECURITY]        # [대분류, 소분류]
tags: [security, network, hping3, banner grabbing, 배너그래빙]     # 태그 (반드시 소문자로 시작 권장)
---
Telnet과 같이 원격지의 시스템에 로그인을 시도하였을 때 나타나는 안내문을 배너(Banner)라고 한다. 이러한 배너는 기본적으로 애플리케이션의 버전 등을 나타내기 때문에 이를 통해 기본적인 정보 수집이 가능하다.

80, 25, 3306 포트를 통해 각 서버의 정보 확인 가능

(21, 23, 25, 110, 143 포트에서도 가능)

## 1\. 운영체제 버전과 커널 버전 확인 가능

#### 1) CentOS 7.6 웹 서버 설정
1. httpd 설치
![image](https://blog.kakaocdn.net/dna/OaV5U/btsHCz6LSaw/AAAAAAAAAAAAAAAAAAAAAKfpxlIesHpZ_0QUg4nY5EIr6ehvHo0qKGEw6jEk_f8y/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=emA66U9csx7iFtDVhW7o4HJ3YbQ%3D)

2. 방화벽 밀어버리기
![image](https://blog.kakaocdn.net/dna/cKRXyc/btsHBMMPhw5/AAAAAAAAAAAAAAAAAAAAAHg_PLjw90jAqhZJRs-vW5aTnT3kMHic_IPtkNfCgj8v/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=j62FE8yHdWSPq2J8mVCgVll%2F%2Bak%3D)

3. 데몬 재실행
![image](https://blog.kakaocdn.net/dna/kBjcs/btsHBTZf0dG/AAAAAAAAAAAAAAAAAAAAACzt0GkYe3TXa-uFc8VZyZMH74EaHweUVPLJKaCixg5i/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=3KVvGDHdTzoBRbEWr%2BX2nblQQlo%3D)

#### 2) 웹 서버 접속으로 배너 그래빙
운영체제와 웹 서버의 종류 확인 가능
![image](https://blog.kakaocdn.net/dna/bLcH96/btsHCudkp7E/AAAAAAAAAAAAAAAAAAAAAMnnTwURuofsCCE35dbdWEMHNx-oGSUe9Mi-BPzfYjfy/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=xSPUpSR6dmR4Omr5oRt9MBJIh5s%3D)

#### 3) hping3 명령으로 기본 네트워크 정보 수집(ping 명령과 유사)
-   네트워크 패킷 생성 및 분석 도구로, 주로 네트워크 테스트, 방화벽 규칙 검증, 포트 스캔 및 네트워크 공격 시뮬레이션 등에 사용됨

CentOS 7.6에 설치한 웹 서버에 패킷을 보내 확인
![image](https://blog.kakaocdn.net/dna/b6NuA0/btsHBmAVylL/AAAAAAAAAAAAAAAAAAAAAKofQAeBZwlUF9ZG7I5JuSFSMtawwhOdxmjaip3UUbUi/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=4NWUCeql3pdlpP7r9z2j9hfbKYM%3D)