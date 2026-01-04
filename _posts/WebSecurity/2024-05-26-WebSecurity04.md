---
title: "[Web Security] SQL Injection(2)_인증 우회, DB 획득"       # 글 제목
date: 2024-05-27 00:40:00 +0900 # 작성 시간
categories: [SECURITY, WEB SECURITY]        # [대분류, 소분류]
tags: [security, web security, sqlinjection]     # 태그 (반드시 소문자로 시작 권장)
---

> **이러한 실습은 항상 단순 실습용으로, 공부용으로만 진행하기!**<br>
> **실제 운영 중인 사이트에 시도조차 하지 말기!!! 철컹철컹**
{: .prompt-warning}

웹 서버와 DB 서버가 연동되는 웹 서비스 중 사용자의 입력을 받는 화면(로그인, 검색 입력 창 등)이 존재하고 입력 받는 문자열에 별도의 처리 없이 데이터베이스 조회를 위한 SQL 구문이 사용될 경우 정상적인 SQL 구문 인자 값의 변조를 통해 데이터베이스 접근 및 임의의 SQL Query문을 실행할 수 있다.

※ 이전 게시물에 이어 진행(여기서부턴 다시 진행하면서 캡처한 내용이 아닌, 캡쳐본을 따온 사진들이기 때문에 말끔하지 못함..)

[[Web Security] SQL Injection(1)_Burp Suite, 프록시 설정, CA인증서 등](https://haksuperman.github.io/posts/websecurity03.md)


## 1\. 취약점 개요

-   일반적인 사용자는 게시판의 검색을 이용하여 원하는 데이터를 검색하지만, 공격자는 게시판의 검색 부분에 SQL Injection 구문을 삽입하여 DB 정보 추출

## 2\. SQL Injection 위험성(인증 우회)

-   데이터베이스(DB)와 연동된 웹 애플리케이션에서 입력된 데이터에 유효성 검증을 하지 않을 경우, 공격자가 입력 폼 URL 입력란에 SQL 구문을 삽입하여 DB로부터 정보를 열람하거나 조작할 수 있다.
-   인증 우회
    -   사용자 인증 우회, 정상적인 사용자의 인증권한 획득 가능
    -   사용자 로그인 입력 값에 비정상적인 SQL Query 삽입
![image](/assets/img/posts/WebSecurity/WebSecurity04_01.png)
무조건 참을 반환하도록 입력한 것

## 3\. SQL Injection(인증 우회) 실습

1. 로그인 해보기
![image](/assets/img/posts/WebSecurity/WebSecurity04_02.png)

    > - ID : admin
    > - PASSWORD : ' or 1=1 --
    > IP는 상관 없이 패스워드에 항상 참이되는 공식을 넣어 패스워드 인증을 받도록 함
    {: .prompt-info }

2. admin 로그인 했는데 oyes 로그인 됨
강제 참을 반환하도록 했는데, DB에서 모든 회원을 찾았고 회원 중 가장 위에 있던 oyes 사용자로 로그인 된 것
![image](/assets/img/posts/WebSecurity/WebSecurity04_03.png)

    > ![image](/assets/img/posts/WebSecurity/WebSecurity04_04.png)
    > 패스워드가 이렇게 들어갔는데, 해당 조건문이 항상 참이 되어 버림(members 테이블의 모든 항목들이 참이 된 것)
    > \-> **SQL 구문에 대한 입력 값 검증이 되지 않았기 때문에** 비정상적인 SQL 구문으로 공격이 성공한 것
    {: .prompt-info }

## 4\. SQL Injection(인증 우회)의 다양한 공격 문자열

은 항상 참이 되는 값을 생각해서 시도해보기. 물론 실습용 사이트에^^

## 5\. SQL Injection의 위험성(DB 획득)

-   의도적으로 DB 에러메시지 유발, DB의 구조 파악 가능
-   사용자 입력을 받아 SQL Query문을 생성할 경우
    -   고의적으로 에러메시지가 발생하도록 유도 가능
    -   테이블명, 필드명 등과 같은 주요 정보 노출 가능
    -   DB의 구조 파악 및 2차 공격 시도

#### 1) db\_name()

-   db\_name()을 이용하여 Database명 파악
    -   Database의 이름을 문자열로 반환하는 MS-SQL 함수
-   결과값 문자열을 정수와 비교연산하도록 하여 에러를 유발시킴
    -   '시스템 구조 상 이렇기 때문에 잘못 됐어 제대로 다시 해줘' 안내를 해줄 때 정보 노출의 위험이 있다.

1. 로그인 시도
![image](/assets/img/posts/WebSecurity/WebSecurity04_05.png)

    > ID : aaaa<br>
    > PW : 'and db\_name() > 1 --<br>
    > db\_name() 함수를 사용해 숫자 1과 비교해 일부러 에러를 유발
    {: .prompt-info }

2. DB이름을 숫자 1과 비교하려하니, 에러 발생<br>
\-> DB 측 에러임을 유추 가능, 이때 DB명 노출
![image](/assets/img/posts/WebSecurity/WebSecurity04_06.png)

#### 2) having을 이용하여 테이블명과 첫 번째 컬럼명 파악

-   having은 group by 다음에 나옴(동일한 데이터를 group by로 묶고 having으로 조건 구문 사용)
-   의도적으로 having을 사용해 오류를 발생시킴(group by 없이 having을 쓰면 에러 발생)

1. 로그인 시도
![image](/assets/img/posts/WebSecurity/WebSecurity04_07.png)

    > ID : aaaa<br>
    > PW : 'having 1=1 --<br>
    > having을 쓰려면 테이블명 컬럼명이 필요하다<br>
    > ( group by \[테이블명\] having \[컬럼명\] )
    {: .prompt-info }

2. Members 테이블명에 num 컬러명 노출
![image](/assets/img/posts/WebSecurity/WebSecurity04_08.png)

#### 3) group by()를 이용하여 나머지 컬럼명 파악
1. 로그인 시도
![image](/assets/img/posts/WebSecurity/WebSecurity04_09.png)

    > ID : aaaa<br>
    > PW : 'group by (num) --
    {: .prompt-info }

2. 다음 컬럼명 확인 가능(집계함수 group by를 통해 뭘 할건지를 명시 안해서 에러 발생)
![image](/assets/img/posts/WebSecurity/WebSecurity04_10.png)