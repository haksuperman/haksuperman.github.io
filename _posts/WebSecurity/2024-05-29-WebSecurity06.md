---
title: "[Web Security] 파일 업로드 공격"       # 글 제목
date: 2024-05-29 22:25:00 +0900 # 작성 시간
categories: [SECURITY, WEB SECURITY]        # [대분류, 소분류]
tags: [security, web security, file upload]     # 태그 (반드시 소문자로 시작 권장)
---
웹 애플리케이션 개발/운영 환경에서 공격자가 실행 가능한 언어로 작성된 공격 프로그램을 업로드한 후 원격 해당 파일에 접근하여 실행시키는 취약점이다.

## 1\. 파일 업로드 해킹 방법

#### 1) 공격자가 실행 가능한 언어로 작성된 공격 프로그램을 업로드

-   업로드 기능 이용
-   개발/운영 환경 : JAVA / .NET / PHP
    -   JAVA 환경에서 실행 가능한 언어로 작성된 파일 : .jsp 등
    -   .NET 환경에서 실행 가능한 언어로 작성된 파일 : .asp 등
    -   PHP 환경에서 실행 가능한 언어로 작성된 파일 : .php 등

1. .asp 환경임을 확인
![image](https://blog.kakaocdn.net/dna/wF1Y9/btsHGdD2ShO/AAAAAAAAAAAAAAAAAAAAAJVB4XjVoq3olruxdGFw8byMNWujKlWAPIwJfjtgegCF/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=%2B%2FrAJAL1MHwrhLBfzYKZcfPBUxU%3D)

#### 2) 업로드한 악성 파일을 실행

-   업로드 한 파일은 서버측 업로드 전용 폴더를 만들어 놓았을 때 보통 해당 폴더에 저장됨
-   공격자는 업로드 파일 위치한 경로명(폴더 이름)을 알아내고, URL 직접 접근을 통해 실행함

실습을 위해 백신을 꺼야함! 악성 파일임을 확인하고 바로 삭제시키기 때문 -> **실습이 끝나면 바로 백신 켜기!!!**


1. GitHub에 공개된 webshell 파일 다운
![image](https://blog.kakaocdn.net/dna/dr8bb6/btsHGCKcsuk/AAAAAAAAAAAAAAAAAAAAAFzpVv3QRKH-Yp07dYVc_k140M1UvvDfI4dB_TSRwXYK/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=7h0QHliuRqm5GC1NUK4vCHktuKA%3D)
![image](https://blog.kakaocdn.net/dna/VlycQ/btsHGbGmwh4/AAAAAAAAAAAAAAAAAAAAAJdevwm7AEtx_9Uno1FyvgFtzmy0qBzB59U6gd1g8cLs/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=qE%2BRJz%2FSedHiG29Jsjx4SAw%2Bpac%3D)

> 웹 쉘(Webshell) : 서버에서 명령어를 실행할 수 있는 악성코드 파일
{: .prompt-info }


## 2\. 파일 업로드 취약점

#### 1) 취약성 및 위험성

-   애플리케이션의 개발, 운영 환경과 동일한 언어로 작성된 악성 파일을 웹 서버 측에 업로드
-   원격으로 해당 파일에 접근하여 실행시키는 취약점
-   작성된 공격 파일의 기능에 따라 다양한 위험 존재
-   Websehll 등의 파일을 이용한 시스템 장악 목적

#### 2) 진단 방법

-   게시판에 첨부파일 기능을 이용하여 가능 여부 확인
    -   게시판에 글쓰기 권한과 파일 첨부 기능이 있는지 확인한 후 확장자가 jsp/php/asp/cgi 등의 파일들이 업로드 가능한지 확인

1. 다운 받은 cmd.asp 파일 업로드 테스트
![image](https://blog.kakaocdn.net/dna/cdPDzT/btsHGAlok3c/AAAAAAAAAAAAAAAAAAAAAOOTAW-mAE_rh9vgsHWyfJPGe-fBvzWQaxmsRWOkw4mA/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=zkDuU1ogk4WippjKm6ZFSoHxjW0%3D)

2. 특정 확장자만 업로드 가능
![image](https://blog.kakaocdn.net/dna/bMhEaL/btsHHhrU7Va/AAAAAAAAAAAAAAAAAAAAADMhp_RdqnfBXiBhMIrxDeGh_1a3Qp7MAMNMpbhB1COu/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=2FtijneiATgdpPyB9QveEb945s0%3D)

## 3\. 우회 기법

#### 1) 대소문자 우회 공격

-   확장자를 비교할 경우 대소문자를 무시한 문자열 비교를 해야 함
-   대소문자 혼합도 시스템에서는 인식하기 때문에 모든 가능한 문자 조합에 대한 필터링 필요
-   Ex) **".aSp"**, **".Jsp"**, **".phP"**, **".eXe"** 등등


1. .aSp 확장자로 업로드 시도
![image](https://blog.kakaocdn.net/dna/c5XOVz/btsHGX1Grtv/AAAAAAAAAAAAAAAAAAAAACSWFUeT7_5ItbTdZtTgng4dBOnjIwht14_PtE792qMF/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=ughWBJxyx0BU2R2fzPb0bTS86Hc%3D)

2. 대소문자 우회 공격 실패
![image](https://blog.kakaocdn.net/dna/bHOyB7/btsHHiqPEXd/AAAAAAAAAAAAAAAAAAAAAIcnJzF2IfQVoYoKTxohCn_I5ZwGGVjrlHZekT6b07ng/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=2kjZgk9sZe5XbzlKIukJh0yNJkA%3D)

#### 2) 확장자 연장 우회 공격

-   확장자 필터링을 조건문자 ('.')를 기준으로 앞쪽부터 유효한 파일인지 필터링하게 되면 공격 받을 수 있음
-   확장자 필터링을 조건문자 ('.')를 기준으로 맨 마지막부터 해야 함
-   Ex) **attack.txt.asp**

1. txt를 확장자로 인식하고 업로드 되도록 공격
![image](https://blog.kakaocdn.net/dna/EWM2U/btsHFQoWFkA/AAAAAAAAAAAAAAAAAAAAAIzbixDRVrLl6-X2QTvfgtLO4vwv52vEsXdOWHFPCAka/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=zYaxdofdv1l2%2FdViBLwAzKcMM8k%3D)

2. 확장자 연장 우회 공격 성공
확장자를 구분짓는 조건문자 ('.') 를 왼쪽부터 검사해서 txt를 확장자로 인식 한 것 -> 우측부터 검사하도록 해야 함!
![image](https://blog.kakaocdn.net/dna/bHfFAy/btsHGTZmrma/AAAAAAAAAAAAAAAAAAAAAJ-uymYNzmMTBdvd_cTPuGMvjyM8Au8v5ZuOuLCDWUaO/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=um4sNlAillugA%2Fc6VKHCXml5DH4%3D)

#### 3) 특수문자 우회 공격

-   종단문자를 이용한 우회 공격
-   Ex) **"%00"**, **"%ZZ"**, **"%09"**, **"%13"** \-> %가 들어갔다는 것은 URL 인코딩으로 판단 가능

1. URL Incode 확인
![image](https://blog.kakaocdn.net/dna/cpmHTw/btsHHtyRPVT/AAAAAAAAAAAAAAAAAAAAAB906Pk4QzkNMk8y-wWEjFq_VJ1gVgkF2wT_dQKPXPOT/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=oKj11vVyPRH642jsB%2FJRcbHyY0Y%3D)

2. %00이 Null인 것 확인
![image](https://blog.kakaocdn.net/dna/daTSmo/btsHGbNanoB/AAAAAAAAAAAAAAAAAAAAABUo3hOMlUPrTrZf_wv9eoASu0A95zVkHYlrZojomQky/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=1Rl0UTKJmwOuVnprcKSjov5XdzQ%3D)


3. %00이 Null 값(종단)을 의미하므로 cmd.asp 가 되는 것이다.
![image](https://blog.kakaocdn.net/dna/KF5sw/btsHF9BLIXm/AAAAAAAAAAAAAAAAAAAAADyh-dSL1d4IJwmxKusQoaFQ0HGAQqy4cjiO9JobmH0O/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=R5hipHBEQbRXGNtJn0huArPZDNQ%3D)

4. 업로드 성공
![image](https://blog.kakaocdn.net/dna/Lq4WR/btsHIaMl1iz/AAAAAAAAAAAAAAAAAAAAAA-7zZhiFTD4rA3nD5EB4NLjLxD34x07p8jljeXaNcUI/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1767193199&allow_ip=&allow_referer=&signature=L8%2Fo%2BSbroJkyiCxuQWS56VWaaF8%3D)