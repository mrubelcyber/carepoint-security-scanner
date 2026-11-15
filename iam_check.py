import boto3


def check_iam_mfa():
    iam = boto3.client("iam")
    findings = []
    for page in iam.get_paginator("list_users").paginate():
        for user in page["Users"]:
            name = user["UserName"]
            try:
                iam.get_login_profile(UserName=name)
                has_console = True
            except iam.exceptions.NoSuchEntityException:
                has_console = False
            has_mfa = len(iam.list_mfa_devices(UserName=name)["MFADevices"]) > 0
            if not has_console:
                status, detail = "PASS", "No console password (console MFA not needed)"
            elif has_mfa:
                status, detail = "PASS", "Console user has MFA"
            else:
                status, detail = "FAIL", "Console password but NO MFA"
            findings.append({"check": "IAM MFA", "resource": name, "status": status, "detail": detail})
    return findings


if __name__ == "__main__":
    for f in check_iam_mfa():
        print(f"[{f['status']}] {f['resource']} - {f['detail']}")
