# src/tui.py
import argparse, time, re, yaml, json, asyncio
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

from .tailer import tail_file
from .window import SlidingWindow
from .detector import CompositeScorer
from .executor import build_iptables_block_cmd, show_command, run_command
from .incident import build_incident, save_incident, pretty_print_incident

console = Console()

NGINX_LOG_RE = re.compile(r'(?P<ip>\S+) .*? ".*? (?P<path>\S+) .*?" .*? "?(?P<ua>.*?)"?$')

def parse_nginx_line(line):
    m = NGINX_LOG_RE.match(line)
    if not m:
        parts = line.split()
        ip = parts[0] if parts else "unknown"
        path = parts[6] if len(parts) > 6 else "/"
        ua = line.split('"')[-1]
        return ip, path, ua
    return m.group('ip'), m.group('path'), m.group('ua')

async def main_loop(args, cfg):
    window = SlidingWindow(args.window)
    scorer = CompositeScorer(cfg)
    alert_history = []  # persistent list of incidents (in-session)
    dashboard_refresh = 4

    async for line in tail_file(args.logfile, poll=args.poll):
        ts = time.time()
        ip, path, ua = parse_nginx_line(line)
        window.add(ts, ip, path, ua)
        feat = window.features()
        score_obj = scorer.score(feat)

        # build small summary view
        table = Table.grid()
        table.add_column()
        table.add_row(f"[bold]Log:[/bold] {args.logfile}")
        table.add_row(f"[bold]Requests in window:[/bold] {feat['requests']}")
        table.add_row(f"[bold]Unique IPs:[/bold] {feat['unique_ips']}")
        table.add_row(f"[bold]Composite score:[/bold] {score_obj['score']:.1f} | Z(req): {score_obj['z']['requests']:.2f}")

        # persistent alert display: show last 3 incidents summary
        if alert_history:
            recent = alert_history[-3:]
            s = "\n".join([f"{i['id']} • {i['time']} • score {i['score']:.1f} • conf {i['confidence']}" for i in recent])
            table.add_row(Panel(s, title="Recent Incidents", style="magenta"))

        with Live(table, refresh_per_second=dashboard_refresh, transient=False):
            # check alert condition
            if scorer.is_alert(score_obj) and feat['requests'] >= cfg.get("min_requests_for_alert", 200):
                # create incident
                incident = build_incident(feat, score_obj, window, cfg)
                # save to disk for audit
                path = save_incident(incident)
                alert_history.append(incident)

                # pretty print detailed report (blocks until operator input)
                pretty_print_incident(incident)

                # operator interaction (non-blocking behavior not required for demo)
                choice = console.input("Choose action id to preview/run (or press Enter to skip): ").strip()
                if choice:
                    # find mitigation
                    found = next((m for m in incident["recommended_mitigations"] if choice in (m["id"], m["label"], m["cmd_preview"])), None)
                    # if user typed a simple number mapping, map to list index
                    if not found:
                        try:
                            idx = int(choice) - 1
                            found = incident["recommended_mitigations"][idx]
                        except Exception:
                            found = None
                    if found:
                        console.print(f"[yellow]Selected:[/yellow] {found['label']}")
                        show_command(found["cmd_preview"])
                        if not cfg.get("dry_run", True):
                            ans = console.input("Run this command? (y/n): ").strip().lower()
                            if ans == "y":
                                rc, out, err = run_command(found["cmd_preview"])
                                console.print(f"rc={rc}\nout={out}\nerr={err}")
                        else:
                            console.print("[green]Dry-run mode enabled — command not executed.[/green]")
                    else:
                        console.print("[red]No matching mitigation found. Skipping.[/red]")

                console.print(f"[blue]Incident saved to:[/blue] {path}")
                # after report is shown, keep it in alert_history so dashboard displays it
        await asyncio.sleep(0.01)

def load_cfg(path):
    with open(path, 'r') as fh:
        return yaml.safe_load(fh)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", required=True)
    parser.add_argument("--window", type=int, default=60)
    parser.add_argument("--poll", type=float, default=1.0)
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    cfg = load_cfg(args.config)
    try:
        asyncio.run(main_loop(args, cfg))
    except KeyboardInterrupt:
        console.print("Shutting down.")
