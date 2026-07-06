from flask import Flask, render_template, request, Response
from scheduler import (
    Process,
    fcfs,
    sjf,
    srtf,
    round_robin,
    priority_scheduling,
    priority_non_preemptive,
    priority_preemptive,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
last_gantt = None


@app.route("/", methods=["GET", "POST"])
def index():
    global last_gantt
    results = None
    message = None
    submitted_processes = []
    selected_algorithm = request.form.get("algorithm", "FCFS") if request.method == "POST" else "FCFS"
    selected_quantum = request.form.get("quantum", "2") if request.method == "POST" else "2"
    selected_priority_order = request.form.get("priority_order", "low_to_high") if request.method == "POST" else "low_to_high"

    if request.method == "POST":
        processes = []
        raw_processes = request.form.get("processes", "")
        pids = request.form.getlist("pid[]")
        arrivals = request.form.getlist("arrival[]")
        bursts = request.form.getlist("burst[]")
        priorities = request.form.getlist("priority[]")

        if pids or arrivals or bursts or priorities:
            row_count = max(len(pids), len(arrivals), len(bursts), len(priorities), 0)

            for index in range(row_count):
                pid = pids[index].strip() if index < len(pids) else ""
                arrival_text = arrivals[index].strip() if index < len(arrivals) else ""
                burst_text = bursts[index].strip() if index < len(bursts) else ""
                priority_text = priorities[index].strip() if index < len(priorities) else ""

                if not any([pid, arrival_text, burst_text, priority_text]):
                    continue

                submitted_processes.append({
                    "pid": pid,
                    "arrival": arrival_text,
                    "burst": burst_text,
                    "priority": priority_text,
                })

                try:
                    arrival = int(arrival_text)
                    burst = int(burst_text)
                    priority = int(priority_text) if priority_text else 0
                except ValueError as exc:
                    message = f"Please enter valid numbers for arrival, burst, and priority. {exc}"
                    break

                processes.append(Process(pid, arrival, burst, priority))
        elif raw_processes:
            for line in raw_processes.splitlines():
                line = line.strip()
                if not line:
                    continue

                parts = [part.strip() for part in line.split(",")]
                if len(parts) < 3:
                    message = "Each process must follow PID, Arrival, Burst (and optional Priority)."
                    break

                try:
                    pid = parts[0]
                    arrival = int(parts[1])
                    burst = int(parts[2])
                    priority_value = parts[3].strip() if len(parts) > 3 else ""
                    priority = int(priority_value) if priority_value else 0
                except ValueError as exc:
                    message = f"Please enter valid numbers for arrival, burst, and priority. {exc}"
                    break

                submitted_processes.append({
                    "pid": pid,
                    "arrival": str(arrival),
                    "burst": str(burst),
                    "priority": str(priority),
                })
                processes.append(Process(pid, arrival, burst, priority))

        algo = request.form.get("algorithm", "FCFS")
        priority_order = request.form.get("priority_order", "low_to_high")
        try:
            quantum = int(request.form.get("quantum") or 2)
        except ValueError:
            quantum = 2

        if not message and not processes:
            message = "Please enter at least one process."
        elif not message:
            if algo == "FCFS":
                gantt = fcfs(processes)
            elif algo == "SJF":
                gantt = sjf(processes)
            elif algo == "SRTF":
                gantt = srtf(processes)
            elif algo == "Round Robin":
                gantt = round_robin(processes, quantum)
            elif algo == "Priority (Preemptive)":
                gantt = priority_preemptive(processes, priority_order)
            elif algo in ("Priority", "Priority (Non-Preemptive)"):
                gantt = priority_non_preemptive(processes, priority_order)
            else:
                gantt = priority_scheduling(processes, priority_order)

            avg_wait = sum(p.waiting for p in processes) / len(processes)
            avg_turn = sum(p.turnaround for p in processes) / len(processes)

            results = {
                "gantt": gantt,
                "avg_wait": avg_wait,
                "avg_turn": avg_turn,
                "table": processes,
            }
            last_gantt = gantt

    return render_template(
        "index.html",
        results=results,
        message=message,
        submitted_processes=submitted_processes,
        selected_algorithm=selected_algorithm,
        selected_quantum=selected_quantum,
        selected_priority_order=selected_priority_order,
    )


@app.route("/gantt.png")
def gantt_chart():
    global last_gantt
    if not last_gantt:
        return Response("No chart available", mimetype="text/plain")

    fig, ax = plt.subplots(figsize=(8, 3))
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6", "#f1c40f", "#95a5a6"]

    chart_intervals = []
    sorted_intervals = sorted(last_gantt, key=lambda item: item[1])
    current_time = 0
    for pid, start, end in sorted_intervals:
        if start > current_time:
            chart_intervals.append(("Idle", current_time, start))
        chart_intervals.append((pid, start, end))
        current_time = max(current_time, end)

    for i, (pid, start, end) in enumerate(chart_intervals):
        color = colors[i % len(colors)] if pid != "Idle" else "#d0d7de"
        ax.barh(0, end - start, left=start, color=color, edgecolor="black")
        if pid != "Idle":
            ax.text((start + end) / 2, 0, pid, ha="center", va="center", color="white", fontsize=10)

    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title("Gantt Chart")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return Response(buf.getvalue(), mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)