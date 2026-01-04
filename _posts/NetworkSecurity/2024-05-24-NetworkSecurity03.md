---
title: "[Network Security] Nmap을 활용한 네트워크 스캐닝"      # 글 제목
date: 2024-05-24 00:15:00 +0900 # 작성 시간
categories: [SECURITY, NETWORK SECURITY]        # [대분류, 소분류]
tags: [security, network, nmap, nslookup, ping, tcp 하프오픈 스캔, traceroute, tracert, wireshark, 스캐닝, scanning]     # 태그 (반드시 소문자로 시작 권장)
---
## 1\. nmap을 활용한 활성화 된 Host 스캔

-   Nmap Option<br>

| **\-sT** | connect() 함수를 이용한 Open 스캔(오픈) | **\-PS** | TCP SYN 패킷 만을 보내 시스템 활성화 여부 검사 |
| **\-sS** | 세션을 성립시키지 않는 SYN 스캔(하프오픈) | **\-PI** | 시스템 활성화 여부를 ICMP로 검사 |
| **\-sF** | FIN 패킷을 이용한 스캔 | **\-PB** | TCP와 ICMP 둘 다 사용하여 HOST 활성화 여부 검사 |
| **\-sN** | NULL 패킷을 이용한 스캔 | **\-O** | 시스템 운영체제 수정 |
| **\-sX** | X-MAS 패킷을 이용한 스캔 | **\-I** | Ident 프로토콜(RFC1413)을 사용해 열려있는 프로세스가 어떤 사용자에 의한 것인지 검사 |
| **\-sP** | ping을 이용한 HOST 활성화 여부 확인 | **\-n** | DNS Lookup을 하지 않음 |
| **\-sU** | UDP 포트 스캔 | **\-R** | DNS Lookup을 함 |
| **\-sR** | RPC 포트 스캔 | **\-PR** | ARP Ping |
| **\-sA** | ACK 패킷에 대한 TTL 값의 분석 | **\--traceroute** | HOST까지 경로를 추적 |
| **\-sW** | ACK 패킷에 대한 윈도우 크기 분석 | **\-PE** | ICMP Echo를 이용한 스캐닝 |
| **\-b** | FTP 바운스 스캔 | **\-PU** | UDP를 이용한 Ping |
| **\-f** | 스캔 시 방화벽을 통과할 수 있도록 패킷을 조작 | **\-PS** | TCP SYN Ping |
| **\-v** | 스캔의 세부 사항 표시 | **\-sL** | List Scan |
| **\-P0** | 스캔 전 ping을 하지 않음 | **\-sn** | Port Scan을 하지 않음 |
| **\-PT** | ping의 대용으로 TCP 패킷을 이용 | **\--packet-trace** | 전송 및 수신된 모든 패킷 표시 |


1. 192.168.0.0/24 대역에 활성화 된 Host 검색<br>
(-sP 옵션으로 Ping을 통해 확인)<br><br>
192.168.0.1 : VMware 예약<br>
192.168.0.2 : 게이트웨이<br>
192.168.0.17 : CentOS 6.9<br>
192.168.0.18 : CentOS 7.6<br>
192.168.0.254 : VMware 예약<br>
192.168.0.15 : Kali<br>
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_01.png)


2. wireshark 실행해서 -sP 옵션 자세히 확인 해보기
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_02.png)

3. -sP 옵션은 Ping 통신을 이용해 스캔하는 방식인데, ARP 패킷으로 스캔함(어..?)
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_03.png)

> **ICMP Echo Request**  
>  - 대부분의 경우, 특히 대상이 라우터나 인터넷 상의 원격 호스트일 때, ICMP Echo Request 패킷을 보냄  
>  - ICMP Echo Request는 일반적인 ping 명령과 동일하게 작동하며, 대상 호스트가 응답할 경우 활성 상태임을 확인  
>  - IP 계층에서 동작하며, 네트워크 내의 경로를 통해 패킷이 전송됨  
>   
> **ARP Request**  
>   - 대상이 동일 네트워크에 있을 때, ARP Request 패킷을 사용하여 호스트 탐지를 수행  
>   - ARP Request는 동일 네트워크 내에서 IP 주소에 해당하는 MAC 주소를 찾기 위해 사용됨  
>   - ARP는 데이터 링크 계층(2계층)에서 작동하며, 브로드캐스트 방식으로 네트워크 내 모든 장치에 요청을 보내고 해당 IP를 가진 장치의 응답을 기다림
{: .prompt-info }

## 2\. 상위 N개의 포트 스캐닝

-   가장 많이 쓰는 상위 N개의 포트 스캐닝
-   옵션 : --top-ports N(개수)
-   ex) nmap --top-ports 5


1. CentOS 6.9(192.168.0.17)을 대상으로 스캔한 것이 아닌 **통계적으로 가장 많이 사용**하는 포트 5개 스캔
(ftp, telnet, http, https는 해당 시스템에 설치가 되어 있지 않아서 closed)
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_04.png)

2. 상위 10개의 프로토콜도 스캔 가능(TCP 통신으로 스캔함)
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_05.png)

## 3\. Script를 이용한 스캐닝

-   옵션 : --script
-   ex) nmap -p 139, 445 --script=smb-vuln-ms17-010 \[IP\]  
    smb-vuln-ms17-010 스크립트를 이용한 MS17-010 취약점 및 Eternalblue 감염 여부 확인


스크립트의 위치는 /usr/share/nmap/scripts에 있음( find / -name "scripts" )
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_06.png)

## 4\. 보내고 받은 모든 패킷 표시하며 스캐닝 수행

-   옵션 : --packet-trace

1. `--packet-trace` 명령 안했을 때
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_07.png)

2. `--packet-trace` 명령 했을 때
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_08.png)

3. ssh말고 다른 포트가 열린 것도 확인해 보고 싶으면 CentOS 7.6 웹 서버 설치(yum install -y httpd) 후 똑같이 진행 해보기
(iptables -L 확인 후 iptables -F / iptables -X 로 iptable 날린 후 진행)
![image](/assets/img/posts/NetworkSecurity/NetworkSecurity03_09.png)