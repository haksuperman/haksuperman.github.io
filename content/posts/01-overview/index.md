---
title: AWS–OCI BGP VPN 이중화 개요
linkTitle: AWS–OCI BGP VPN · 01. 개요
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
---
## 1.1. 목표

-   AWS와 OCI에서 VPN을 생성할 때, 자동으로 tunnel이 2개 생성
-   두 클라우드의 VPN 구성 시, tunnel IP 를 Customer Gateway(AWS), CPE(OCI)로 지정해야 하기 때문에 하나의 터널만 구성(Up) 가능
-   두 개의 VPN을 구성해 두 개의 tunnel을 이용할 수 있도록 함
    -   AWS VPN1 tunnel 1 - OCI VPN1 tunnel 1
    -   AWS VPN2 tunnel 2 - OCI VPN2 tunnel 2

## 1.2. AWS-OCI 기본 Network 구성

### 1.2.1. AWS

-   VPC : 192.168.0.0/16
-   Public Subnet : 192.168.0.0/24
-   Private Subnet : 192.168.1.0/24

### 1.2.2. OCI

-   VCN : 10.0.0.0/16
-   Public Subnet : 10.0.0.0/24
-   Private Subnet : 10.0.1.0/24
