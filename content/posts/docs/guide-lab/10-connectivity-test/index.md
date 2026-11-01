---
title: AWS–OCI VPN 통신 확인
linkTitle: AWS–OCI BGP VPN · 10. 통신 확인
date: '2025-10-25T20:39:00+09:00'
tags:
- aws
- oci
- vpn
- tunnel
- bgp
- asn
- duplication
draft: false
collection: docs
docCategory: guide-lab
aliases:
- /docs/guide-lab/aws-oci-bgp-vpn/10-connectivity-test/
- /posts/multicloud10/
---
{{< callout type="info" >}}
통신은 양 측 라우팅 테이블, 방화벽 설정이 완료된 것을 전제로 진행
{{< /callout >}}

## 10.1. Ping

### 10.1.1. AWS → OCI
![image](MultiCloud10_01.png)

#### 10.1.2. OCI → AWS
![image](MultiCloud10_02.png)

## 10.2. SSH

### 10.2.1. AWS → OCI
![image](MultiCloud10_03.png)

#### 10.2.2. OCI → AWS
![image](MultiCloud10_04.png)
