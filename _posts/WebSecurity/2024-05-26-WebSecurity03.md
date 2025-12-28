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
![image](https://blog.kakaocdn.net/dna/bAatJd/btsHCwpr1DU/AAAAAAAAAAAAAAAAAAAAAMbmqmRI2-dfW39KgJfY9b81eboydlcrP78vJFu87vT0/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=4itSxWomWDi4PknwOL17UzowDRk%3D)
![image](https://blog.kakaocdn.net/dna/Jv5ab/btsHBUYKAzm/AAAAAAAAAAAAAAAAAAAAAP5jioDr8a_73O5Um3NM4RtzX4ghi7gBE9w7T0_b4Lf3/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=RbtEYo5xf1xBhXpThYIL4X8Fb6c%3D)
![image](https://blog.kakaocdn.net/dna/cKkYrn/btsHCoyomnJ/AAAAAAAAAAAAAAAAAAAAAMjgk69RgEtTEgB4VH7Wlnlj9dGon3KoIaNhiE6WOAF6/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=b5jSoNku%2Bf0f3NeHHufiU9g18aU%3D)

## 2\. Java JDK 설치(정상적으로 Burp Suite 실행되지 않는 경우에만)

[https://www.oracle.com/kr/java/technologies/downloads/#jdk22-windows](https://www.oracle.com/kr/java/technologies/downloads/#jdk22-windows)

![image](https://blog.kakaocdn.net/dna/3DhOz/btsHDN4O73h/AAAAAAAAAAAAAAAAAAAAAJkzdmpG41OeSzYZV5eaUqG7-v2wS6aZJjUL0BxDgx6A/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=06nbH8C4cEOq5DI%2B3oPOsAgEmCs%3D)

## 3\. Burp Suite 프록시 설정

1. 기본적으로 8080 포트 사용
(이미 8080 포트가 사용중이라면 Running에 체크 해제 되어 있을 것 -> 임의의 포트를 별도로 추가해서 사용해야함)
![image](https://blog.kakaocdn.net/dna/bNmlCv/btsHCorCmgD/AAAAAAAAAAAAAAAAAAAAAOc3qzGlqBN1b-k-zFZts_Kn8wN3y1g8_OPPef4kWPbs/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=yxB645GcJATzdoMbG9c0LkZUuBk%3D)

2. 브라우저에서 출발하는 패킷을 잡아 보는 것
![image](https://blog.kakaocdn.net/dna/rMqwh/btsHCy8vcUN/AAAAAAAAAAAAAAAAAAAAAJIOqA_FsCLiIzXdihydRuRj-YjTqhLl0KY-CRcCBWx5/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=QsIduGZqf4IDXrYYyyCEeakim98%3D)


3. 체크
(요청을 보내고 서버에서 돌아오는 패킷을 브라우저 앞에서 먼저 잡아 볼 때)
\-> Burp Suite를 껐다 켜면 체크가 풀림
![image](https://blog.kakaocdn.net/dna/HAxrk/btsHCzsQA3s/AAAAAAAAAAAAAAAAAAAAAK2uBFNpL-_H-roNt1LeeLmHykapMAZ-_fIwxqw5RcBm/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=50j%2FkHYLWZQoDg7%2FqVv0nbfCNlo%3D)

## 4\. CA 인증서

http(80)보다 https(443)을 사용하는 곳이 더 많기 때문에 CA 인증서가 필요하다.

1. 연동된 Chrome 브라우저 오픈
![image](https://blog.kakaocdn.net/dna/bQY4Ig/btsHB5Z9N7m/AAAAAAAAAAAAAAAAAAAAAGWSpObFLhjNQiCKa-leBOWWVUOLkMSqE98QcdqneO5S/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=t3SanClZlTwNi2a88qCUL18pAwA%3D)

2. 연동된 크롬 사용
![image](https://blog.kakaocdn.net/dna/dgEQyv/btsHDGktiqt/AAAAAAAAAAAAAAAAAAAAAHtTEQt_coyBs5xQ4ah-zf5uEaFpBi_0DuBvQv6ZY66U/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=CMJEzZI%2B7vu1Ccray43VuMPbE0I%3D)

3. **http://burp** 접속
![image](https://blog.kakaocdn.net/dna/07fLN/btsHDbryvMf/AAAAAAAAAAAAAAAAAAAAAHbIrgXR585I2nGkyfJYcqZY2d-bTqFYCjlqbdBUdUPS/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=ArXG%2F9FLznspMSaRJBpPGsEOZMw%3D)

4. 우측 CA 인증서 다운
![image](https://blog.kakaocdn.net/dna/pjvJO/btsHBSms5ac/AAAAAAAAAAAAAAAAAAAAABY6T1XhyYabTss9sYJ0uQQBaN0U8HqZ6m92F-ZBjcUG/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=eoMSCUWb2meWlPq81JmTgA6veC4%3D)

5. 다운 받은 파일 실행
![image](https://blog.kakaocdn.net/dna/ssXlK/btsHBM0ZcFF/AAAAAAAAAAAAAAAAAAAAAKJBQLyc5SSV4zPpfdxtZgPlhlD2pPTt5xiwD3SfJw2O/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=dwaSwrHgoWi27caVSliPUBYy%2BOw%3D)

6. 인증서 설치
![image](https://blog.kakaocdn.net/dna/dNhS4W/btsHCk3NMxQ/AAAAAAAAAAAAAAAAAAAAAD2usSkVZcm9xCOqdT44chOkLylH3mxB05SLTWbvmdyk/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=LHLbVw6%2FkNeTo6HIcZYIqru5q6s%3D)

7. 로컬 컴퓨터에 설치
![image](https://blog.kakaocdn.net/dna/IE98J/btsHDVPeps7/AAAAAAAAAAAAAAAAAAAAAKf6E8TJzyrLu-bYyWlv2IfXNjo3iI4BfISpA3Iq19Vs/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=fbl5GOX6dxide9o3NSqojsKWwbU%3D)

8. 신뢰할 수 있는 루트 인증 기관
![image](https://blog.kakaocdn.net/dna/6saZU/btsHDg7oybY/AAAAAAAAAAAAAAAAAAAAAArQOBBCsZXZ0H40MtsdSgp2YaASV2MHHDobkxWeDHan/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=n5L1p1j7TSTItKKlR6iIuR7QZ3U%3D)

9. 인증서 가져오기 완료
![image](https://blog.kakaocdn.net/dna/BOREm/btsHDVhpfSc/AAAAAAAAAAAAAAAAAAAAAG7J3PgbGlOlfdefK1kn-Cw004EncfTzubr0lBt1ZmPY/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=tRLv%2FJwtgGBYIZAcoINq6CBwXVs%3D)

10. Burp Suite 재실행(인증서 적용)
다른 브라우저는 웬만하면 다 닫고
![image](https://blog.kakaocdn.net/dna/bG04AX/btsHDHDGugv/AAAAAAAAAAAAAAAAAAAAAH998ayzKEahDDz9PtixMaBXjRnylbmwmd8k2yjPtoGW/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=xKG3dtFX2hrcj2FPLUzqaBnyPBo%3D)

![image](https://blog.kakaocdn.net/dna/b72Jsi/btsHBNS98aO/AAAAAAAAAAAAAAAAAAAAAMsTXeoPOw8ZgnStZXNfF92G8lgFwvNNkxml8nwnLaXf/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=ZH4gwS%2BMHU5kJUyJNfNDs0crxzo%3D)
교육기간에만 접속 가능

>   
> 내용을 변조하는 유형의 공격은 모두 공격으로 간주되므로 실제 일반 사이트에는 절대 하면 안된다!!!!  
> (접속한 테스트 사이트에서만 진행 해야 함, 나도 쫄려서 직접 하지 못하고 정리해 놓은 캡처본 보고 공부함)
{: .prompt-warning }