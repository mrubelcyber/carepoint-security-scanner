# CarePoint Shield

A read-only AWS security scanner for a small hospital cloud (fictional CarePoint Health).

## What it checks
| Check | FAIL when |
| --- | --- |
| S3 buckets | Bucket policy makes the bucket public (WARN if Block Public Access is off) |
| Security groups | SSH, RDP, MySQL, PostgreSQL or all traffic open to 0.0.0.0/0 |
| IAM users | Console password without MFA |

## How to run (AWS CloudShell)
Run `python3 scanner.py`. Results print to the screen and are saved to `report.html` (not committed).

## Permissions needed (read-only)
s3:ListAllMyBuckets, s3:GetBucketPublicAccessBlock, s3:GetBucketPolicyStatus,
ec2:DescribeSecurityGroups, iam:ListUsers, iam:GetLoginProfile, iam:ListMFADevices,
sts:GetCallerIdentity

## Built with
Python, boto3, AWS CloudShell
