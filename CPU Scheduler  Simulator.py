import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Process class to store process details
class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst  # For Round Robin

# Main GUI Application
class CPUSchedulerSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent CPU Scheduler Simulator")
        self.root.geometry("1000x700")

        self.processes = []
        self.pid_counter = 1

        # Input Frame
        input_frame = ttk.LabelFrame(root, text="Input Processes")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Arrival Time:").grid(row=0, column=0, padx=5, pady=5)
        self.arrival_entry = ttk.Entry(input_frame)
        self.arrival_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Burst Time:").grid(row=0, column=2, padx=5, pady=5)
        self.burst_entry = ttk.Entry(input_frame)
        self.burst_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Priority (for Priority Scheduling):").grid(row=0, column=4, padx=5, pady=5)
        self.priority_entry = ttk.Entry(input_frame)
        self.priority_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(input_frame, text="Add Process", command=self.add_process).grid(row=0, column=6, padx=5, pady=5)

        # Process List Display
        self.process_text = tk.Text(root, height=5, width=80)
        self.process_text.pack(padx=10, pady=5)

        # Algorithm Selection
        algo_frame = ttk.LabelFrame(root, text="Scheduling Algorithm")
        algo_frame.pack(padx=10, pady=10, fill="x")

        self.algorithm = tk.StringVar(value="FCFS")
        algorithms = [("FCFS", "FCFS"), ("SJF", "SJF"), ("Round Robin", "RR"), ("Priority", "Priority")]
        for i, (text, value) in enumerate(algorithms):
            ttk.Radiobutton(algo_frame, text=text, variable=self.algorithm, value=value).grid(row=0, column=i, padx=5)

        ttk.Label(algo_frame, text="Quantum (for RR):").grid(row=0, column=4, padx=5)
        self.quantum_entry = ttk.Entry(algo_frame, width=5)
        self.quantum_entry.grid(row=0, column=5, padx=5)
        self.quantum_entry.insert(0, "2")

        # Buttons
        ttk.Button(root, text="Simulate", command=self.simulate).pack(pady=5)
        ttk.Button(root, text="Reset", command=self.reset).pack(pady=5)

        # Output Frame
        self.output_frame = ttk.LabelFrame(root, text="Results")
        self.output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.result_text = tk.Text(self.output_frame, height=3, width=80)
        self.result_text.pack(padx=5, pady=5)

        # Matplotlib Figure for Gantt Chart
        self.fig, self.ax = plt.subplots(figsize=(8, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.output_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def add_process(self):
        try:
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get() or 0)
            if arrival < 0 or burst <= 0:
                raise ValueError("Invalid input")
            process = Process(f"P{self.pid_counter}", arrival, burst, priority)
            self.processes.append(process)
            self.pid_counter += 1
            self.update_process_display()
            self.clear_entries()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")

    def update_process_display(self):
        self.process_text.delete(1.0, tk.END)
        for p in self.processes:
            self.process_text.insert(tk.END, f"{p.pid}: Arrival={p.arrival}, Burst={p.burst}, Priority={p.priority}\n")

    def clear_entries(self):
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)

    def simulate(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes added!")
            return

        algo = self.algorithm.get()
        if algo == "RR":
            try:
                quantum = int(self.quantum_entry.get())
                if quantum <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid quantum value")
                return
        else:
            quantum = None

        gantt, avg_wait, avg_turnaround = self.run_algorithm(algo, quantum)
        self.display_results(gantt, avg_wait, avg_turnaround)

    def run_algorithm(self, algo, quantum):
        processes = sorted(self.processes, key=lambda x: x.arrival)
        gantt = []
        current_time = 0
        completed = []
        waiting_time = {p.pid: 0 for p in processes}
        turnaround_time = {p.pid: 0 for p in processes}

        if algo == "FCFS":
            for p in processes:
                if current_time < p.arrival:
                    current_time = p.arrival
                gantt.append((p.pid, current_time, current_time + p.burst))
                current_time += p.burst
                turnaround_time[p.pid] = current_time - p.arrival
                waiting_time[p.pid] = turnaround_time[p.pid] - p.burst
                completed.append(p)

        elif algo == "SJF":
            remaining = processes.copy()
            while remaining:
                available = [p for p in remaining if p.arrival <= current_time]
                if not available:
                    current_time += 1
                    continue
                shortest = min(available, key=lambda x: x.burst)
                gantt.append((shortest.pid, current_time, current_time + shortest.burst))
                current_time += shortest.burst
                turnaround_time[shortest.pid] = current_time - shortest.arrival
                waiting_time[shortest.pid] = turnaround_time[shortest.pid] - shortest.burst
                remaining.remove(shortest)
                completed.append(shortest)

        elif algo == "RR":
            queue = processes.copy()
            while queue:
                p = queue.pop(0)
                if current_time < p.arrival:
                    current_time = p.arrival
                exec_time = min(quantum, p.remaining)
                gantt.append((p.pid, current_time, current_time + exec_time))
                current_time += exec_time
                p.remaining -= exec_time
                if p.remaining > 0:
                    queue.append(p)
                else:
                    turnaround_time[p.pid] = current_time - p.arrival
                    waiting_time[p.pid] = turnaround_time[p.pid] - p.burst
                    completed.append(p)

        elif algo == "Priority":
            remaining = processes.copy()
            while remaining:
                available = [p for p in remaining if p.arrival <= current_time]
                if not available:
                    current_time += 1
                    continue
                highest = min(available, key=lambda x: x.priority)  # Lower priority value = higher priority
                gantt.append((highest.pid, current_time, current_time + highest.burst))
                current_time += highest.burst
                turnaround_time[highest.pid] = current_time - highest.arrival
                waiting_time[highest.pid] = turnaround_time[highest.pid] - highest.burst
                remaining.remove(highest)
                completed.append(highest)

        avg_wait = sum(waiting_time.values()) / len(processes)
        avg_turnaround = sum(turnaround_time.values()) / len(processes)
        return gantt, avg_wait, avg_turnaround

    def display_results(self, gantt, avg_wait, avg_turnaround):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Average Waiting Time: {avg_wait:.2f}\n")
        self.result_text.insert(tk.END, f"Average Turnaround Time: {avg_turnaround:.2f}\n")

        self.ax.clear()
        for i, (pid, start, end) in enumerate(gantt):
            self.ax.barh(0, end - start, left=start, height=0.5, align='center', label=pid)
            self.ax.text((start + end) / 2, 0, pid, ha='center', va='center', color='white')
        self.ax.set_xlabel("Time")
        self.ax.set_yticks([])
        self.ax.set_title("Gantt Chart")
        self.canvas.draw()

    def reset(self):
        self.processes.clear()
        self.pid_counter = 1
        self.process_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.ax.clear()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerSimulator(root)
    root.mainloop()
