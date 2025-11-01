# src/executor.py
import shlex, subprocess, time

def build_iptables_block_cmd(ip):
    return f"sudo iptables -I INPUT -s {ip} -j DROP"

def build_nginx_rate_limit_cmd(location, limit="10r/s"):
    # This is a helper: we propose a command that would add a snippet in site config — manual review required
    return f"echo \"# RATE LIMIT STRATEGY: add limit_req zone and location {location}\""

def show_command(cmd):
    print("[EXECUTE CMD] (dry-run) ->", cmd)

def run_command(cmd):
    """Run a CLI command — explicit operator approval required before calling this function."""
    parts = shlex.split(cmd)
    proc = subprocess.run(parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr
