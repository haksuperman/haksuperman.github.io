---
title: "VPN 1 구성: OCI CPE와 VPN"
linkTitle: "03. VPN 1 — OCI"
date: "2025-10-25T19:59:00+09:00"
lastmod: "2025-10-25T19:59:00+09:00"
aliases: ["/posts/multicloud03/"]
tags:
  - "aws"
  - "oci"
  - "vpn"
  - "tunnel"
  - "bgp"
  - "asn"
  - "duplication"
categories:
  - "CLOUD"
  - "MULTICLOUD"
weight: 30
---
## 3.1. CPE

### 3.1.1. AWS 측 VPN Tunnel 1 IP 확인

-   Virtual Private Gateway 항목 확인
-   OCI 측에서 CPE IP에 해당
![image](MultiCloud03_01.png)

### 3.1.2. 설정

1. 내비게이션 메뉴 → Networking → Customer connectivity → Customer-premises equipment
![image](MultiCloud03_02.png)

2. Create CPE
- Name : \<적절한 이름 입력>
- IP address : \<위에서 확인한 AWS 측 VPN Tunnel 1 IP 입력>
- Vendor : Other
![image](MultiCloud03_03.png)

3. 생성 확인
![image](MultiCloud03_04.png)

## 3.2. VPN

### 3.2.1. 기본 생성

1. 내비게이션 메뉴 → Networking → Customer connectivity → Site-to-Site VPN
![image](MultiCloud03_05.png)

2. Create IPSec connection
- Name : \<적절한 이름 입력>
- Customer-premises equipment : \<위에서 생성한 CPE 선택>
- Dynamic routing gateway : \<OCI 측 네트워크에 Attach된 DRG 선택>
- Static routes to on-premises network : \<AWS 측 VPC Subnet CIDR 입력>
![image](MultiCloud03_06.png)
{{< callout type="info" >}}
VPN을 BGP로 구성하는 경우, 해당 Static route to on-premises network 설정은 무시됨
{{< /callout >}}

### 3.2.2 Tunnel 1 (+Tunnel 2)

1. 기본 정보
- Name : \<적절한 이름 입력>
- IKE version : IKEv2 선택
- Routing type : BGP dynamic routing 선택
![image](MultiCloud03_07.png)

2. BGP 정보
- BGP ASN : \AWS 측 ASN 입력>
- IPv4 inside tunnel interface - CPE : \<AWS 측 Virtual Private Gateway 항목 입력>
- Pv4 inside tunnel interface - Oracle : \<AWS 측 Customer Gateway 항목 입력>
![image](MultiCloud03_08.png)

3. Phase 1 → AWS 측 정보와 일치
- Encryption algorithm
- Authentication algorithm
- Diffie-Hellman group
- IKE session key lifetime
![image](MultiCloud03_09.png)
{{< callout type="info" >}}
AWS에서 Tunnel 알고리즘 정보를 변경하지 않고 Default로 생성한 경우, 위 Configuration 파일과 같이 Phase 별 알고리즘 정보가 하나만 표기 (실제 아래 사진과 같이 모두 체크되어 이용할 수 있으나 OCI 측에서 설정되어야 하는 알고리즘 정보를 오해하기 쉬움)  
![image](MultiCloud03_09.png)
![image](MultiCloud03_10.png)
{{< /callout >}}

4. Phase 2 → AWS 측 정보와 일치
- Encryption algorithm
- IPSec session key lifetime
- Deffie-Hellman group
![image](MultiCloud03_11.png)
{{< callout type="info" >}}
Tunnul2는 이용하지 않지만, 동일한 방법으로 구성
{{< /callout >}}

5. 생성 확인
![image](MultiCloud03_12.png)


### 3.2.3. Tunnel configuration

1. 생성한 tunnel1 선택 → 우측 상단 Open CPE configuration helper 선택
![image](MultiCloud03_13.png)

2. 우측 하단 Create content 선택
![image](MultiCloud03_14.png)

3. Download configuration 클릭
![image](MultiCloud03_15.png)

4. Tunnel IP 및 PSK 확인
![image](MultiCloud03_16.png)
