import boto3
from botocore.exceptions import ClientError


def check_s3():
    s3 = boto3.client("s3")
    findings = []
    for bucket in s3.list_buckets().get("Buckets", []):
        name = bucket["Name"]
        try:
            cfg = s3.get_public_access_block(Bucket=name)["PublicAccessBlockConfiguration"]
            blocked = all(cfg.values())
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                blocked = False
            else:
                findings.append({"check": "S3", "resource": name, "status": "ERROR",
                                 "detail": e.response["Error"]["Code"]})
                continue
        try:
            is_public = s3.get_bucket_policy_status(Bucket=name)["PolicyStatus"]["IsPublic"]
        except ClientError:
            is_public = False  # no bucket policy at all
        if is_public:
            status, detail = "FAIL", "Bucket policy makes this bucket PUBLIC"
        elif not blocked:
            status, detail = "WARN", "Block Public Access is not fully turned on"
        else:
            status, detail = "PASS", "Block Public Access is on"
        findings.append({"check": "S3", "resource": name, "status": status, "detail": detail})
    return findings


if __name__ == "__main__":
    for f in check_s3():
        print(f"[{f['status']}] {f['resource']} - {f['detail']}")
