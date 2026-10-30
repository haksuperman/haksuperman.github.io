#!/usr/bin/env python3
"""Build the second-batch Study migration manifest from the reviewed plan."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SLUGS = {
    "AWS02": "vpc-web-infrastructure-lab",
    "AWS04": "shared-responsibility-model",
    "AWS05": "cloud-native-security-tools",
    "AWS06": "modern-operating-model",
    "AWS07": "iam-foundations",
    "AWS08": "iam-common-patterns",
    "AWS09": "tag-based-access-control",
    "AWS10": "secure-cross-account-access",
    "AWS11": "identity-system-integration",
    "AWS12": "organizational-security-best-practices",
    "AWS13": "iam-best-practices",
    "AWS14": "least-privilege-access",
    "AWS15": "short-and-long-term-credentials",
    "AWS16": "iam-access-review",
    "AWS17": "vpc-security-foundations",
    "AWS18": "working-with-vpcs",
    "AWS19": "route-tables-security-groups-nacls",
    "AWS20": "private-network-segmentation",
    "AWS21": "protecting-access-beyond-vpc",
    "AWS22": "vpc-endpoints-and-privatelink",
    "AWS23": "aws-waf",
    "AWS24": "aws-shield-ddos",
    "AWS25": "third-party-firewalls",
    "AWS26": "data-protection-overview",
    "AWS27": "data-security-challenges",
    "AWS28": "data-at-rest",
    "AWS29": "data-in-transit",
    "AWS30": "data-access-logging",
    "AWS31": "data-classification",
    "AWS32": "audit-logs-and-incident-response",
    "AWS33": "management-event-logging",
    "AWS34": "resource-configuration-tracking",
    "AWS35": "centralized-application-logging",
    "AWS36": "resource-configuration-scanning",
    "AWS37": "host-vulnerability-scanning",
    "AWS38": "threat-detection-in-logs",
    "AWS39": "security-event-tracking",
    "AWS40": "incident-response-planning",
    "AWS41": "incident-response-automation",
    "Kubernetes01": "vmware-node-setup",
    "Kubernetes02": "docker-installation",
    "Kubernetes03": "kubernetes-tools-installation",
    "Kubernetes04": "cluster-bootstrap",
    "Linux01": "basic-commands-files-and-paths",
    "Linux02": "file-permissions-and-acl",
    "Linux03": "setuid-sudo-and-permissions",
    "Linux04": "vi-editor",
    "Linux05": "package-archive-and-text-tools",
    "Network01": "cloud-environment-concepts",
    "Network02": "lan-and-wan-fundamentals",
    "Network03": "packet-tracer-cabling-lab",
    "Network04": "three-tier-switching-architecture",
    "Network05": "routing-fundamentals",
    "Network06": "network-architecture-and-technologies",
    "Network07": "ip-subnetting-and-cidr",
    "Network08": "gns3-installation-and-ip-setup",
    "Network09": "router-security-and-static-routing",
    "Network10": "default-routing",
    "Network11": "network-address-translation",
    "Network12": "access-control-lists",
    "Network13": "l3-switching-and-vlan",
    "Network14": "dhcp",
    "Network15": "virtual-private-network",
    "NetworkSecurity01": "lab-environment",
    "NetworkSecurity02": "network-scanning-attacks",
    "NetworkSecurity03": "nmap-scanning",
    "NetworkSecurity04": "banner-grabbing-hping3",
    "NetworkSecurity05": "hping3-scanning",
    "NetworkSecurity06": "scanning-defense",
    "NetworkSecurity07": "lan-attacks",
    "NetworkSecurity08": "arp-spoofing",
    "WebSecurity01": "web-hacking-overview",
    "WebSecurity02": "osint-shodan-censys-ghdb",
    "WebSecurity03": "sql-injection-proxy-setup",
    "WebSecurity04": "sql-injection-auth-bypass",
    "WebSecurity05": "reflected-xss",
    "WebSecurity06": "file-upload-attacks",
    "OCI04": "account-creation-free-tier-mfa",
    "OCI05": "vcn-foundations",
    "OCI06": "identity-compartments-groups-users-policies",
    "OCI07": "compute-instance-ssh-key",
    "OCI08": "bastion-service",
    "OCI09": "network-security-and-firewall",
    "OCI10": "mysql-database-setup",
    "OCI11": "flask-application-deployment",
    "OCI12": "https-vault-ca-certificates",
    "OCI13": "load-balancer-autoscaling",
    "OCI14": "resource-cleanup-oci-cli",
    "Terraform01": "devops-and-infrastructure-as-code",
    "Terraform02": "tool-installation-vscode",
    "Terraform03": "aws-credentials-and-iam",
    "Terraform04": "terraform-commands-and-provider",
    "Terraform05": "iam-groups-policies-users",
    "Terraform06": "tfvars-and-credentials",
    "Terraform07": "single-server-deployment",
    "Terraform08": "configurable-server-variables",
    "Terraform09": "asg-web-cluster",
}

TITLE_OVERRIDES = {
    "AWS02": "VPC 기반 기본 웹 서비스 인프라 구성",
    "AWS08": "AWS IAM의 일반적인 권한 관리 패턴",
    "Kubernetes01": "VMware 노드 구성",
    "Kubernetes02": "Docker 설치",
    "Kubernetes03": "kubelet, kubeadm, kubectl 설치",
    "Kubernetes04": "Kubernetes 클러스터 구성",
    "Linux01": "리눅스 기본 명령어와 파일·경로",
    "Linux02": "리눅스 파일 권한과 ACL",
    "Linux03": "SetUID, sudo와 리눅스 권한",
    "Linux04": "vi 편집기 사용법",
    "Linux05": "dpkg, apt, tar와 sed",
    "Network01": "클라우드 환경의 개념",
    "Network02": "네트워크 기본 개념: LAN과 WAN",
    "Network03": "Packet Tracer 케이블 연결 실습",
    "Network04": "네트워크 스위치의 3계층",
    "Network05": "라우팅 기본 개념",
    "Network06": "네트워크 구성과 주요 기술",
    "Network07": "IP, Subnetting과 CIDR",
    "Network08": "GNS3 설치와 장비별 IP 설정",
    "Network09": "라우터 보안 설정과 Static Routing",
    "Network10": "Default Routing",
    "Network11": "NAT",
    "Network12": "Access Control List",
    "Network13": "L3 Switching과 VLAN",
    "Network14": "DHCP",
    "Network15": "VPN",
    "NetworkSecurity01": "네트워크 보안 실습 환경 준비",
    "NetworkSecurity04": "Banner Grabbing과 hping3 기초",
    "NetworkSecurity05": "hping3를 이용한 SYN·UDP·ICMP 스캔",
    "WebSecurity01": "웹 서비스 공격과 웹 해킹 개요",
    "WebSecurity02": "Shodan, Censys와 GHDB를 이용한 정보 수집",
    "WebSecurity03": "SQL Injection 실습 환경: Burp Suite와 프록시",
    "WebSecurity04": "SQL Injection 인증 우회와 데이터베이스 정보 획득",
    "WebSecurity05": "Reflected XSS",
    "WebSecurity06": "파일 업로드 공격",
    "OCI04": "Oracle Cloud 계정 생성과 2단계 인증",
    "OCI05": "VCN 주요 구성과 생성 실습",
    "OCI06": "Compartment, Group, User와 Policy 구성",
    "OCI07": "가상 머신과 SSH 키 생성",
    "OCI08": "OCI Bastion 서비스",
    "OCI09": "Security List, Bastion Session과 서버 방화벽",
    "OCI10": "MySQL 데이터베이스 설치와 기본 구성",
    "OCI11": "Flask, PyMySQL과 Faker 애플리케이션 배포",
    "OCI12": "OCI Vault와 CA 인증서를 이용한 HTTPS 구성",
    "OCI13": "Load Balancer와 Auto Scaling 구성",
    "OCI14": "OCI CLI와 Cloud Shell로 리소스 정리",
    "Terraform01": "DevOps와 Infrastructure as Code",
    "Terraform02": "AWS CLI와 Terraform 설치, Visual Studio Code 연동",
    "Terraform03": "Terraform을 위한 AWS Credentials와 IAM 준비",
    "Terraform04": "Terraform 기본 명령어와 Provider",
    "Terraform05": "IAM Group, Policy와 User 구성",
    "Terraform06": "terraform.tfvars와 변수 관리",
    "Terraform07": "단일 서버와 웹 서버 배포",
    "Terraform08": "변수로 구성 가능한 서버 배포",
    "Terraform09": "Auto Scaling Group 웹 서버 클러스터",
}

LINK_TITLE_OVERRIDES = {
    "AWS08": "2.2. IAM 권한 관리 패턴",
    "WebSecurity04": "04. SQL Injection 인증 우회",
}

COLLECTION_NAMES = {
    "aws-security": "AWS Security Study",
    "aws-technical-essentials": "AWS Technical Essentials Study",
    "kubernetes-cluster": "Kubernetes Cluster Study",
    "linux-fundamentals": "Linux Fundamentals Study",
    "network-fundamentals": "Network Fundamentals Study",
    "network-security": "Network Security Study",
    "oci-foundations": "OCI Foundations Study",
    "terraform-infrastructure": "Terraform Infrastructure Study",
    "web-security": "Web Security Study",
}


def prefix_and_weight(collection: str, sequence: str) -> tuple[str, int]:
    if collection == "aws-security":
        major, minor = (int(part) for part in sequence.split("."))
        return f"{major:02d}-{minor:02d}", major * 100 + minor * 10
    number = int(sequence)
    return f"{number:02d}", number * 10


def main() -> None:
    plan = json.loads((ROOT / "migration" / "full-plan.json").read_text(encoding="utf-8"))
    study = [
        item
        for item in plan["items"]
        if item["target_area"] == "Study"
    ]
    codes = {str(item["source_code"]) for item in study}
    if len(study) != 97:
        raise ValueError(f"expected 97 Study posts, found {len(study)}")
    if codes != SLUGS.keys():
        missing = sorted(codes - SLUGS.keys())
        extra = sorted(SLUGS.keys() - codes)
        raise ValueError(f"manifest mismatch: missing={missing}, extra={extra}")

    manifest: list[dict[str, object]] = []
    for item in study:
        code = str(item["source_code"])
        collection = str(item["target_collection"])
        sequence = str(item["sequence"])
        prefix, weight = prefix_and_weight(collection, sequence)
        title = TITLE_OVERRIDES.get(code, str(item["suggested_title"]))
        display_sequence = sequence if collection == "aws-security" else prefix
        destination = (
            f"content/study/{collection}/{prefix}-{SLUGS[code]}/index.md"
        )
        manifest.append(
            {
                "source": item["source"],
                "source_sha256": item["source_sha256"],
                "legacy_url": item["legacy_url"],
                "destination": destination,
                "title": title,
                "linkTitle": LINK_TITLE_OVERRIDES.get(
                    code, f"{display_sequence}. {title}"
                ),
                "section": COLLECTION_NAMES[collection],
                "weight": weight,
                "sourceStatus": "needs-review",
            }
        )

    expected_destinations = {
        "AWS08": "content/study/aws-security/02-02-iam-common-patterns/index.md",
        "Kubernetes02": "content/study/kubernetes-cluster/02-docker-installation/index.md",
        "WebSecurity04": "content/study/web-security/04-sql-injection-auth-bypass/index.md",
    }
    by_code = {
        Path(str(item["source"])).stem.split("-")[-1]: item for item in manifest
    }
    for code, destination in expected_destinations.items():
        if by_code[code]["destination"] != destination:
            raise ValueError(f"existing sample path changed: {code}")

    path = ROOT / "migration" / "study-posts.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "count": len(manifest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
