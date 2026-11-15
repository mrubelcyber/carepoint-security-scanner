import html
from datetime import datetime, timezone

import boto3

from s3_check import check_s3
from sg_check import check_security_groups
from iam_check import check_iam_mfa

COLORS = {"PASS": "#16a34a", "WARN": "#d97706", "FAIL": "#dc2626", "ERROR": "#6b7280"}


def main():
    account = boto3.client("sts").get_caller_identity()["Account"]
    masked = "********" + account[-4:]
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    findings = check_s3() + check_security_groups() + check_iam_mfa()
    counts = {s: sum(1 for f in findings if f["status"] == s) for s in COLORS}

    print(f"CarePoint Shield scan - account {masked} - {when}")
    for f in findings:
        print(f"[{f['status']:5}] {f['check']:15} {f['resource']} - {f['detail']}")
    print("Summary:", ", ".join(f"{k}={v}" for k, v in counts.items()))

    rows = "".join(
        f"<tr><td style='color:{COLORS[f['status']]};font-weight:bold'>{f['status']}</td>"
        f"<td>{html.escape(f['check'])}</td><td>{html.escape(f['resource'])}</td>"
        f"<td>{html.escape(f['detail'])}</td></tr>"
        for f in sorted(findings, key=lambda f: ["FAIL", "WARN", "ERROR", "PASS"].index(f["status"]))
    )
    summary = " &nbsp; ".join(
        f"<span style='color:{COLORS[k]};font-weight:bold'>{k}: {v}</span>" for k, v in counts.items()
    )
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>CarePoint Shield Report</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;color:#0f172a}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #cbd5e1;padding:8px;text-align:left}}
th{{background:#0b1f3a;color:white}}</style></head><body>
<h1>CarePoint Shield - Security Report</h1>
<p>Account: {masked} &nbsp;|&nbsp; Scanned: {when}</p><p>{summary}</p>
<table><tr><th>Status</th><th>Check</th><th>Resource</th><th>Detail</th></tr>{rows}</table>
</body></html>"""
    with open("report.html", "w") as fh:
        fh.write(page)
    print("Report saved to report.html")


if __name__ == "__main__":
    main()
