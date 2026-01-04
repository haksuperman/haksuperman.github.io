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
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity04_01.png)

2. 방화벽 밀어버리기
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity04_02.png)
3. 데몬 재실행
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity04_03.png)

#### 2) 웹 서버 접속으로 배너 그래빙
운영체제와 웹 서버의 종류 확인 가능
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity04_04.png)

#### 3) hping3 명령으로 기본 네트워크 정보 수집(ping 명령과 유사)
-   네트워크 패킷 생성 및 분석 도구로, 주로 네트워크 테스트, 방화벽 규칙 검증, 포트 스캔 및 네트워크 공격 시뮬레이션 등에 사용됨

CentOS 7.6에 설치한 웹 서버에 패킷을 보내 확인
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity04_05.png)