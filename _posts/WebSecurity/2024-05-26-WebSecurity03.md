---
title: "[Web Security] SQL Injection(1)_Burp Suite, 프록시 설정, CA인증서 등"       # 글 제목
date: 2024-05-26 23:22:00 +0900 # 작성 시간
categories: [SECURITY, WEB SECURITY]        # [대분류, 소분류]
tags: [security, web security, sqlinjection, burp suite, proxy, ca]     # 태그 (반드시 소문자로 시작 권장)
---
웹 서버와 DB 서버가 연동되는 웹 서비스 중 사용자의 입력을 받는 화면이(로그인, 검색 입력 창 등) 존재하고 입력 받는 문자열에 별도의 처리 없이 데이터베이스 조회를 위한 SQL 구문이 사용될 경우 정상적인 SQL 구문 인자 값의 변조를 통해 데이터베이스 접근 및 임의의 SQL Query문을 실행할 수 있다.

\* Burp Suite와 Chrome 진행 예정

## 1\. Burp Suite  설치 및 기본 설정
1. 기본 default로 Next 설치
[https://portswigger.net/burp/releases/professional-community-2024-4-4?requestededition=community&requestedplatform=](https://portswigger.net/burp/releases/professional-community-2024-4-4?requestededition=community&requestedplatform=)
![image](/assets/img/posts/WebSecurity/WebSecurity03_01.png)
![image](/assets/img/posts/WebSecurity/WebSecurity03_02.png)
![image](/assets/img/posts/WebSecurity/WebSecurity03_03.png)

## 2\. Java JDK 설치(정상적으로 Burp Suite 실행되지 않는 경우에만)

[https://www.oracle.com/kr/java/technologies/downloads/#jdk22-windows](https://www.oracle.com/kr/java/technologies/downloads/#jdk22-windows)

![image](/assets/img/posts/WebSecurity/WebSecurity03_04.png)

## 3\. Burp Suite 프록시 설정

1. 기본적으로 8080 포트 사용
(이미 8080 포트가 사용중이라면 Running에 체크 해제 되어 있을 것 -> 임의의 포트를 별도로 추가해서 사용해야함)
![image](/assets/img/posts/WebSecurity/WebSecurity03_05.png)

2. 브라우저에서 출발하는 패킷을 잡아 보는 것
![image](/assets/img/posts/WebSecurity/WebSecurity03_06.png)


3. 체크
(요청을 보내고 서버에서 돌아오는 패킷을 브라우저 앞에서 먼저 잡아 볼 때)
\-> Burp Suite를 껐다 켜면 체크가 풀림
![image](/assets/img/posts/WebSecurity/WebSecurity03_07.png)

## 4\. CA 인증서

http(80)보다 https(443)을 사용하는 곳이 더 많기 때문에 CA 인증서가 필요하다.

1. 연동된 Chrome 브라우저 오픈
![image](/assets/img/posts/WebSecurity/WebSecurity03_08.png)

2. 연동된 크롬 사용
![image](/assets/img/posts/WebSecurity/WebSecurity03_09.png)

3. **http://burp** 접속
![image](/assets/img/posts/WebSecurity/WebSecurity03_10.png)

4. 우측 CA 인증서 다운
![image](/assets/img/posts/WebSecurity/WebSecurity03_11.png)

5. 다운 받은 파일 실행
![image](/assets/img/posts/WebSecurity/WebSecurity03_12.png)

6. 인증서 설치
![image](/assets/img/posts/WebSecurity/WebSecurity03_13.png)

7. 로컬 컴퓨터에 설치
![image](/assets/img/posts/WebSecurity/WebSecurity03_14.png)

8. 신뢰할 수 있는 루트 인증 기관
![image](/assets/img/posts/WebSecurity/WebSecurity03_15.png)

9. 인증서 가져오기 완료
![image](/assets/img/posts/WebSecurity/WebSecurity03_16.png)

10. Burp Suite 재실행(인증서 적용)
다른 브라우저는 웬만하면 다 닫고
![image](/assets/img/posts/WebSecurity/WebSecurity03_17.png)

![image](/assets/img/posts/WebSecurity/WebSecurity03_18.png)
교육기간에만 접속 가능

>   
> 내용을 변조하는 유형의 공격은 모두 공격으로 간주되므로 실제 일반 사이트에는 절대 하면 안된다!!!!  
> (접속한 테스트 사이트에서만 진행 해야 함, 나도 쫄려서 직접 하지 못하고 정리해 놓은 캡처본 보고 공부함)
{: .prompt-warning }