---
title: "[Web Security] 쇼단(Shodan), Censys, GHDB"       # 글 제목
date: 2024-05-26 22:44:00 +0900 # 작성 시간
categories: [SECURITY, WEB SECURITY]        # [대분류, 소분류]
tags: [security, web security, shodan, censys, ghdb]     # 태그 (반드시 소문자로 시작 권장)
---
## 1\. 쇼단(Shodan)

구글이 컨텐츠를 검색하는 웹 서비스라면, 쇼단(Shodan)은 인터넷에 연결된 장치를 검색하는 웹 서비스이다.

[https://www.shodan.io](https://www.shodan.io)

1. 로그인을 진행해야 완전한 Searching을 할 수 있다.

2. 인터넷에 노출되어 있는 정보들을 가공해서 보기 편하게 모아 놓은 것(실제 해킹의 작업은 x)
![image](/assets/img/posts/WebSecurity/WebSecurity02_01.png)

3. IP와 서버 종류들도 확인 가능(더 취약한 웹 서버의 경우 버전 정보까지도 나올 수 있음 -> 버전 별로 노출된 취약점 확인 가능)
![image](/assets/img/posts/WebSecurity/WebSecurity02_02.png)

4. IP 혹은 IP 대역대로 검색할 때는 **net:** 을 붙여서 검색
![image](/assets/img/posts/WebSecurity/WebSecurity02_03.png)

## 2\. Censys

쇼단과 유사하게 장치와 서버를 찾아주는 웹 서비스이다.

[https://search.censys.io/](https://search.censys.io/)

1. 오픈된 포트도 검색 가능
![image](/assets/img/posts/WebSecurity/WebSecurity02_04.png)

2. 쇼단과 다르게 Censys는 ip 검색 시 net: 을 붙이지 않아도 되는데, Censys는 비회원 시 질의 제한이 있다.
![image](/assets/img/posts/WebSecurity/WebSecurity02_05.png)

## 3\. GHDB(Google Hacking Database)

구글 검색을 통해 수집할 수 있는 민감한 정보를 모아 놓은 데이터 베이스이다. Exploit Database에서 관리하고 운영한다.

[https://www.exploit-db.com/](https://www.exploit-db.com/)

[##_Image|kage@ymnQE/btsHDOvT3HK/AAAAAAAAAAAAAAAAAAAAAJe9kF_qhTVQSCoa4OusRLciRJJyd7OBrB1CBJtIMyfI/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&amp;expires=1767193199&amp;allow_ip=&amp;allow_referer=&amp;signature=VCeeVYs%2FTl7Ev%2FsfeIqlpijYupM%3D|CDM|1.3|{"originWidth":2560,"originHeight":1528,"style":"alignCenter","filename":"09_GHDB 메뉴 선택.png"}_##]

1. 구글 해킹 데이터베이스(GHDB)
![image](/assets/img/posts/WebSecurity/WebSecurity02_06.png)

3. 웹 서버가 기본적으로 제공하는 디렉터리 인덱스 -> 보안 상 비활성화 해야 함!
(디렉터리의 구조를 나열시켜줌)
![image](/assets/img/posts/WebSecurity/WebSecurity02_07.png)

4. 구글링하는 방식으로 index of 페이지 검색
![image](/assets/img/posts/WebSecurity/WebSecurity02_08.png)

> 허가 받지 않은 사이트는 국내 법상 해킹으로 간주될 위험이 있음!  
> (실제 뭘 들어가 보지는 않음...)
{: .prompt-warning }