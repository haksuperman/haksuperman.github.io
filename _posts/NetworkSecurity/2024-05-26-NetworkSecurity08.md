---
title: "[Network Security] ARP 스푸핑(ARP Spoofing)"      # 글 제목
date: 2024-05-26 18:50:00 +0900 # 작성 시간
categories: [SECURITY, NETWORK SECURITY]        # [대분류, 소분류]
tags: [security, network, arp spoofing, arp, arpspoof, fragrouter, kali, sniffing, spoofing, 스니핑, 스푸핑, 와이어샤크, wireshark]     # 태그 (반드시 소문자로 시작 권장)
---
ARP 스푸핑은 근거리 네트워크에서 사용되는 대표적인 중간자 공격으로 두 단말 간의 통신을 속여 자신을 통해 통신하도록 만들어 중간에서 네트워크 통신 내용을 스니핑 또는 스푸핑 하도록 하는 기술이다.

## 1\. ARP 스푸핑

-   근거리 네트워크(LAN) 환경에서 중간자 공격에 사용되는 기술로 활용
-   IP에서 MAC 주소로 변환하는 과정에서 발생하는 ARP Reply 패킷을 변조하여 공격하는 방식

## 2\. APR 스푸핑을 이용한 MITM 공격 원리

-   두 단말 간의 통신 사이에서 정상 통신으로 속여 데이터가 공격자를 경유하도록 유도하는 기술
-   두 단말 간은 정상적 통신을 하는 것으로 알고 있지만 실제로는 공격자를 통해 패킷을 전달
-   공격자는 두 단말 간의 통신 내용을 스니핑(Sniffing) 또는 스푸핑(Spoofing) 하여 전달 가능

> **스니핑(Sniffing)과 스푸핑(Spoofing)의 차이**  
>  - 스니핑 : 네트워크 상의 데이터를 몰래 엿보는 행위(주로 정보를 가로채는데 사용)  
>  - 스푸핑 : 공격자가 다른 시스템, 장치, 또는 사용자로 가장하여 네트워크 상에서 잘못된 정보를 보내는 행위(주로 권한을 얻거나 잘못된 정보를 제공하는데 사용)  
>  - 스니핑은 수동적은 공격 방식인 반면, 스푸핑은 능동적인 공격 방식이다.
{: .prompt-info }

## 3\. ARP 스푸핑의 공격 과정

-   공격자(IP:x.x.x.40)는 B 사용자 PC에게 연결하고자 하는 A 사용자 IP에게 MAC 주소를 포함하는 ARP Reply 패킷을 지속적으로 보냄
-   B 사용자 PC는 x.x.x.10에 해당하는 IP를 자신의 ARP 테이블 내 공격자의 MAC 주소로 기억

## 4\. ARP 스푸핑 공격 실습

-   환경 구성 : Kail(공격자), CentOS 7.6(피해자 서버), CentOS 6.9(피해자 클라이언트)
-   공격 방법  
    \- 피해자 PC의 IP와 게이트웨이 IP에게 ARP Reply 공격 수행  
    \- 네트워크 연결을 위해 포워딩

#### 1) 정상적인 ARP 테이블 환경 구성을 위한 Ping 테스트
1. CentOS 6.7에서 Kail, CentOS 7.6으로 핑을 보내 정상적인 ARP 테이블 구성(Kail는 ARP 테이블 등록이 필요 없지만...)

    ```bash
    ping 192.168.0.15 -c 3
    ping 192.168.0.18 -c 3
    ```

    ![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_01.png)


2. CentOS 7.6에서 Kail, CentOS 6.9로 핑을 보내 정상적인 ARP 테이블 구성

    ```bash
    ping 192.168,0.15 -c 3
    ping 192.168.0.17 -c 3
    ```

    ![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_02.png)

#### 2) 정상적인 ARP 테이블 확인
1. CentOS 6.9 ARP 테이블 확인
(192.168.0.18의 CentOS 7.6의 MAC 주소 **00:0c:29:a4:4a:cd** 등록 되어 있음)

    ```bash
    arp -a
    ```
    ![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_03.png)


2. CentOS 7.6 ARP 테이블 확인
(192.168.0.17의 CentOS 6.9의 MAC 주소 **00:0c:29:72:21:22** 등록 되어 있음)

    ```bash
    apr -a
    ```

    ![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_04.png)

#### 3) Kail에서 ARP Spoofing 공격


공격 대상의 서버를 두 곳 모두 진행(CentOS 6.9, CentOS 7.6 모두 양 방향으로 패킷을 보낼 수 있기 때문)
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_05.png)

(1) eth0 네트워크 인터페이스를 사용해(-i 옵션), 192.168.0.17의 IP를 가진 시스템을 공격(-t 옵션), 자신을 192.168.0.18 IP로 속임<br>
\-> 192.168.0.17(CentOS 6.9)이 192.168.0.18(CentOS 7.6)로 패킷을 보내면 공격자(Kali)로 보내도록 ARP 테이블을 공격

(2) eth0 네트워크 인터페이스를 사용해(-i 옵션), 192.168.0,18의 IP를 가진 시스템을 공격(-t 옵션), 자신을 192.168.0.17 IP로 속임<br>
\-> 192.168.0.18(CentOS 7.6)이 192.168.0.17(CentOS 6.9)로 패킷을 보내면 공격자(Kali)로 보내도록 ARP 테이블을 공격

```bash
arpspoof -i eth0 -t 192.168.0.17 192.168.0.18
arpspoof -i eth0 -t 192.168.0.18 192.168.0.17
```

> CentOS 6.9(192.168.0.17)과 CentOS 7.6(192.168.0.18)도 ARP 패킷을 보내 ARP를 발생시키고 최신화 시키기 때문에 지속적으로 ARP Spoofing을 수행해줘야 한다!
{: .prompt-tip }

#### 4) 기존 패킷 도착지로 전달(fragrouter -B1)

1. 공격지(Kali)로 온 패킷을 원래 도착지로 전달(전달하는 느낌)
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_06.png)

2. Kali에서 수집한 ICMP 패킷 확인<br>
fragrouter -B1 터미널 창에서 총 3개의 패킷을 받고 전달한 것 확인 가능<br>
(와이어샤크에서 자세한 패킷 확인 가능)
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_07.png)

> flagrouter -B1 명령을 수행하지 않고 공격자(Kali)에서 다 먹어버리면 ARP Poisoning 공격이다!  
> (포워딩까지 하면 ARP Spoofing)
{: .prompt-info }

#### 5) 피해 서버, 클라이언트(CentOS 6.9, CentOS 7.6) ARP 테이블 확인
1. CentOS 6.9 ARP 테이블 확인
CentOS 7.6(192.168.0.18)의 MAC 주소가 Kali(192.168.0.15)의 MAC 주소인 **00:0c:29:fe:e3:96**으로 바뀜
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_08.png)

2. CentOS 7.6 ARP 테이블 확인
CentOS 6.9(192.168.0.17)의 MAC 주소가 Kali(192.168.0.15)의 MAC 주소인 **00:0c:29:fe:e3:96**으로 바뀜
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity08_09.png)

## 5\. ARP Spoofing 대응방안(시스템 내)

-   정적인 ARP 테이블 관리
    -   재부팅 시에도 항상 정적인 ARP 테이블이 관리될 수 있도록 설정
    -   static으로 설정한 ARP 테이블이 가장 우선순위가 높기 때문에 ARP Spoofing 공격에도 먹히지 않음
-   보안 수준 강화
    -   공격자가 설치한 프로그램으로 수행될 수 있으므로, 서버 내의 보안 수준을 강화
-   중요 패킷 암호화
    -   네트워크를 통해 중요한 데이터가 송/수신 될 경우 유출 및 변조되지 않도록 조치
    -   위의 와이어샤크와 같은 캡처 프로그램으로 간단하게 패킷 내용을 확인할 수 있기 때문에 내용 자체를 암호화하는 것이 바람직함!

## 6\. ARP Spoofing 대응방안(네트워크 장비 내)

-   정적인 MAC 주소 관리
-   사설 VLAN 활용
-   보안 스위치 활용