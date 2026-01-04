---
title: "[Web Security] XSS(Cross Site Script) - Reflected XSS(반사형)"       # 글 제목
date: 2024-05-27 22:28:00 +0900 # 작성 시간
categories: [SECURITY, WEB SECURITY]        # [대분류, 소분류]
tags: [security, web security, xss, cross site script, reflected xss]     # 태그 (반드시 소문자로 시작 권장)
---
XSS 취약점은 외부의 공격자가 클라이언트 스크립트를 악용하여 웹 사이트에 접속하려는 일반 사용자로 하여금 공격자가 의도한 명령이나 작업을 수행하도록 하는 공격이다. 공격자는 이 공격을 이용해서 악성 서버 유도, 사용자 쿠키 정보 추출을 통한 세션 가로채기 공격 등을 수행할 수 있다.

SQL 구문이 아닌 스크립트를 악용하는 기법으로, 로그인 한 피해자의 쿠키 값을 탈취하거나 악성 서버로 유도 되어서 악성코드를 감염시킬 수 있다.

웹 페이지의 경우 개발 편의성이나 시간 단축 측면에서 효율적인 동적인 메커니즘으로 제작되는 경우가 많은데 변수를  활용하는 이런 동적인 페이지의 유연성은 XSS 취약점을 유발하는 원인이 되기도 한다.

## 1\. 취약성 및 위험성

-   메시지를 매개변수로 받는 동적인 페이지 -> 개발 편의성 및 시간 단축
    -   구성의 일부를 변수로 받아 이 내용을 HTML 소스에 삽입하는 페이지
-   브라우저로 반환된 변수의 내용 조작 가능
-   클라이언트 사이드 스크립트의 이용자 실행 가능

## 2\. 점검 방법

-   URL 매개변수에 아래 문구를 입력 후 **XSS 팝업창**이 출력되면 취약하다고 판단
    ```
    "><script>alert('XSS')</script>
    ```
-   URL 매개변수에 아래 문구를 입력 후 **Cookie 값 팝업창**이 출력되면 취약하다고 판단
    ```
    "\><script>alert(document.coocke)</script>
    ```
-   일시적으로 사용자에게 반사(서버에 저장되지 x)

## 3) 실습

1. XSS 팝업창 출력되는지 테스트
![image](/assets/img/posts/WebSecurity/WebSecurity05_01.png)

2. XSS 팝업 출력 -> 취약점이 있다고 판단
![image](/assets/img/posts/WebSecurity/WebSecurity05_02.png)

3. 취약점 진단 문구를 작성하고 게시물 등록
![image](/assets/img/posts/WebSecurity/WebSecurity05_03.png)

4. 해당 게시물을 열면 취약점이 파악된대로 팝업 출력
![image](/assets/img/posts/WebSecurity/WebSecurity05_04.png)

5. 쿠키 값도 그대로 출력됨
\-> 둘 다 취약점이 존재
![image](/assets/img/posts/WebSecurity/WebSecurity05_05.png)