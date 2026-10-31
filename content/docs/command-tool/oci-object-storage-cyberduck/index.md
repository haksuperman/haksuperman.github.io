---
title: "Cyberduck으로 OCI Object Storage 사용하기"
linkTitle: "OCI Object Storage와 Cyberduck"
date: "2025-05-01T11:13:00+09:00"
lastmod: "2025-05-01T11:13:00+09:00"
aliases: ["/posts/oci16/"]
tags:
  - "oci"
  - "cloud"
  - "oraclecloud"
  - "oracle cloud infrastructure"
  - "cyberduck"
  - "object storage"
categories:
  - "CLOUD"
  - "OCI"
---
## 1. 사전 준비

### 1.1. Customer Secret Key 생성

1. 우측 상단 Profile -> 계정명 선택
![image](OCI16_01.png)

2. 좌측 하단 Resources -> \[Customer secret keys -> Generate secret key\] 선택
![image](OCI16_02.png)

3. Name : \<적절한 이름 입력>
![image](OCI16_03.png)

4. 생성된 Secret Key 복사 (재확인 불가)
![image](OCI16_04.png)

5. Access Key 복사
![image](OCI16_05.png)
{{< callout type="info" >}}
Access Key와 Secret Key를 통해 해당 테넌시에 접근
{{< /callout >}}

### 1.2. 테넌시 Object Storage namespace 확인

1. 우측 상단 Profile -> Tenancy 선택
![image](OCI16_06.png)

2. Tenancy information -> Object stroage namespace 확인
![image](OCI16_07.png)

## 2. Cyberduck 설치

[https://cyberduck.io/download/](https://cyberduck.io/download/)


## 3. Cyberduck Object Storage 접근

### 3.1. OCI Object Stoarge 프로필 등록

1. 새 연결 클릭 -> Profile 변경
![image](OCI16_08.png)
![image](OCI16_09.png)

2. More Options 클릭
![image](OCI16_10.png)

3. 프로필 탭 -> OCI Object Storage \<이용 리전> 체크
![image](OCI16_11.png)

### 3.2. 북마크 생성

1. 좌측 하단 북마크 추가 아이콘 클릭
![image](OCI16_12.png)

2. 프로필 변경
![image](OCI16_13.png)

3. 위에서 등록한 OCI Object Stoarge 프로필 선택
![image](OCI16_14.png)

4. 북마크 추가
-   별명 : \<적절한 이름 입력>
-   서버 : \<Object storage namespace>.compat.objectstorage.\<Region명>.oraclecloud.com
-   위에서 확인한 Access Key와 Secret Key 입력
![image](OCI16_15.png)

5. 추가된 북마크 더블클릭
![image](OCI16_16.png)

6. 테넌시 내의 Object storage Bucket 확인 가능
![image](OCI16_17.png)

## 4. 파일 업로드

1. 해당 Bucket 더블클릭

2. 우클릭 -> 업로드
![image](OCI16_18.png)

3. 파일 선택 및 Upload 선택
![image](OCI16_19.png)

4. 전송 기록 확인
![image](OCI16_20.png)

## 5. 파일 다운로드

1. 해당 파일 선택 후 우클릭

2. 내려받기
![image](OCI16_21.png)
