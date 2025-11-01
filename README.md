# 🧠 AI-Driven DDoS Detection & Explainable Response System

> **“An intelligent cybersecurity sentinel that not only detects DDoS anomalies but explains, recommends, and acts.”**

---

## 🚀 Overview

This project is a **CLI-based real-time DDoS attack detection and mitigation assistant** powered by a **lightweight AI model** designed for live terminal execution.  
The system continuously monitors network logs (e.g., Nginx access logs) for **anomalous traffic behavior** and dynamically generates **explainable incident reports** — identifying attackers, explaining anomalies, and recommending mitigation strategies.

It simulates a real-world **Security Operations Center (SOC)** workflow:
- **Terminal 1**: Real-time DDoS detection and AI explanation  
- **Terminal 2**: Simulated attack traffic generator

This architecture creates a **self-contained demonstration of AI-assisted defense automation** that is both functional and visually impressive.

---

## 🧩 Core Concept

| Component | Description |
|------------|-------------|
| **Traffic Stream Analyzer** | Parses access logs in real-time, extracting request rates, IP counts, and endpoint patterns. |
| **AI Anomaly Scorer** | A hybrid scoring engine combining statistical z-scores and lightweight ML-based heuristics to identify attack-like deviations. |
| **Explainable AI Engine (XAI)** | Generates human-readable justifications for each alert — explaining *why* it triggered and *which features* contributed most. |
| **Incident Response Generator** | Builds structured reports (in JSON and terminal UI) including risk level, probable sources, and recommended mitigation commands. |
| **Interactive CLI Dashboard** | Uses `Rich` library to render a live dashboard and persistent alert feed for operator decision-making. |

---

## 🧠 Explainable AI (XAI) Dimension

Traditional anomaly detectors output numeric scores with no context.  
This project integrates **Explainable AI (XAI)** principles to make detection **transparent and auditable**:

- Identifies *which traffic features* (requests, unique IPs, endpoint concentration) influenced the anomaly score.
- Provides *confidence levels* (Low / Medium / High) for every detection.
- Suggests *automated, risk-ranked mitigation strategies* (rate limiting, IP blocking, WAF challenges).
- Stores every incident as a structured JSON file for future audit or visualization.

This makes the AI not just *reactive*, but *advisory and interpretable* — a step toward **conscious cybersecurity systems**.

---

## 🏗️ Project Structure



AI-DDoS-Detection/
├── src/
│   ├── **init**.py
│   ├── tui.py                 # Real-time interactive CLI interface
│   ├── incident.py            # Generates explainable incident reports
│   ├── detector.py            # Composite scoring logic
│   ├── tailer.py              # File tailing (log streaming)
│   ├── window.py              # Sliding window traffic aggregation
│   ├── executor.py            # Mitigation command executor
├── tools/
│   └── simulate_log_writer.py # DDoS traffic simulator (attack generator)
├── config.yaml                # Model parameters and thresholds
├── requirements.txt           # Python dependencies
├── incidents/                 # Auto-generated incident reports (JSON)
├── tests/
│   └── sample_access.log      # Sample log file for demo
└── README.md

---

## ⚙️ Dependencies

All components are pure Python and run efficiently inside **WSL Ubuntu** or native Linux.

**Core Dependencies**
```bash
rich
pyyaml
asyncio
````

**Optional (for advanced demo/report export)**

```bash
reportlab
pandas
```

Install everything in one go:

```bash
pip install -r requirements.txt
```

---

## 🧪 Quick Setup Guide (WSL Compatible)

### 1️⃣ Clone & Setup Environment

```bash
git clone https://github.com/Mr-Infect/ddos-xai-poc.git
cd ddos-xai-poc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Start the Detection Engine (Terminal 1)

```bash
python3 -m src.tui --logfile tests/sample_access.log --window 30 --poll 0.5
```

### 3️⃣ Simulate a DDoS Attack (Terminal 2)

```bash
python3 tools/simulate_log_writer.py --log tests/sample_access.log --qps 400 --duration 30 --unique 80 --path /login
```

---

## 🛡️ Live Demo Flow

1. **Terminal 1:** Starts monitoring the log file for live traffic patterns.
2. **Terminal 2:** Simulates a sudden surge (DDoS attack).
3. **AI Engine:** Detects abnormality, explains contributing features, lists attacking IPs.
4. **Operator Prompt:** User can preview or run mitigation (e.g., block IPs).
5. **Incident Report:** Saved in `/incidents/` with detailed JSON data and recommendations.

---

## 📊 Sample Incident Output

```
─────────────────────────────────────────────
 ALERT • Score: 91.3 • Confidence: HIGH
─────────────────────────────────────────────
Time: 2025-11-01T15:47:52Z
Top Features: requests:412 | unique_ips:76
Explanation: requests contributed ~68%; unique_ips ~25%; path concentration ~7%
─────────────────────────────────────────────
Recommended Mitigations:
1. Rate-limit path /login (10r/s)
2. DROP top offenders: 192.168.0.23, 192.168.0.24
3. Enable WAF challenge for suspect path
─────────────────────────────────────────────
Operator action: Choose mitigation id to preview/run.
─────────────────────────────────────────────
```

Each report is also saved as a structured JSON file for forensic review.

---

## 🧩 Technical Highlights

* **Live Stream Processing:** Uses asynchronous file tailing for real-time log ingestion.
* **Statistical + Heuristic Scoring:** Composite model fusing request-rate anomalies and entropy deviation.
* **Explainable AI Narrative:** Feature attribution for every alert (similar to SHAP-style explanation).
* **Interactive CLI Interface:** Built with `Rich` for a visually compelling SOC simulation.
* **Offline Audit Trail:** JSON-based report storage for every detection event.
* **Human-in-the-loop Design:** Operator confirms AI-suggested mitigations.

---

## 🧱 Architectural Diagram (Conceptual)

```
 ┌─────────────────────────────────────────────┐
 │         AI-Driven DDoS Detection CLI        │
 ├─────────────────────────────────────────────┤
 │   Log Stream (Nginx, Access Logs, etc.)    │
 │                     │                      │
 │         Sliding Window Aggregator          │
 │                     │                      │
 │           Composite AI Scorer              │
 │        (Z-Score + Heuristic Model)         │
 │                     │                      │
 │         Explainable AI Engine (XAI)        │
 │    ↳ Feature Attribution + Confidence      │
 │                     │                      │
 │        Incident Generator & CLI UI         │
 │    ↳ Report, IPs, Mitigations, Commands    │
 │                     │                      │
 │             Operator Feedback              │
 └─────────────────────────────────────────────┘
```

---

## 🧠 Future Enhancements

* Integrate **Transformer-based traffic embeddings** for high-fidelity anomaly detection.
* Extend **explainability** with visual charts (via Streamlit).
* Add **auto-mitigation mode** with dynamic firewall rule updates.
* Deploy as a **microservice** in cloud-native SOC environments.

---

## 🏁 Conclusion

This project demonstrates the convergence of **cyber defense**, **AI analytics**, and **human interpretability**.
Unlike conventional IDS systems, this model:

* Detects attacks in real-time,
* Explains its reasoning transparently,
* Suggests feasible, ranked mitigation paths.

It’s a lightweight yet **forward-looking SOC automation prototype** — showing how **AI can defend, explain, and assist**.

---

