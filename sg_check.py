import boto3

RISKY_PORTS = {22: "SSH", 3389: "RDP", 3306: "MySQL", 5432: "PostgreSQL"}
SAFE_WEB = [(80, 80), (443, 443)]


def _open_to_world(rule):
    v4 = any(r.get("CidrIp") == "0.0.0.0/0" for r in rule.get("IpRanges", []))
    v6 = any(r.get("CidrIpv6") == "::/0" for r in rule.get("Ipv6Ranges", []))
    return v4 or v6


def check_security_groups():
    ec2 = boto3.client("ec2")
    findings = []
    for page in ec2.get_paginator("describe_security_groups").paginate():
        for sg in page["SecurityGroups"]:
            label = f"{sg['GroupId']} ({sg['GroupName']})"
            problems = []
            for rule in sg.get("IpPermissions", []):
                if not _open_to_world(rule):
                    continue
                proto = rule.get("IpProtocol")
                if proto == "-1":
                    problems.append(("FAIL", "ALL traffic is open to the internet"))
                    continue
                if proto in ("icmp", "icmpv6"):
                    problems.append(("WARN", "Ping (ICMP) is open to the internet"))
                    continue
                low, high = rule.get("FromPort"), rule.get("ToPort")
                risky = [n for p, n in RISKY_PORTS.items() if low <= p <= high]
                if risky:
                    problems.append(("FAIL", f"{', '.join(risky)} open to the internet"))
                elif (low, high) not in SAFE_WEB:
                    problems.append(("WARN", f"Port {low}-{high} open to the internet"))
            if not problems:
                findings.append({"check": "Security Group", "resource": label,
                                 "status": "PASS", "detail": "No risky internet access"})
            for status, detail in problems:
                findings.append({"check": "Security Group", "resource": label,
                                 "status": status, "detail": detail})
    return findings


if __name__ == "__main__":
    for f in check_security_groups():
        print(f"[{f['status']}] {f['resource']} - {f['detail']}")
