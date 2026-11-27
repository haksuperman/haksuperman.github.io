---
title: AWS–OCI BGP VPN 이중화 구성
date: '2025-10-25T19:35:00+09:00'
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
- /docs/guide-lab/aws-oci-bgp-vpn/
- /posts/01-overview/
- /docs/guide-lab/aws-oci-bgp-vpn/01-overview/
- /posts/multicloud01/
- /posts/02-vpn1-aws-temporary-cgw/
- /docs/guide-lab/aws-oci-bgp-vpn/02-vpn1-aws-temporary-cgw/
- /posts/multicloud02/
- /posts/03-vpn1-oci/
- /docs/guide-lab/aws-oci-bgp-vpn/03-vpn1-oci/
- /posts/multicloud03/
- /posts/04-vpn1-aws-final-cgw/
- /docs/guide-lab/aws-oci-bgp-vpn/04-vpn1-aws-final-cgw/
- /posts/multicloud04/
- /posts/05-vpn1-validation/
- /docs/guide-lab/aws-oci-bgp-vpn/05-vpn1-validation/
- /posts/multicloud05/
- /posts/06-vpn2-aws-temporary-cgw/
- /docs/guide-lab/aws-oci-bgp-vpn/06-vpn2-aws-temporary-cgw/
- /posts/multicloud06/
- /posts/07-vpn2-oci/
- /docs/guide-lab/aws-oci-bgp-vpn/07-vpn2-oci/
- /posts/multicloud07/
- /posts/08-vpn2-aws-final-cgw/
- /docs/guide-lab/aws-oci-bgp-vpn/08-vpn2-aws-final-cgw/
- /posts/multicloud08/
- /posts/09-vpn2-validation/
- /docs/guide-lab/aws-oci-bgp-vpn/09-vpn2-validation/
- /posts/multicloud09/
- /posts/10-connectivity-test/
- /docs/guide-lab/aws-oci-bgp-vpn/10-connectivity-test/
- /posts/multicloud10/
- /posts/11-dynamic-routing-retrospective/
- /docs/guide-lab/aws-oci-bgp-vpn/11-dynamic-routing-retrospective/
- /posts/multicloud11/
lastmod: '2026-11-27T19:53:50+09:00'
---
AWS와 OCI 사이의 BGP VPN 이중화 구성을 개요부터 연결 검증까지 한 문서로 정리했다. VPN 1과 VPN 2를 순서대로 구성한 뒤, 양방향 통신과 동적 라우팅 결과를 확인한다.

## 1. 구성 개요 {#구성-개요}

### 1.1. 목표 {#목표}

-   AWS와 OCI에서 VPN을 생성할 때, 자동으로 tunnel이 2개 생성
-   두 클라우드의 VPN 구성 시, tunnel IP 를 Customer Gateway(AWS), CPE(OCI)로 지정해야 하기 때문에 하나의 터널만 구성(Up) 가능
-   두 개의 VPN을 구성해 두 개의 tunnel을 이용할 수 있도록 함
    -   AWS VPN1 tunnel 1 - OCI VPN1 tunnel 1
    -   AWS VPN2 tunnel 2 - OCI VPN2 tunnel 2

### 1.2. AWS-OCI 기본 Network 구성 {#aws-oci-기본-network-구성}

**AWS**

-   VPC : 192.168.0.0/16
-   Public Subnet : 192.168.0.0/24
-   Private Subnet : 192.168.1.0/24

**OCI**

-   VCN : 10.0.0.0/16
-   Public Subnet : 10.0.0.0/24
-   Private Subnet : 10.0.1.0/24

## 2. VPN 1 구성 {#vpn-1-구성}

### 2.1. AWS 임시 Customer Gateway와 Transit Gateway {#aws-임시-customer-gateway와-transit-gateway}

**임시 Customer Gateway**

**개요**

-   OCI 측의 VPN tunnel IP를 Customer Gateway로 생성해야 하지만, 아직 OCI 측 tunnel IP를 모르기 때문에 임시 Customer Gateway를 생성 (1.1.1.1)
{{< callout type="info" >}}
**AWS vs OCI**<br>  
Customer gateway는 OCI의 CPE에 해당하는 리소스
{{< /callout >}}

**설정**

1. VPC → Customer Gateway → Create customer gateway 클릭
![image](MultiCloud02_01.png)

2. Create customer gateway
-  Name tag : \<적절한 이름 입력>
-  BGP ASN : 31898 (OCI 측 ASN은 31898 사용)
-  IP address : \<적절한 임시 IP 입력>
![image](MultiCloud02_02.png)

    > OCI 측 BGP ASN은 31898으로, 이를 변경할 수 있는 화면이 OCI Console 내 존재하지 않음
    > (변경 불가한 항목으로 보여짐, 공식적으로 불가하다라는 내용이 명시되어 있지는 않음)  
     (https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/ip-sec-tunnel\_update.htm)
{{< callout type="info" >}}
{{< /callout >}}

3. 생성 확인
![image](MultiCloud02_03.png)

**Transit gateway**

**개요**
-   VPN 구성을 위해 Virtual private gateway도 가능하지만, 이는 단일 네트워크와의 연결을 위한 목적
-   ex) 하나의 VCN - 하나의 On-premise/Cloud Network
![image](MultiCloud02_04.png)
{{< callout type="info" >}}
**AWS vs OCI**<br> 
Transit gateway는 OCI의 DRG에 해당하는 리소스
{{< /callout >}}

1. Create transit gateway
-   Name tag : \<적절한 이름 입력>
-   Description : \<적절한 설명 입력>
-   Amazon side Autonomous System Number (ASN) : \<AWS 측에서 이용할 ASN 번호 입력> (여기서는 입력하지 않고 기본 값으로 이용)
![image](MultiCloud02_05.png)
{{< callout type="info" >}}
AWS에서 BGP 통신을 위한 ASN 번호의 기본 값은 64512이며,  
Default or 64512-65535 or 4200000000-4294967294 중 선택하여 생성 가능  
  
Amazon side Autonomous System Number(ASN) The Autonomous System Number (ASN) for the AWS side of a Border Gateway Protocol (BGP) session. You can use the default ASN, or you can specify a private ASN in the 64512-65534 or 4200000000-4294967294 ranges.  
(https://docs.aws.amazon.com/vpc/latest/tgw/tgw-transit-gateways.html#create-tgw)
{{< /callout >}}

2. 생성 확인
![image](MultiCloud02_06.png)

**VPC Attach**
1. VPC → Transit gateway attachments → Create transit gateway attachment
![image](MultiCloud02_07.png)

2. Create transit gateway attachment
- Name tag : <적절한 이름 입력>
- Transit gateway ID : <위에서 생성한 Transit gateway 선택>
- Attachment type : VPC 선택
- VPC ID : Attach 할 VPC 선택 및 Subnet 선택
![image](MultiCloud02_08.png)

3. 생성 확인
![image](MultiCloud02_09.png)

**Site-to-Site VPN**

**VPN 생성**
1. VPC → Virtual private network (VPN) Connections→ Create VPN Connection
![image](MultiCloud02_10.png)

2. Create VPN connection
- Name tag : <적절한 이름 입력>
- Transit gateway type : Transit gateway 선택
- Transit gateway : <위에서 생성한 Transit gateway 선택>
- Customer gateway ID : <위에서 생성한 임시 Customer gateway 선택>
- Routing options : Dynamic (requires BGP) 선택
![image](MultiCloud02_11.png)

3. tunnel 1 options - optional
-   Inside IPv4 CIDR for tunnel 1 : \<OCI 불가 CIDR 제외 하여 입력>
{{< callout type="info" >}}
아래 IP 범위는 VPN tunnel Inside Interface로 사용 불가  
169.254.10.0 ~ 169.254.19.255<br>
169.254.100.0 ~ 169.254.109.255<br>
169.254.192.0 ~ 169.254.201.255<br>
( https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/settingupIPsec.htm )  
  
IPSec VPN 터널을 구성할 때, 터널 내부에서 서로 통신할 수 있는 IP 주소가 필요  
VPN 터널의 내부 IP는 외부 인터넷이나 다른 네트워크와 직접 연결되지 않음  
/30 Subnet을 선택해야 하는 이유는 VPN 터널 내부에서 단 두 개의 IP만 필요
{{< /callout >}}
-   Advanced options for tunnel 1 : Phase 1, 2에서 사용할 알고리즘 선택<br> (여기서는 기본 값으로 이용)
![image](MultiCloud02_12.png)

4. 생성 확인
![image](MultiCloud02_13.png)

**Configuration 다운 및 확인**

1. 우측 상단 → Download configuration 클릭
![image](MultiCloud02_14.png)

2. Download configuration
- Vendor : Generic 선택
- Platform : Generic 선택
- Software : Vendor Agnostic
- IKE version : ikev2 선택
![image](MultiCloud02_15.png)

3. configuration 확인 (tunnel 1)

```plaintext
Amazon Web Services
Virtual Private Cloud

VPN Connection Configuration
================================================================================
AWS utilizes unique identifiers to manipulate the configuration of
a VPN Connection. Each VPN Connection is assigned a VPN Connection Identifier
and is associated with two other identifiers, namely the
Customer Gateway Identifier and the Virtual Private Gateway Identifier.

Your VPN Connection ID		         : vpn-07855594c097e0b6e
Your Virtual Private Gateway ID          : 
Your Customer Gateway ID    		 : cgw-079524c4e95be47a7

A VPN Connection consists of a pair of IPSec tunnel security associations (SAs).
It is important that both tunnel security associations be configured.


IPSec Tunnel #1
================================================================================
#1: Internet Key Exchange Configuration

Configure the IKE SA as follows:
Please note, these sample configurations are for the minimum requirement of AES128, SHA1, and DH Group 2.
Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
You will need to modify these sample configuration files to take advantage of AES256, SHA256, or other DH groups like 2, 14-18, 22, 23, and 24.
NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
The address of the external interface for your customer gateway must be a static address.
Your customer gateway may reside behind a device performing network address translation (NAT).
To ensure that NAT traversal (NAT-T) can function, you must adjust your firewall !rules to unblock UDP port 4500.
If not behind NAT, and you are not using an Accelerated VPN, we recommend disabling NAT-T. If you are using an Accelerated VPN, make sure that NAT-T is enabled.
  - IKE version              : IKEv2
  - Authentication Method    : Pre-Shared Key
  - Pre-Shared Key           : <REDACTED — 새 PSK 사용>
  - Authentication Algorithm : sha1
  - Encryption Algorithm     : aes-128-cbc
  - Lifetime                 : 28800 seconds
  - Phase 1 Negotiation Mode : main
  - Diffie-Hellman           : Group 2

#2: IPSec Configuration

Configure the IPSec SA as follows:
Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
Please note, you may use these additionally supported IPSec parameters for encryption like AES256 and other DH groups like 2, 5, 14-18, 22, 23, and 24.
NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
  - Protocol                 : esp
  - Authentication Algorithm : hmac-sha1-96
  - Encryption Algorithm     : aes-128-cbc
  - Lifetime                 : 3600 seconds
  - Mode                     : tunnel
  - Perfect Forward Secrecy  : Diffie-Hellman Group 2

IPSec Dead Peer Detection (DPD) will be enabled on the AWS Endpoint. We
recommend configuring DPD on your endpoint as follows:
  - DPD Interval             : 10
  - DPD Retries              : 3

IPSec ESP (Encapsulating Security Payload) inserts additional
headers to transmit packets. These headers require additional space,
which reduces the amount of space available to transmit application data.
To limit the impact of this behavior, we recommend the following
configuration on your Customer Gateway:
  - TCP MSS Adjustment       : 1379 bytes
  - Clear Don't Fragment Bit : enabled
  - Fragmentation            : Before encryption

#3: Tunnel Interface Configuration

Your Customer Gateway must be configured with a tunnel interface that is
associated with the IPSec tunnel. All traffic transmitted to the tunnel
interface is encrypted and transmitted to the Virtual Private Gateway.



The Customer Gateway and Virtual Private Gateway each have two addresses that relate
to this IPSec tunnel. Each contains an outside address, upon which encrypted
traffic is exchanged. Each also contain an inside address associated with
the tunnel interface.

The Customer Gateway outside IP address was provided when the Customer Gateway
was created. Changing the IP address requires the creation of a new
Customer Gateway.

The Customer Gateway inside IP address should be configured on your tunnel
interface.

Outside IP Addresses:
  - Customer Gateway 		        : 1.1.1.1
  - Virtual Private Gateway	        : 3.38.86.169

Inside IP Addresses
  - Customer Gateway         		: 169.254.40.2/30
  - Virtual Private Gateway             : 169.254.40.1/30

Configure your tunnel to fragment at the optimal size:
  - Tunnel interface MTU     : 1436 bytes

#4: Border Gateway Protocol (BGP) Configuration:

The Border Gateway Protocol (BGPv4) is used within the tunnel, between the inside
IP addresses, to exchange routes from the VPC to your home network. Each
BGP router has an Autonomous System Number (ASN). Your ASN was provided
to AWS when the Customer Gateway was created.

BGP Configuration Options:
  - Customer Gateway ASN	          : 31898
  - Virtual Private  Gateway ASN          : 64512
  - Neighbor IP Address     		  : 169.254.40.1
  - Neighbor Hold Time       : 30

Configure BGP to announce routes to the Virtual Private Gateway. The gateway
will announce prefixes to your customer gateway based upon the prefix you
assigned to the VPC at creation time.
```

4. configuration 확인 (tunnel 2)

```plaintext
IPSec Tunnel #2
================================================================================
#1: Internet Key Exchange Configuration

Configure the IKE SA as follows:
Please note, these sample configurations are for the minimum requirement of AES128, SHA1, and DH Group 2.
Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
You will need to modify these sample configuration files to take advantage of AES256, SHA256, or other DH groups like 2, 14-18, 22, 23, and 24.
NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
The address of the external interface for your customer gateway must be a static address.
Your customer gateway may reside behind a device performing network address translation (NAT).
To ensure that NAT traversal (NAT-T) can function, you must adjust your firewall !rules to unblock UDP port 4500.
If not behind NAT, and you are not using an Accelerated VPN, we recommend disabling NAT-T. If you are using an Accelerated VPN, make sure that NAT-T is enabled.
  - IKE version              : IKEv2
  - Authentication Method    : Pre-Shared Key
  - Pre-Shared Key           : <REDACTED — 새 PSK 사용>
  - Authentication Algorithm : sha1
  - Encryption Algorithm     : aes-128-cbc
  - Lifetime                 : 28800 seconds
  - Phase 1 Negotiation Mode : main
  - Diffie-Hellman           : Group 2

#2: IPSec Configuration

Configure the IPSec SA as follows:
Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
Please note, you may use these additionally supported IPSec parameters for encryption like AES256 and other DH groups like 2, 5, 14-18, 22, 23, and 24.
NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
  - Protocol                 : esp
  - Authentication Algorithm : hmac-sha1-96
  - Encryption Algorithm     : aes-128-cbc
  - Lifetime                 : 3600 seconds
  - Mode                     : tunnel
  - Perfect Forward Secrecy  : Diffie-Hellman Group 2

IPSec Dead Peer Detection (DPD) will be enabled on the AWS Endpoint. We
recommend configuring DPD on your endpoint as follows:
  - DPD Interval             : 10
  - DPD Retries              : 3

IPSec ESP (Encapsulating Security Payload) inserts additional
headers to transmit packets. These headers require additional space,
which reduces the amount of space available to transmit application data.
To limit the impact of this behavior, we recommend the following
configuration on your Customer Gateway:
  - TCP MSS Adjustment       : 1379 bytes
  - Clear Don't Fragment Bit : enabled
  - Fragmentation            : Before encryption

#3: Tunnel Interface Configuration

Your Customer Gateway must be configured with a tunnel interface that is
associated with the IPSec tunnel. All traffic transmitted to the tunnel
interface is encrypted and transmitted to the Virtual Private Gateway.



The Customer Gateway and Virtual Private Gateway each have two addresses that relate
to this IPSec tunnel. Each contains an outside address, upon which encrypted
traffic is exchanged. Each also contain an inside address associated with
the tunnel interface.

The Customer Gateway outside IP address was provided when the Customer Gateway
was created. Changing the IP address requires the creation of a new
Customer Gateway.

The Customer Gateway inside IP address should be configured on your tunnel
interface.

Outside IP Addresses:
  - Customer Gateway 		        : 1.1.1.1
  - Virtual Private Gateway	        : 52.79.161.27

Inside IP Addresses
  - Customer Gateway         		: 169.254.149.226/30
  - Virtual Private Gateway             : 169.254.149.225/30

Configure your tunnel to fragment at the optimal size:
  - Tunnel interface MTU     : 1436 bytes

#4: Border Gateway Protocol (BGP) Configuration:

The Border Gateway Protocol (BGPv4) is used within the tunnel, between the inside
IP addresses, to exchange routes from the VPC to your home network. Each
BGP router has an Autonomous System Number (ASN). Your ASN was provided
to AWS when the Customer Gateway was created.

BGP Configuration Options:
  - Customer Gateway ASN	          : 31898
  - Virtual Private  Gateway ASN          : 64512
  - Neighbor IP Address     		  : 169.254.149.225
  - Neighbor Hold Time       : 30

Configure BGP to announce routes to the Virtual Private Gateway. The gateway
will announce prefixes to your customer gateway based upon the prefix you
assigned to the VPC at creation time.



Additional Notes and Questions
================================================================================

  - Amazon Virtual Private Cloud Getting Started Guide:
      http://docs.amazonwebservices.com/AmazonVPC/latest/GettingStartedGuide
  - Amazon Virtual Private Cloud Network Administrator Guide:
      http://docs.amazonwebservices.com/AmazonVPC/latest/NetworkAdminGuide
```

### 2.2. OCI CPE와 VPN {#oci-cpe와-vpn}

**CPE**

**AWS 측 VPN Tunnel 1 IP 확인**

-   Virtual Private Gateway 항목 확인
-   OCI 측에서 CPE IP에 해당
![image](MultiCloud03_01.png)

**설정**

1. 내비게이션 메뉴 → Networking → Customer connectivity → Customer-premises equipment
![image](MultiCloud03_02.png)

2. Create CPE
- Name : \<적절한 이름 입력>
- IP address : \<위에서 확인한 AWS 측 VPN Tunnel 1 IP 입력>
- Vendor : Other
![image](MultiCloud03_03.png)

3. 생성 확인
![image](MultiCloud03_04.png)

**VPN**

**기본 생성**

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

**Tunnel 1 (+Tunnel 2)**

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


**Tunnel configuration**

1. 생성한 tunnel1 선택 → 우측 상단 Open CPE configuration helper 선택
![image](MultiCloud03_13.png)

2. 우측 하단 Create content 선택
![image](MultiCloud03_14.png)

3. Download configuration 클릭
![image](MultiCloud03_15.png)

4. Tunnel IP 및 PSK 확인
![image](MultiCloud03_16.png)

### 2.3. AWS Customer Gateway와 PSK {#aws-customer-gateway와-psk}

**Customer gateway**

**OCI 측 tunnel IP를 가진 정식 Customer gateway 생성**

1. Create customer gateway
- Name tag : \<적절한 이름 입력>
- BGP ASN : 31898
- IP address : \<OCI 측 tunnel IP 입력>
![image](MultiCloud04_01.png)


2. 생성 확인
![image](MultiCloud04_02.png)

**VPN 구성 변경**

1. 이전에 생성한 VPN 선택 → 우측 상단 Actions → Modify VPN connection 클릭
![image](MultiCloud04_03.png)

2. Target customer gateway 변경
![image](MultiCloud04_04.png)

3. 적용 확인
![image](MultiCloud04_05.png)

**PSK (Pre-Shared Key) 변경**

1. 생성한 VPN 우측 상단 → Actions → Modify VPN tunnel options 클릭
![image](MultiCloud04_06.png)

2. OCI 측과 연결한 tunnel 선택
![image](MultiCloud04_07.png)

3. OCI 측에서 할당받은 PSK로 변경
![image](MultiCloud04_08.png)

4. 적용 확인
![image](MultiCloud04_09.png)
{{< callout type="info" >}}
**PSK(Pre-Shared Key) 일치**  
  
AWS 측과 OCI 측의 PSK 유효 조건이 다름  
 - AWS : 8~64자 / A~Z, a~z, 0~9, 언더바(\_), 점(.) / 0으로 시작 불가  
 - OCI : 1~255자 / 문자, 숫자, 공백  
    (https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/overviewIPsec.htm#components)  
⇒ OCI 측에서 지원하는 유효 문자가 더 적음(특수문자 불가) → OCI PSK를 AWS에 맞춤\
{{< /callout >}}

### 2.4. 연결 결과 확인 {#연결-결과-확인}

**AWS VPN 및 BGP State**
![image](MultiCloud05_01.png)

**OCI VPN 및 BGP State**
![image](MultiCloud05_02.png)

## 3. VPN 2 구성 {#vpn-2-구성}

### 3.1. AWS 임시 Customer Gateway와 VPN {#aws-임시-customer-gateway와-vpn}

**임시 Customer Gateway**

**개요**

-   OCI 측의 VPN tunnel IP를 Customer Gateway로 생성해야 하지만, 아직 OCI 측 tunnel IP를 모르기 때문에 임시 Customer Gateway를 생성 (2.2.2.2)
{{< callout type="info" >}}
VPN1 생성 했을 때 사용한 Customer gateway(1.1.1.1)를 사용해도 무방함  
(단, AWS에서 VPN1과 VPN2를 동시에 생성하는 경우 두 개의 임시 Customer gateway를 생성해야 함)
{{< /callout >}}

**설정**

1. VPC → Customer Gateway → Create customer gateway 클릭
![image](MultiCloud06_01.png)

2. Create customer gateway
- Name tag : \<적절한 이름 입력>
- BGP ASN : 31898 (OCI 측 ASN은 31898 사용)
- IP address : \<적절한 임시 IP 입력>
![image](MultiCloud06_02.png)
{{< callout type="info" >}}
OCI 측 BGP ASN은 31898으로, 이를 변경할 수 있는 화면이 OCI Console 내 존재하지 않음 (변경 불가한 항목으로 보여짐, 공식적으로 불가하다라는 내용이 명시되어 있지는 않음)  
(https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/ip-sec-tunnel\_update.htm)
{{< /callout >}}

3. 생성 확인
![image](MultiCloud06_03.png)

**Transit gateway**

**설정**
-   기존 VPN1 생성할 때 설정하였으므로, 생략

**Site-to-Site VPN**

**VPN 생성**

1. VPC → Virtual private network (VPN) Connections→ Create VPN Connection
![image](MultiCloud06_04.png)

2. Create VPN connection
- Name tag : \<적절한 이름 입력>
- Transit gateway type : Transit gateway 선택
- Transit gateway : \<위에서 생성한 Transit gateway 선택>
- Customer gateway ID : \<위에서 생성한 임시 Customer gateway 선택>
- Routing options : Dynamic (requires BGP) 선택
![image](MultiCloud06_05.png)

3. tunnel 1 options - optional
- Inside IPv4 CIDR for tunnel 1 : \<OCI 불가 CIDR 제외 하여 입력>
{{< callout type="info" >}}
아래 IP 범위는 VPN tunnel Inside Interface로 사용 불가  
 - 169.254.10.0 ~ 169.254.19.255  
 - 169.254.100.0 ~ 169.254.109.255  
 - 169.254.192.0 ~ 169.254.201.255  
( https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/settingupIPsec.htm )  
  
 - IPSec VPN 터널을 구성할 때, 터널 내부에서 서로 통신할 수 있는 IP 주소가 필요  
 - VPN 터널의 내부 IP는 외부 인터넷이나 다른 네트워크와 직접 연결되지 않음  
 - /30 Subnet을 선택해야 하는 이유는 VPN 터널 내부에서 단 두 개의 IP만 필요
{{< /callout >}}
- Advanced options for tunnel 1 : Phase 1, 2에서 사용할 알고리즘 선택 (여기서는 기본 값으로 이용)
![image](MultiCloud06_06.png)

4. 생성 확인
![image](MultiCloud06_07.png)

**Configuration 파일 다운 및 확인**

1. 우측 상단 → Download configuration 클릭
![image](MultiCloud06_08.png)

2. Download configuration
- Vendor : Generic 선택
- Platform : Generic 선택
- Software : Vendor Agnostic
- IKE version : ikev2 선택
![image](MultiCloud06_09.png)

3. configuration 확인 (tunnel 1)

    ```plaintext
    Amazon Web Services
    Virtual Private Cloud

    VPN Connection Configuration
    ================================================================================
    AWS utilizes unique identifiers to manipulate the configuration of
    a VPN Connection. Each VPN Connection is assigned a VPN Connection Identifier
    and is associated with two other identifiers, namely the
    Customer Gateway Identifier and the Virtual Private Gateway Identifier.

    Your VPN Connection ID		         : vpn-0864bc9165964e3c9
    Your Virtual Private Gateway ID          : 
    Your Customer Gateway ID    		 : cgw-062cd6a964d31964f

    A VPN Connection consists of a pair of IPSec tunnel security associations (SAs).
    It is important that both tunnel security associations be configured.


    IPSec Tunnel #1
    ================================================================================
    #1: Internet Key Exchange Configuration

    Configure the IKE SA as follows:
    Please note, these sample configurations are for the minimum requirement of AES128, SHA1, and DH Group 2.
    Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
    You will need to modify these sample configuration files to take advantage of AES256, SHA256, or other DH groups like 2, 14-18, 22, 23, and 24.
    NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

    Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
    The address of the external interface for your customer gateway must be a static address.
    Your customer gateway may reside behind a device performing network address translation (NAT).
    To ensure that NAT traversal (NAT-T) can function, you must adjust your firewall !rules to unblock UDP port 4500.
    If not behind NAT, and you are not using an Accelerated VPN, we recommend disabling NAT-T. If you are using an Accelerated VPN, make sure that NAT-T is enabled.
    - IKE version              : IKEv2
    - Authentication Method    : Pre-Shared Key
    - Pre-Shared Key           : <REDACTED — 새 PSK 사용>
    - Authentication Algorithm : sha1
    - Encryption Algorithm     : aes-128-cbc
    - Lifetime                 : 28800 seconds
    - Phase 1 Negotiation Mode : main
    - Diffie-Hellman           : Group 2

    #2: IPSec Configuration

    Configure the IPSec SA as follows:
    Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
    Please note, you may use these additionally supported IPSec parameters for encryption like AES256 and other DH groups like 2, 5, 14-18, 22, 23, and 24.
    NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

    Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
    - Protocol                 : esp
    - Authentication Algorithm : hmac-sha1-96
    - Encryption Algorithm     : aes-128-cbc
    - Lifetime                 : 3600 seconds
    - Mode                     : tunnel
    - Perfect Forward Secrecy  : Diffie-Hellman Group 2

    IPSec Dead Peer Detection (DPD) will be enabled on the AWS Endpoint. We
    recommend configuring DPD on your endpoint as follows:
    - DPD Interval             : 10
    - DPD Retries              : 3

    IPSec ESP (Encapsulating Security Payload) inserts additional
    headers to transmit packets. These headers require additional space,
    which reduces the amount of space available to transmit application data.
    To limit the impact of this behavior, we recommend the following
    configuration on your Customer Gateway:
    - TCP MSS Adjustment       : 1379 bytes
    - Clear Don't Fragment Bit : enabled
    - Fragmentation            : Before encryption

    #3: Tunnel Interface Configuration

    Your Customer Gateway must be configured with a tunnel interface that is
    associated with the IPSec tunnel. All traffic transmitted to the tunnel
    interface is encrypted and transmitted to the Virtual Private Gateway.



    The Customer Gateway and Virtual Private Gateway each have two addresses that relate
    to this IPSec tunnel. Each contains an outside address, upon which encrypted
    traffic is exchanged. Each also contain an inside address associated with
    the tunnel interface.

    The Customer Gateway outside IP address was provided when the Customer Gateway
    was created. Changing the IP address requires the creation of a new
    Customer Gateway.

    The Customer Gateway inside IP address should be configured on your tunnel
    interface.

    Outside IP Addresses:
    - Customer Gateway 		        : 2.2.2.2
    - Virtual Private Gateway	        : 15.164.201.33

    Inside IP Addresses
    - Customer Gateway         		: 169.254.60.2/30
    - Virtual Private Gateway             : 169.254.60.1/30

    Configure your tunnel to fragment at the optimal size:
    - Tunnel interface MTU     : 1436 bytes

    #4: Border Gateway Protocol (BGP) Configuration:

    The Border Gateway Protocol (BGPv4) is used within the tunnel, between the inside
    IP addresses, to exchange routes from the VPC to your home network. Each
    BGP router has an Autonomous System Number (ASN). Your ASN was provided
    to AWS when the Customer Gateway was created.

    BGP Configuration Options:
    - Customer Gateway ASN	          : 31898
    - Virtual Private  Gateway ASN          : 64512
    - Neighbor IP Address     		  : 169.254.60.1
    - Neighbor Hold Time       : 30

    Configure BGP to announce routes to the Virtual Private Gateway. The gateway
    will announce prefixes to your customer gateway based upon the prefix you
    assigned to the VPC at creation time.
    ```

4. configuration 확인 (tunnel 2)

    ```plaintext
    IPSec Tunnel #2
    ================================================================================
    #1: Internet Key Exchange Configuration

    Configure the IKE SA as follows:
    Please note, these sample configurations are for the minimum requirement of AES128, SHA1, and DH Group 2.
    Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
    You will need to modify these sample configuration files to take advantage of AES256, SHA256, or other DH groups like 2, 14-18, 22, 23, and 24.
    NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

    Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
    The address of the external interface for your customer gateway must be a static address.
    Your customer gateway may reside behind a device performing network address translation (NAT).
    To ensure that NAT traversal (NAT-T) can function, you must adjust your firewall !rules to unblock UDP port 4500.
    If not behind NAT, and you are not using an Accelerated VPN, we recommend disabling NAT-T. If you are using an Accelerated VPN, make sure that NAT-T is enabled.
    - IKE version              : IKEv2
    - Authentication Method    : Pre-Shared Key
    - Pre-Shared Key           : <REDACTED — 새 PSK 사용>
    - Authentication Algorithm : sha1
    - Encryption Algorithm     : aes-128-cbc
    - Lifetime                 : 28800 seconds
    - Phase 1 Negotiation Mode : main
    - Diffie-Hellman           : Group 2

    #2: IPSec Configuration

    Configure the IPSec SA as follows:
    Category "VPN" connections in the GovCloud region have a minimum requirement of AES128, SHA2, and DH Group 14.
    Please note, you may use these additionally supported IPSec parameters for encryption like AES256 and other DH groups like 2, 5, 14-18, 22, 23, and 24.
    NOTE: If you customized tunnel options when creating or modifying your VPN connection, you may need to modify these sample configurations to match the custom settings for your tunnels.

    Higher parameters are only available for VPNs of category "VPN," and not for "VPN-Classic".
    - Protocol                 : esp
    - Authentication Algorithm : hmac-sha1-96
    - Encryption Algorithm     : aes-128-cbc
    - Lifetime                 : 3600 seconds
    - Mode                     : tunnel
    - Perfect Forward Secrecy  : Diffie-Hellman Group 2

    IPSec Dead Peer Detection (DPD) will be enabled on the AWS Endpoint. We
    recommend configuring DPD on your endpoint as follows:
    - DPD Interval             : 10
    - DPD Retries              : 3

    IPSec ESP (Encapsulating Security Payload) inserts additional
    headers to transmit packets. These headers require additional space,
    which reduces the amount of space available to transmit application data.
    To limit the impact of this behavior, we recommend the following
    configuration on your Customer Gateway:
    - TCP MSS Adjustment       : 1379 bytes
    - Clear Don't Fragment Bit : enabled
    - Fragmentation            : Before encryption

    #3: Tunnel Interface Configuration

    Your Customer Gateway must be configured with a tunnel interface that is
    associated with the IPSec tunnel. All traffic transmitted to the tunnel
    interface is encrypted and transmitted to the Virtual Private Gateway.



    The Customer Gateway and Virtual Private Gateway each have two addresses that relate
    to this IPSec tunnel. Each contains an outside address, upon which encrypted
    traffic is exchanged. Each also contain an inside address associated with
    the tunnel interface.

    The Customer Gateway outside IP address was provided when the Customer Gateway
    was created. Changing the IP address requires the creation of a new
    Customer Gateway.

    The Customer Gateway inside IP address should be configured on your tunnel
    interface.

    Outside IP Addresses:
    - Customer Gateway 		        : 2.2.2.2
    - Virtual Private Gateway	        : 52.79.45.9

    Inside IP Addresses
    - Customer Gateway         		: 169.254.97.202/30
    - Virtual Private Gateway             : 169.254.97.201/30

    Configure your tunnel to fragment at the optimal size:
    - Tunnel interface MTU     : 1436 bytes

    #4: Border Gateway Protocol (BGP) Configuration:

    The Border Gateway Protocol (BGPv4) is used within the tunnel, between the inside
    IP addresses, to exchange routes from the VPC to your home network. Each
    BGP router has an Autonomous System Number (ASN). Your ASN was provided
    to AWS when the Customer Gateway was created.

    BGP Configuration Options:
    - Customer Gateway ASN	          : 31898
    - Virtual Private  Gateway ASN          : 64512
    - Neighbor IP Address     		  : 169.254.97.201
    - Neighbor Hold Time       : 30

    Configure BGP to announce routes to the Virtual Private Gateway. The gateway
    will announce prefixes to your customer gateway based upon the prefix you
    assigned to the VPC at creation time.



    Additional Notes and Questions
    ================================================================================

    - Amazon Virtual Private Cloud Getting Started Guide:
        http://docs.amazonwebservices.com/AmazonVPC/latest/GettingStartedGuide
    - Amazon Virtual Private Cloud Network Administrator Guide:
        http://docs.amazonwebservices.com/AmazonVPC/latest/NetworkAdminGuide
    ```

### 3.2. OCI CPE와 VPN {#oci-cpe와-vpn-1}

**CPE**

**AWS 측 VPN tunnel 2 IP 확인**

-   Virtual Private Gateway 항목 확인
-   OCI 측에서 CPE IP에 해당
![image](MultiCloud07_01.png)

**설정**

1. 내비게이션 메뉴 → Networking → Customer connectivity → Customer-premises equipment
![image](MultiCloud07_02.png)

2. Create CPE
- Name : \<적절한 이름 입력>
- IP address : \<위에서 확인한 AWS 측 VPN tunnel 1 IP 입력>
- Vendor : Other
![image](MultiCloud07_03.png)

3. 생성 확인
![image](MultiCloud07_04.png)

**VPN**

**기본 생성**

1. 내비게이션 메뉴 → Networking → Customer connectivity → Site-to-Site VPN
![image](MultiCloud07_05.png)

2. Create IPSec connection
- Name : \<적절한 이름 입력>
- Customer-premises equipment : \<위에서 생성한 CPE 선택>
- Dynamic routing gateway : \<OCI 측 네트워크에 Attach된 DRG 선택>
- Static routes to on-premises network : \<AWS 측 VPC Subnet CIDR 입력>
![image](MultiCloud07_06.png)
{{< callout type="info" >}}
VPN을 BGP로 구성하는 경우, 해당 Static route to on-premises network 설정은 무시됨.  
BGP가 실패하고 Static으로 통신해야 할 때, VPN1과 이중화를 위해 CIDR 범위를 좁게 설정 (Longest prefix match rule)
{{< /callout >}}

**tunnel 2 (+tunnel 1)**

1. 기본 정보
- Name : \<적절한 이름 입력>
- IKE version : IKEv2 선택
- Routing type : BGP dynamic routing 선택
![image](MultiCloud07_07.png)

2. BGP 정보
- BGP ASN : \<AWS 측 ASN 입력>
- IPv4 inside tunnel interface - CPE : \<AWS 측 Virtual Private Gateway 항목 입력>
- IPv4 inside tunnel interface - Oracle : \<AWS 측 Customer Gateway 항목 입력>
![image](MultiCloud07_08.png)

3. Phase 1 → AWS 측 정보와 일치
- Encryption algorithm
- Authentication algorithm
- Diffie-Hellman group
- IKE session key lifetime
![image](MultiCloud07_09.png)
{{< callout type="info" >}}
AWS에서 tunnel 알고리즘 정보를 변경하지 않고 Default로 생성한 경우, 위 Configuration 파일과 같이 Phase 별 알고리즘 정보가 하나만 표기 (실제 아래 사진과 같이 모두 체크되어 이용할 수 있으나 OCI 측에서 설정되어야 하는 알고리즘 정보를 오해하기 쉬움)  
![image](MultiCloud07_10.png)
![image](MultiCloud07_11.png)
{{< /callout >}}

4. Phase 2 → AWS 측 정보와 일치
- Encryption algorithm
- IPSec session key lifetime
- Deffie-Hellman group
![image](MultiCloud07_12.png)
{{< callout type="info" >}}
tunnel 1은 이용하지 않지만, 동일한 방법으로 구성
{{< /callout >}}

5. 생성 확인
![image](MultiCloud07_13.png)

**tunnel configuration**

1. 생성한 tunnel 2 선택 → 우측 상단 Open CPE configuration helper 선택
![image](MultiCloud07_14.png)


2. 우측 하단 Create content 선택
![image](MultiCloud07_15.png)

3. Download configuration 클릭
![image](MultiCloud07_16.png)

4. tunnel IP 및 PSK 확인
![image](MultiCloud07_17.png)

### 3.3. AWS Customer Gateway와 PSK {#aws-customer-gateway와-psk-1}

**Customer gateway**

**OCI 측 tunnel IP를 가진 정식 Customer gateway 생성**
1. Create customer gateway
Name tag : \<적절한 이름 입력>
BGP ASN : 31898
IP address : \<OCI 측 tunnel IP 입력>
![image](MultiCloud08_01.png)

2. 생성 확인
![image](MultiCloud08_02.png)

**VPN 구성 변경**

1. 이전에 생성한 VPN 선택 → 우측 상단 Actions → Modify VPN connection 클릭
![image](MultiCloud08_03.png)

2. Target customer gateway 변경
![image](MultiCloud08_04.png)

3. 적용 확인
![image](MultiCloud08_05.png)

**PSK (Pre-Shared Key) 변경**

1. 생성한 VPN 우측 상단 → Actions → Modify VPN tunnel options 클릭
![image](MultiCloud08_06.png)

2. OCI 측과 연결한 tunnel 선택
![image](MultiCloud08_07.png)

3. OCI 측에서 할당받은 PSK로 변경
![image](MultiCloud08_08.png)

4. 적용 확인
![image](MultiCloud08_09.png)
{{< callout type="info" >}}
**PSK(Pre-Shared Key) 일치**  
  
AWS 측과 OCI 측의 PSK 유효 조건이 다름  
 - AWS : 8~64자 / A~Z, a~z, 0~9, 언더바(\_), 점(.) / 0으로 시작 불가  
 - OCI : 1~255자 / 문자, 숫자, 공백  
( https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/overviewIPsec.htm#components )  
  
⇒ OCI 측에서 지원하는 유효 문자가 더 적음(특수문자 불가) → OCI PSK를 AWS에 맞춤
{{< /callout >}}

### 3.4. 연결 결과 확인 {#연결-결과-확인-1}

**AWS VPN 및 BGP State**
![image](MultiCloud09_01.png)

**OCI VPN 및 BGP State**
![image](MultiCloud09_02.png)

## 4. 통신 확인 {#통신-확인}

{{< callout type="info" >}}
통신은 양 측 라우팅 테이블, 방화벽 설정이 완료된 것을 전제로 진행
{{< /callout >}}

### 4.1. Ping {#ping}

**AWS → OCI**
![image](MultiCloud10_01.png)

**OCI → AWS**
![image](MultiCloud10_02.png)

### 4.2. SSH {#ssh}

**AWS → OCI**
![image](MultiCloud10_03.png)

**OCI → AWS**
![image](MultiCloud10_04.png)

## 5. 동적 라우팅과 회고 {#동적-라우팅과-회고}

### 5.1. OCI 측 DRG Route table {#oci-측-drg-route-table}

-   AWS 측에서 광고 받아 서브넷 정보 동적으로 등록
![image](MultiCloud11_01.png)

### 5.2. AWS 측 Transit gateway Route table {#aws-측-transit-gateway-route-table}

-   OCI 측에서 광고 받아 서브넷 정보 동적으로 등록
![image](MultiCloud11_02.png)

### 5.3. 회고 {#회고}

-   정말 이중화라는 것은 끝도 없는 것 같다.. 세상에 장애 없는 시스템은 없고, 이를 어디까지 이중화 시키는지에 대한 고민이 당연하게도 필요하다. 예를 들어, 비용적인 부분을 고려하지 않는다면 멀티 리전을 넘어, 멀티 클라우드로까지 고려해 볼 수 있다. 하지만, 누구나 그렇듯 비용적인 부분이 항상 걸림돌이다.
    -   AWS 터널에 장애가 발생하면 어쩌나 -> 터널을 이중화하면 되지
    -   AWS 서울 리전이 장애가 발생하면 어쩌나 -> 타 리전에 DR을 구축하면 되지
    -   AWS 자체에 장애가 발생하면 어쩌나 -> 타 클라우드로 DR을 구축하면 되지
    -   해저케이블이 끊어져 여러 클라우드에 장애가 발생하면 어쩌나 -> ........
-   항상 어느정도까지의 적정선을 두고 구축하는지가 중요한 것 같다. 클라우드 세상에서 기술적인 방법은 언제나 찾으면 있다...! (아직은 그렇게 믿고 있다)
