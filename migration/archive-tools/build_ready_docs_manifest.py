#!/usr/bin/env python3
"""Build the first-batch Docs migration manifest from the reviewed full plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]

# source_code: (destination, title, linkTitle, optional weight)
READY_DOCS: dict[str, tuple[str, str, str, Optional[int]]] = {
    "AWS01": (
        "content/docs/guide-lab/aws-saa-c03-pass-review/index.md",
        "AWS SAA-C03 일주일 합격 후기",
        "AWS SAA-C03 합격 후기",
        None,
    ),
    "AWS03": (
        "content/docs/guide-lab/aws-scs-c02-pass-review/index.md",
        "AWS SCS-C02 시험을 두 번 미룬 직장인의 합격 후기",
        "AWS SCS-C02 합격 후기",
        None,
    ),
    "Kubernetes05": (
        "content/docs/command-tool/windows-kubectl/index.md",
        "Windows에 kubectl을 설치해 원격 Kubernetes 클러스터 관리하기",
        "Windows kubectl",
        None,
    ),
    "Linux06": (
        "content/docs/command-tool/linux-commands/index.md",
        "엔지니어를 위한 Linux 명령어",
        "Linux 명령어",
        None,
    ),
    "MultiCloud01": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/01-overview/index.md",
        "AWS–OCI BGP VPN 이중화 개요",
        "01. 개요",
        10,
    ),
    "MultiCloud02": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/02-vpn1-aws-temporary-cgw/index.md",
        "VPN 1 구성: AWS 임시 Customer Gateway",
        "02. VPN 1 — AWS 임시 CGW",
        20,
    ),
    "MultiCloud03": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/03-vpn1-oci/index.md",
        "VPN 1 구성: OCI CPE와 VPN",
        "03. VPN 1 — OCI",
        30,
    ),
    "MultiCloud04": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/04-vpn1-aws-final-cgw/index.md",
        "VPN 1 구성: AWS Customer Gateway와 PSK",
        "04. VPN 1 — AWS CGW와 PSK",
        40,
    ),
    "MultiCloud05": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/05-vpn1-validation/index.md",
        "VPN 1 연결 결과 확인",
        "05. VPN 1 결과 확인",
        50,
    ),
    "MultiCloud06": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/06-vpn2-aws-temporary-cgw/index.md",
        "VPN 2 구성: AWS Transit Gateway와 임시 Customer Gateway",
        "06. VPN 2 — AWS 임시 CGW",
        60,
    ),
    "MultiCloud07": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/07-vpn2-oci/index.md",
        "VPN 2 구성: OCI CPE와 VPN",
        "07. VPN 2 — OCI",
        70,
    ),
    "MultiCloud08": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/08-vpn2-aws-final-cgw/index.md",
        "VPN 2 구성: AWS Customer Gateway와 PSK",
        "08. VPN 2 — AWS CGW와 PSK",
        80,
    ),
    "MultiCloud09": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/09-vpn2-validation/index.md",
        "VPN 2 연결 결과 확인",
        "09. VPN 2 결과 확인",
        90,
    ),
    "MultiCloud10": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/10-connectivity-test/index.md",
        "AWS–OCI VPN 통신 확인",
        "10. 통신 확인",
        100,
    ),
    "MultiCloud11": (
        "content/docs/guide-lab/aws-oci-bgp-vpn/11-dynamic-routing-retrospective/index.md",
        "BGP 동적 라우팅 결과와 회고",
        "11. 동적 라우팅과 회고",
        110,
    ),
    "OCI01": (
        "content/docs/theory-reference/oci-services-compared-with-aws/index.md",
        "OCI 주요 서비스와 AWS 대응 관계",
        "OCI 서비스와 AWS 비교",
        None,
    ),
    "OCI02": (
        "content/docs/command-tool/oci-access-methods/index.md",
        "OCI에 접근하는 방법",
        "OCI 접근 방법",
        None,
    ),
    "OCI03": (
        "content/docs/theory-reference/oci-foundations/index.md",
        "Oracle Cloud Infrastructure 기본 개념",
        "OCI 기본 개념",
        None,
    ),
    "OCI15": (
        "content/docs/guide-lab/oci-development-vm-docker/index.md",
        "OCI 개발용 가상 머신과 Docker 구성",
        "OCI VM과 Docker",
        None,
    ),
    "OCI16": (
        "content/docs/command-tool/oci-object-storage-cyberduck/index.md",
        "Cyberduck으로 OCI Object Storage 사용하기",
        "OCI Object Storage와 Cyberduck",
        None,
    ),
    "OCI17": (
        "content/docs/guide-lab/oci-lb-domain-redirect/index.md",
        "OCI Load Balancer Ruleset으로 도메인 리다이렉트하기",
        "OCI LB 도메인 리다이렉트",
        None,
    ),
    "OCI18": (
        "content/docs/guide-lab/oci-lb-add-www/index.md",
        "OCI Load Balancer Ruleset으로 www 강제하기",
        "OCI LB www 강제",
        None,
    ),
    "OCI19": (
        "content/docs/theory-reference/oke-cni-plugin/index.md",
        "OKE 클러스터의 CNI 플러그인",
        "OKE CNI 플러그인",
        None,
    ),
    "OCI20": (
        "content/docs/guide-lab/oke-network-setup/index.md",
        "OKE 클러스터 네트워크 구성",
        "OKE 네트워크 구성",
        None,
    ),
    "OCI21": (
        "content/docs/guide-lab/oke-cluster-deployment/index.md",
        "OKE 클러스터 배포",
        "OKE 클러스터 배포",
        None,
    ),
    "OCI22": (
        "content/docs/guide-lab/oke-access-setup/index.md",
        "OKE 클러스터 접속 환경 구성",
        "OKE 접속 환경",
        None,
    ),
    "OCI23": (
        "content/docs/guide-lab/oke-sample-workload/index.md",
        "OKE에 Sample 파드와 서비스 배포하기",
        "OKE Sample 워크로드",
        None,
    ),
    "OCI24": (
        "content/docs/theory-reference/oke-persistent-volume-overview/index.md",
        "OKE PersistentVolume 개요",
        "OKE PersistentVolume 개요",
        None,
    ),
    "OCI25": (
        "content/docs/guide-lab/oke-block-volume-iscsi/index.md",
        "OKE Block Volume 구성: iSCSI",
        "OKE Block Volume — iSCSI",
        None,
    ),
    "OCI26": (
        "content/docs/guide-lab/oke-block-volume-paravirtualized/index.md",
        "OKE Block Volume 구성: Paravirtualized",
        "OKE Block Volume — Paravirtualized",
        None,
    ),
    "OCI27": (
        "content/docs/guide-lab/oke-file-storage-dynamic-provisioning/index.md",
        "OKE File Storage 동적 프로비저닝",
        "OKE File Storage — 동적",
        None,
    ),
    "OCI28": (
        "content/docs/guide-lab/oke-file-storage-static-provisioning/index.md",
        "OKE File Storage 정적 프로비저닝",
        "OKE File Storage — 정적",
        None,
    ),
    "OCI29": (
        "content/docs/theory-reference/oke-node-cycling/index.md",
        "OKE Node Cycling 개요",
        "OKE Node Cycling",
        None,
    ),
    "OCI30": (
        "content/docs/guide-lab/oci-console-network-perimeters/index.md",
        "Network Perimeters로 OCI Console 접근 제어하기",
        "OCI Console 접근 제어",
        None,
    ),
    "OCI31": (
        "content/docs/guide-lab/oci-bastion-private-instance/index.md",
        "OCI Bastion과 Passphrase SSH Key를 이용한 Private Instance 보안 접속",
        "OCI Bastion 보안 접속",
        None,
    ),
}


def main() -> None:
    plan = json.loads((ROOT / "migration" / "full-plan.json").read_text(encoding="utf-8"))
    ready = [item for item in plan["items"] if item["review_status"] == "ready"]
    ready_codes = {str(item["source_code"]) for item in ready}
    if len(ready) != 35:
        raise ValueError(f"expected 35 ready Docs posts, found {len(ready)}")
    if ready_codes != READY_DOCS.keys():
        missing = sorted(ready_codes - READY_DOCS.keys())
        extra = sorted(READY_DOCS.keys() - ready_codes)
        raise ValueError(f"manifest mismatch: missing={missing}, extra={extra}")

    manifest: list[dict[str, object]] = []
    for item in ready:
        code = str(item["source_code"])
        destination, title, link_title, weight = READY_DOCS[code]
        output: dict[str, object] = {
            "source": item["source"],
            "source_sha256": item["source_sha256"],
            "legacy_url": item["legacy_url"],
            "destination": destination,
            "title": title,
            "linkTitle": link_title,
            "section": item["target_section"],
        }
        if weight is not None:
            output["weight"] = weight
        manifest.append(output)

    path = ROOT / "migration" / "ready-docs.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "count": len(manifest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
