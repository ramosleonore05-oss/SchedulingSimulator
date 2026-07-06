class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.completion = 0
        self.waiting = 0
        self.turnaround = 0

def fcfs(processes):
    time = 0
    gantt = []
    for p in sorted(processes, key=lambda x: x.arrival):
        if time < p.arrival:
            time = p.arrival
        start = time
        time += p.burst
        p.completion = time
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst
        gantt.append((p.pid, start, time))
    return gantt

def sjf(processes):
    time = 0
    gantt = []
    ready = []
    processes = sorted(processes, key=lambda x: x.arrival)
    while processes or ready:
        while processes and processes[0].arrival <= time:
            ready.append(processes.pop(0))
        if ready:
            ready.sort(key=lambda x: x.burst)
            p = ready.pop(0)
            start = time
            time += p.burst
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            gantt.append((p.pid, start, time))
        else:
            time += 1
    return gantt

def srtf(processes):
    time = 0
    gantt = []
    processes = sorted(processes, key=lambda x: x.arrival)
    ready = []
    last_pid = None
    while processes or ready:
        while processes and processes[0].arrival <= time:
            ready.append(processes.pop(0))
        if ready:
            ready.sort(key=lambda x: x.remaining)
            p = ready[0]
            if last_pid != p.pid:
                gantt.append((p.pid, time, time+1))
            else:
                gantt[-1] = (p.pid, gantt[-1][1], time+1)
            p.remaining -= 1
            time += 1
            last_pid = p.pid
            if p.remaining == 0:
                ready.remove(p)
                p.completion = time
                p.turnaround = p.completion - p.arrival
                p.waiting = p.turnaround - p.burst
        else:
            time += 1
            last_pid = None
    return gantt

def round_robin(processes, quantum=2):
    time = 0
    gantt = []
    queue = sorted(processes, key=lambda x: x.arrival)
    while queue:
        p = queue.pop(0)
        if time < p.arrival:
            time = p.arrival
        start = time
        run = min(quantum, p.remaining)
        time += run
        p.remaining -= run
        gantt.append((p.pid, start, time))
        if p.remaining > 0:
            queue.append(p)
        else:
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
    return gantt


def priority_non_preemptive(processes, priority_order="low_to_high"):
    time = 0
    gantt = []
    ready = []
    processes = sorted(processes, key=lambda x: x.arrival)
    while processes or ready:
        while processes and processes[0].arrival <= time:
            ready.append(processes.pop(0))
        if ready:
            if priority_order == "high_to_low":
                ready.sort(key=lambda x: x.priority, reverse=True)
            else:
                ready.sort(key=lambda x: x.priority)
            p = ready.pop(0)
            start = time
            time += p.burst
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            gantt.append((p.pid, start, time))
        else:
            time += 1
    return gantt


def priority_preemptive(processes, priority_order="low_to_high"):
    time = 0
    gantt = []
    ready = []
    processes = sorted(processes, key=lambda x: x.arrival)
    last_pid = None

    while processes or ready:
        while processes and processes[0].arrival <= time:
            ready.append(processes.pop(0))

        if ready:
            if priority_order == "high_to_low":
                ready.sort(key=lambda x: (x.priority, x.arrival), reverse=True)
            else:
                ready.sort(key=lambda x: (x.priority, x.arrival))
            p = ready[0]

            if last_pid != p.pid:
                gantt.append((p.pid, time, time + 1))
            else:
                gantt[-1] = (p.pid, gantt[-1][1], time + 1)

            p.remaining -= 1
            time += 1
            last_pid = p.pid

            if p.remaining == 0:
                ready.remove(p)
                p.completion = time
                p.turnaround = p.completion - p.arrival
                p.waiting = p.turnaround - p.burst
        else:
            time += 1
            last_pid = None

    return gantt


def priority_scheduling(processes, priority_order="low_to_high"):
    return priority_non_preemptive(processes, priority_order)
