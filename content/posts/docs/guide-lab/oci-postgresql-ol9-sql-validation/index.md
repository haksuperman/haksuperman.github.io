---
title: "OCI Database with PostgreSQL — Oracle Linux 9 접속 및 SQL 실행 사전 검증"
date: "2026-11-23T23:10:00+09:00"
draft: false
collection: docs
docCategory: guide-lab
tags: ["OCI","PostgreSQL","Oracle Linux","TLS","psql"]
---

> 이 문서는 [Notion 원문](https://app.notion.com/p/40f9263dda2e81529adfc3ca411ee87c)의 기술 절차를 Markdown으로 옮긴 글입니다. 원문 스크린샷 12장은 현재 포함되어 있지 않으며, 화면 예시는 원문에서 확인할 수 있습니다.

**☝🏼 참고 / 주의**


**목표:** Oracle Linux 9 Compute VM에서 OCI Database with PostgreSQL로 TLS 접속하고 SQL 실행을 검증한다.


---


---


# 1. 구성 개요

```txt
Oracle Linux 9 Compute VM
  └─ PostgreSQL client (psql)
       └─ Private network / TCP 5432 / TLS
            └─ OCI Database with PostgreSQL
```

OCI Database with PostgreSQL 엔드포인트는 인터넷에서 직접 접근할 수 없다. VM은 DB 엔드포인트로 사설 통신 가능한 VCN 경로에 있어야 한다. 가장 단순한 구성은 동일 VCN이며, 서로 다른 VCN이면 피어링/DRG 등 실제 환경의 라우팅 구성이 필요하다.

| 구분 | 플레이스홀더 |
| --- | --- |
| OCI 리전 | ``<REGION>`` |
| Compartment | `<COMPARTMENT_NAME>` |
| VM 이름 | `<OL9_VM_NAME>` |
| VM Private IP | `<OL9_VM_PRIVATE_IP>` |
| VM NSG | `<OL9_VM_NSG>` |
| DB System 이름 | `<OCI_PG_DB_SYSTEM_NAME>` |
| DB 엔드포인트 FQDN | `<DB_ENDPOINT_FQDN>` |
| DB Private IP(참고용) | `<DB_PRIVATE_IP>` |
| DB 포트 | `5432` |
| DB 이름 | `<DATABASE_NAME>` |
| 접속 사용자 | `<DB_USER>` |
| DB NSG | `<DB_NSG>` |
| CA 인증서 파일 | `/home/opc/.postgresql/oci-db-system-ca.pem` |

# 2. 사전 준비 및 주의사항

- OCI Database with PostgreSQL DB System이 `ACTIVE` 상태여야 한다.
- OL9 VM에 SSH 접속할 수 있어야 한다.
- DB System 상세 화면에서 엔드포인트 FQDN과 CA 인증서를 확인할 권한이 있어야 한다.
- VM과 DB 사이에 사설 라우팅 및 보안 규칙이 준비되어야 한다.
- DB 사용자 이름과 암호를 준비한다. 암호는 문서, 셸 기록, 명령행 인자에 평문으로 남기지 않는다.
- `verify-full`에서는 인증서의 호스트 이름 검증이 수행되므로, IP가 아니라 DB System 화면의 **FQDN**을 `host`로 사용한다.
- 클라이언트 버전은 가능하면 DB 서버의 메이저 버전과 같거나 호환 가능한 버전을 사용한다.


# 3. 네트워크 및 보안 규칙 확인

## 3.1 경로 확인

- 동일 VCN: 서브넷 간 로컬 라우팅 경로와 NSG/Security List를 확인한다.
- 다른 VCN: Local Peering Gateway, DRG 또는 실제 구성에 맞는 경로와 양쪽 Route Table을 확인한다.
- DB 엔드포인트는 인터넷 직접 접속 대상이 아니다. 이 실습은 DB로 사설 통신 가능한 OL9 VM에서 수행한다.

## 3.2 권장 NSG 규칙

Oracle은 애플리케이션 보안 요구사항을 서브넷 구조와 분리할 수 있는 NSG 사용을 권장한다.

**DB NSG Ingress**

| 항목 | 값 |
| --- | --- |
| Source Type | Network Security Group 권장, 또는 CIDR |
| Source | `<OL9_VM_NSG>` 또는 `<OL9_VM_PRIVATE_IP>/32` |
| IP Protocol | TCP |
| Source Port | All |
| Destination Port | `5432` |
| Stateful | Yes 권장 |
| 설명 | OL9 VM에서 OCI PostgreSQL 접속 |

**VM 측 Egress가 제한된 경우**

| 항목 | 값 |
| --- | --- |
| Destination Type | Network Security Group 또는 CIDR |
| Destination | `<DB_NSG>` 또는 `<DB_SUBNET_CIDR>` |
| IP Protocol | TCP |
| Destination Port | `5432` |
| Stateful | Yes 권장 |

Security List와 NSG를 함께 사용하는 환경에서는 실제 적용되는 모든 규칙을 확인한다. Stateful 규칙은 허용된 연결의 응답 트래픽을 자동 추적한다.


# 4. 엔드포인트와 CA 인증서 준비

OCI Console에서 다음 경로로 이동한다.

1. **Databases → PostgreSQL → DB Systems**
2. `<OCI_PG_DB_SYSTEM_NAME>` 선택
3. **Connection details**에서 `<DB_ENDPOINT_FQDN>` 확인
4. 같은 영역에서 CA 인증서 다운로드
   


다운로드한 인증서를 안전한 방법으로 OL9 VM에 전송한 뒤 다음처럼 배치한다.

```bash
mkdir -p /home/opc/.postgresql
mv <DOWNLOADED_CA_FILE> /home/opc/.postgresql/
chmod 700 /home/opc/.postgresql
chmod 600 /home/opc/.postgresql/CaCertificate-psql17.pub
ls -l /home/opc/.postgresql/CaCertificate-psql17.pub
```


인증서 내용을 점검한다.

```bash
openssl x509   -in /home/opc/.postgresql/CaCertificate-psql17.pub   -noout -subject -issuer -dates
```


**🔐 참고 / 주의**


OCI Database with PostgreSQL은 SSL 연결만 허용한다. 운영 수준의 검증에는 서버 인증서 체인과 호스트 이름을 모두 확인하는 `sslmode=verify-full`을 사용한다.


# 5. Oracle Linux 9에 psql 설치

먼저 OS와 사용 가능한 패키지를 확인한다.

```bash
cat /etc/oracle-release
sudo dnf repolist
sudo dnf info postgresql
```


기본 저장소에서 PostgreSQL 클라이언트를 설치한다.

```bash
sudo dnf install -y postgresql
psql --version
```


환경에 따라 기본 패키지 버전이 DB System과 다를 수 있다. 조직에서 PostgreSQL 공식 PGDG 저장소 또는 별도 승인 저장소를 사용하는 경우에는 해당 표준에 맞는 버전 패키지를 설치한다. 이 VM에는 접속 검증을 위해 PostgreSQL **서버 데몬**을 설치하거나 기동할 필요가 없다.

# 6. DNS와 TCP 5432 사전 점검

## 6.1 DNS 확인

```bash
getent ahostsv4 <DB_ENDPOINT_FQDN>
```


결과가 없으면 VCN DNS, 사용자 지정 DNS, DHCP Options, 엔드포인트 FQDN 오타를 확인한다.

## 6.2 TCP 포트 확인

추가 패키지 없이 Bash TCP 기능으로 점검하는 예시이다.

```bash
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/<DB_ENDPOINT_FQDN>/5432'   && echo "TCP 5432 reachable"   || echo "TCP 5432 failed"
```


`nc`가 설치되어 있다면 다음도 사용할 수 있다.

```bash
nc -vz -w 5 <DB_ENDPOINT_FQDN> 5432
```

# 7. psql로 TLS 접속

암호를 셸 명령행에 포함하지 않고 `-W`로 대화형 입력한다.

```bash
psql -W \
"host=<DB_ENDPOINT_FQDN> \
port=5432 \
dbname=<DATABASE_NAME> \
user=<DB_USER> \
sslmode=verify-full \
sslrootcert=/home/opc/.postgresql/CaCertificate-psql17.pub \
connect_timeout=10 \
application_name=ol9-precheck"
```


정상 접속 후 `psql` 메타 명령으로 연결 정보를 확인한다.

```sql
\conninfo
```


# 8. SQL 실행 및 검증

## 8.1 기본 정보 확인

```sql
SELECT current_database() AS database_name;
SELECT current_user AS login_user;
SELECT version();
SELECT now() AS db_time;
```


## 8.2 현재 세션의 TLS 확인

```sql
SELECT
    ssl,
    version,
    cipher,
    bits,
    client_dn
FROM pg_stat_ssl
WHERE pid = pg_backend_pid();
```


판정 기준:

- `ssl = true`
- `version`에 협상된 TLS 버전 표시
- `cipher`와 `bits` 값 표시

## 8.3 롤백 가능한 쓰기 SQL 검증

영구 객체를 남기지 않도록 트랜잭션과 임시 테이블을 사용한다.

```sql
BEGIN;

CREATE TEMP TABLE ol9_connection_test (
    id          integer,
    message     text,
    created_at  timestamptz DEFAULT now()
);

INSERT INTO ol9_connection_test (id, message)
VALUES (1, 'OCI PostgreSQL connection test');

SELECT * FROM ol9_connection_test;

ROLLBACK;
```


`ROLLBACK` 후 임시 테이블이 현재 세션에 남아 있을 수 있으므로 명시적으로 정리하려면 다음을 실행한다.

```sql
DROP TABLE IF EXISTS ol9_connection_test;
```

# 9. SQL 파일로 일괄 검증

다음 내용을 `/home/opc/oci_pg_precheck.sql`로 저장한다.

```sql
\set ON_ERROR_STOP on

SELECT current_database() AS database_name;
SELECT current_user AS login_user;
SELECT version();
SELECT now() AS db_time;

SELECT ssl, version, cipher, bits
FROM pg_stat_ssl
WHERE pid = pg_backend_pid();

BEGIN;
CREATE TEMP TABLE ol9_connection_test (
    id integer,
    message text,
    created_at timestamptz DEFAULT now()
);
INSERT INTO ol9_connection_test (id, message)
VALUES (1, 'OCI PostgreSQL connection test');
SELECT * FROM ol9_connection_test;
ROLLBACK;
```

실행한다.

```bash
psql -W \
"host=<DB_ENDPOINT_FQDN> \
port=5432 \
dbname=<DATABASE_NAME> \
user=<DB_USER> \
sslmode=verify-full \
sslrootcert=/home/opc/.postgresql/CaCertificate-psql17.pub \
connect_timeout=10 \
application_name=ol9-precheck" \
-f /home/opc/oci_pg_precheck.sql
```


실행 직후 다음을 실행해 종료코드까지 확인한다.  
`0`이면 모든 SQL이 오류 없이 실행된 것이다.

```bash
echo $?
```


# 10. 오류 진단

| 증상/메시지 | 주요 원인 | 확인 및 조치 |
| --- | --- | --- |
| `could not translate host name` | DNS 해석 실패, FQDN 오타 | Connection details의 FQDN 재확인, `getent ahostsv4`, VCN DNS/DHCP Options 확인 |
| `connection timed out` | 라우팅, NSG, Security List, ZPR 정책, egress 제한 | VM→DB 경로와 TCP 5432 양쪽 규칙 확인 |
| `connection refused` | 잘못된 주소/포트 또는 서비스 상태 | DB System이 ACTIVE인지, FQDN과 포트 5432가 맞는지 확인 |
| `no pg_hba.conf entry ... no encryption` | SSL 없이 연결 시도 | `sslmode=require` 이상 사용. 본 가이드는 `verify-full` 사용 |
| `root certificate file ... does not exist` | CA 경로 오류/권한 문제 | `ls -l`, 절대 경로, 실행 사용자 권한 확인 |
| `certificate verify failed` | 잘못된 CA 파일, 파일 손상, 인증서 갱신 | DB System에서 CA 재다운로드 후 `openssl x509` 확인 |
| `server certificate for ... does not match host name` | IP 또는 별칭으로 접속 | `host=<DB_ENDPOINT_FQDN>` 사용. verify-full에서 IP 우회 금지 |
| `password authentication failed` | 사용자/암호 오류 | 사용자 이름, 대상 DB, 암호 재확인. 암호 만료/잠금 정책 확인 |
| `database ... does not exist` | DB 이름 오류 | 실제 생성된 DB 이름 또는 관리자가 지정한 DB 확인 |
| `permission denied` | SQL 권한 부족 | 해당 SQL에 필요한 최소 권한을 관리자에게 요청 |
| psql 명령 없음 | 클라이언트 미설치/경로 문제 | `sudo dnf install -y postgresql`, `command -v psql` 확인 |

추가 확인 명령:

```bash
command -v psql
psql --version
getent ahostsv4 <DB_ENDPOINT_FQDN>
ip route
ls -l /home/opc/.postgresql/oci-db-system-ca.pem
openssl x509 -in /home/opc/.postgresql/oci-db-system-ca.pem -noout -subject -issuer -dates
```


**⚠️ 참고 / 주의**


문제 해결을 위해 `sslmode=disable`로 낮추지 않는다. OCI Database with PostgreSQL은 비SSL 연결을 지원하지 않는다. 일시적으로 `require`를 사용해 인증서 문제와 네트워크 문제를 분리 진단할 수는 있지만, 최종 성공 판정은 반드시 `verify-full`로 수행한다.


# 11. 공식 참고 문서

- [Oracle — Connecting to a Database in OCI Database with PostgreSQL](https://docs.oracle.com/en-us/iaas/Content/postgresql/connect-to-db.htm)
- [Oracle — Configure Secure Socket Layer in OCI Database with PostgreSQL](https://docs.oracle.com/en/learn/oci-pgsql-ssl/index.html)
- [Oracle — OCI Network Security Rules](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securityrules.htm)
- [Oracle — Network Security Groups](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/networksecuritygroups.htm)
- [Oracle — Use DNF on Oracle Linux](https://docs.oracle.com/en/learn/ol-dnf/)
- [PostgreSQL — Database Connection Control Functions](https://www.postgresql.org/docs/current/libpq-connect.html)
- [PostgreSQL — SSL Support](https://www.postgresql.org/docs/current/libpq-ssl.html)
