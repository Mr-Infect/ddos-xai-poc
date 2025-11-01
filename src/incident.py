# src/incident.py
import json, time
from datetime import datetime, timezone
from rich.panel import Panel
from rich.table import Table
from rich.console import Console

console = Console()

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def top_offenders(ip_counter, limit=5):
    return sorted(ip_counter.items(), key=lambda x: x[1], reverse=True)[:limit]

def format_explanation(score_obj, feat):
    # human readable, SHAP-like narrative from contributions
    contrib = score_obj.get("contributions", {})
    sorted_c = sorted(contrib.items(), key=lambda x: x[1], reverse=True)
    parts = []
    for k,v in sorted_c[:3]:
        percent = v * 100 / (sum(contrib.values())+1e-6)
        parts.append(f"{k} contributed ~{percent:.0f}% to anomaly score")
    narrative = "; ".join(parts)
    # short confidence text
    conf = "HIGH" if score_obj.get("score",0) > 70 else "MEDIUM" if score_obj.get("score",0) > 40 else "LOW"
    return narrative, conf

def feasible_mitigations(top_ips, path, confidence):
    # returns a list of mitigation suggestions ordered by safety/impact
    mitigations = []
    # safe, low-impact
    mitigations.append({
        "id": "rate_limit_path",
        "label": f"Rate-limit path {path} (10r/s)",
        "impact": "low",
        "confidence": confidence,
        "cmd_preview": f"Add nginx limit_req for location {path}"
    })
    # targeted block (medium)
    if top_ips:
        ip_list = ", ".join([ip for ip,_ in top_ips[:3]])
        mitigations.append({
            "id": "block_top_ips",
            "label": f"Temporarily DROP top offenders: {ip_list}",
            "impact": "medium",
            "confidence": confidence,
            "cmd_preview": f"iptables -I INPUT -s {ip_list} -j DROP"
        })
    # broad (higher impact)
    mitigations.append({
        "id": "enable_waf_challenge",
        "label": "Enable WAF challenge (captcha/block) for suspect path",
        "impact": "high",
        "confidence": confidence,
        "cmd_preview": "Cloudflare/WAF: present challenge on /login"
    })
    return mitigations

def build_incident(feat, score_obj, window, cfg):
    top_ips = top_offenders(window.ip_counter, limit=10)
    narrative, conf = format_explanation(score_obj, feat)
    mitigations = feasible_mitigations(top_ips, next(iter(window.path_counter)) if window.path_counter else "/", conf)
    incident = {
        "id": f"incident-{int(time.time())}",
        "time": now_iso(),
        "score": score_obj.get("score"),
        "z": score_obj.get("z"),
        "features": feat,
        "top_offenders": top_ips,
        "explanation": narrative,
        "confidence": conf,
        "recommended_mitigations": mitigations,
        "config_snapshot": cfg
    }
    return incident

def save_incident(incident, path="incidents"):
    import os
    os.makedirs(path, exist_ok=True)
    fname = f"{path}/{incident['id']}.json"
    with open(fname, "w") as fh:
        json.dump(incident, fh, indent=2)
    return fname

def pretty_print_incident(incident):
    # Rich-based attractive report
    header = Panel(f"[bold red]ALERT[/bold red] • Score {incident['score']:.1f} • Confidence: {incident['confidence']}",
                   title=f"Incident {incident['id']}", style="red")
    console.print(header)

    t = Table.grid(expand=False)
    t.add_column(justify="left", ratio=1)
    t.add_column(justify="left", ratio=2)
    t.add_row("[bold]Time[/bold]", incident["time"])
    t.add_row("[bold]Top features[/bold]", ", ".join([f"{k}:{v:.2f}" for k,v in incident["z"].items()]))
    t.add_row("[bold]Explanation[/bold]", incident["explanation"])
    t.add_row("[bold]Requests (window)[/bold]", str(incident["features"].get("requests")))
    t.add_row("[bold]Unique IPs[/bold]", str(incident["features"].get("unique_ips")))
    console.print(Panel(t, title="Summary", expand=False))

    # Top offenders table
    ips = Table(title="Top Offending IPs (sample)", show_lines=True)
    ips.add_column("IP", justify="left")
    ips.add_column("Hits", justify="right")
    for ip, cnt in incident["top_offenders"][:10]:
        ips.add_row(ip, str(cnt))
    console.print(ips)

    # Mitigations
    m = Table(title="Recommended Mitigations (ordered by safety)", show_lines=True)
    m.add_column("Option", justify="left")
    m.add_column("Impact", justify="center")
    m.add_column("Confidence", justify="center")
    m.add_column("Command Preview", justify="left")
    for mm in incident["recommended_mitigations"]:
        m.add_row(mm["label"], mm["impact"], mm["confidence"], mm["cmd_preview"])
    console.print(m)

    console.print(Panel("[bold]Operator action:[/bold] Choose mitigation id and confirm. (Demo mode: dry-run only = commands are previews)", title="Next Steps", style="cyan"))
