import simpy
import random
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =========================================================
# CAMPUS PARKING & EXIT CARPOOL COORDINATION
# Process-Oriented Simulation.py
# Based on Workshops 1, 2 and 3
# =========================================================

SIMULATION_TIME = 7

# =========================================================
# TICS (Days)
# =========================================================

TIC_NAMES = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun"
}

# =========================================================
# CAMPUS DATA
# =========================================================

MOTORCYCLE_DEMAND = {
    "Mon": (140, 180),
    "Tue": (150, 190),
    "Wed": (160, 200),
    "Thu": (160, 210),
    "Fri": (180, 240),
    "Sat": (60, 100),
    "Sun": (20, 50)
}

BASEMENT_CAPACITY = 110

MAX_EXTERNAL_OVERFLOW = 90

CARPOOL_REQUESTS = {
    "Mon": (40, 70),
    "Tue": (45, 75),
    "Wed": (50, 80),
    "Thu": (55, 85),
    "Fri": (70, 120),
    "Sat": (20, 40),
    "Sun": (5, 15)
}

# =========================================================
# SCENARIOS
# =========================================================

SCENARIOS = {
    "baseline": {
        "match_rate": 0.45,
        "sync_fail_rate": 0.15,
        "cancellation_rate": 0.10,
        "description": "Normal institutional operation"
    },
    "optimization": {
        "match_rate": 0.75,
        "sync_fail_rate": 0.03,
        "cancellation_rate": 0.04,
        "description": "Optimized architecture"
    },
    "failure": {
        "match_rate": 0.30,
        "sync_fail_rate": 0.40,
        "cancellation_rate": 0.25,
        "description": "Critical failures & desynchronization"
    }
}

RAIN_PROBABILITY = 0.35
RAIN_DEMAND_BOOST = 1.25

# =========================================================
# MAIN CLASS
# =========================================================

class CampusSimulation:

    def __init__(self, root):

        self.root = root
        self.root.title("Smart Campus Mobility Simulator")
        self.root.geometry("1450x850")
        self.root.configure(bg="#e8edf2")

        # =============================================
        # STYLE
        # =============================================

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Card.TFrame",
            background="white"
        )

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold"),
            background="#e8edf2",
            foreground="#1d3557"
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10),
            background="#e8edf2",
            foreground="#4f5d75"
        )

        style.configure(
            "Custom.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )

        # =============================================
        # METRICS
        # =============================================

        self.total_matches = 0
        self.failed_matches = 0
        self.total_overflow = 0
        self.total_sync_errors = 0
        self.total_cancellations = 0

        # Graph data
        self.tics_list = []
        self.daily_parking_demand = []
        self.daily_overflow = []
        self.daily_matches = []

        self.create_widgets()

    # =====================================================
    # UI
    # =====================================================

    def create_widgets(self):

        # =============================================
        # HEADER
        # =============================================

        header = tk.Frame(
            self.root,
            bg="#e8edf2"
        )
        header.pack(fill="x", pady=(10, 0))

        title = ttk.Label(
            header,
            text="Smart Campus Mobility Simulator",
            style="Title.TLabel"
        )
        title.pack()

        subtitle = ttk.Label(
            header,
            text="Parking saturation and exit carpool coordination",
            style="Subtitle.TLabel"
        )
        subtitle.pack(pady=(0, 10))

        # =============================================
        # TOP PANEL
        # =============================================

        top_panel = tk.Frame(
            self.root,
            bg="#e8edf2"
        )
        top_panel.pack(fill="x", padx=15)

        # =============================================
        # CONTROL CARD
        # =============================================

        control_card = tk.Frame(
            top_panel,
            bg="white",
            bd=0,
            relief="flat"
        )
        control_card.pack(side="left", fill="x", expand=True)

        tk.Label(
            control_card,
            text="Simulation Scenario",
            bg="white",
            fg="#1d3557",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.scenario_var = tk.StringVar(value="optimization")

        scenario_combo = ttk.Combobox(
            control_card,
            textvariable=self.scenario_var,
            values=["baseline", "optimization", "failure"],
            width=25,
            state="readonly"
        )
        scenario_combo.pack(anchor="w", padx=15, pady=5)

        run_button = ttk.Button(
            control_card,
            text="Run Simulation",
            style="Custom.TButton",
            command=self.run_simulation
        )
        run_button.pack(anchor="w", padx=15, pady=(10, 15))

        # =============================================
        # STATS CARD
        # =============================================

        self.stats_card = tk.Frame(
            top_panel,
            bg="#1d3557",
            width=300
        )
        self.stats_card.pack(side="right", padx=(15, 0), fill="y")

        tk.Label(
            self.stats_card,
            text="System Overview",
            bg="#1d3557",
            fg="white",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        self.stats_label = tk.Label(
            self.stats_card,
            text="Press 'Run Simulation' to begin.",
            justify="left",
            bg="#1d3557",
            fg="white",
            font=("Consolas", 9)
        )
        self.stats_label.pack(anchor="w", padx=15, pady=(0, 15))

        # =============================================
        # MAIN CONTENT
        # =============================================

        content = tk.Frame(
            self.root,
            bg="#e8edf2"
        )
        content.pack(fill="both", expand=True, padx=15, pady=15)

        # =============================================
        # LOG PANEL
        # =============================================

        log_container = tk.Frame(
            content,
            bg="white"
        )
        log_container.pack(side="left", fill="both", expand=True)

        tk.Label(
            log_container,
            text="Simulation Activity Log",
            bg="white",
            fg="#1d3557",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(12, 8))

        self.log_text = tk.Text(
            log_container,
            height=20,
            bg="#f7f9fb",
            fg="#222222",
            relief="flat",
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # =============================================
        # GRAPH PANEL
        # =============================================

        graph_container = tk.Frame(
            content,
            bg="white",
            width=500
        )
        graph_container.pack(side="right", fill="both", padx=(15, 0))

        tk.Label(
            graph_container,
            text="System Metrics",
            bg="white",
            fg="#1d3557",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(12, 8))

        self.graph_area = tk.Frame(
            graph_container,
            bg="white"
        )
        self.graph_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # =====================================================
    # LOG
    # =====================================================

    def add_log(self, message):

        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    # =====================================================
    # CARPOOL PROCESS
    # =====================================================

    def process_carpool(self, env, request_id, match_rate):

        yield env.timeout(random.uniform(0.2, 1.0))

        matched = random.random() < match_rate

        if matched:
            self.total_matches += 1
            self.add_log(f"[MATCH] Request {request_id} connected")
        else:
            self.failed_matches += 1
            self.add_log(f"[FAILED] Request {request_id} no route found")

    # =====================================================
    # MAIN SYSTEM PROCESS
    # =====================================================

    def campus_generator(self, env):

        while True:

            tic_index = int(env.now) % 7
            tic_name = TIC_NAMES[tic_index]

            scenario_name = self.scenario_var.get()
            scenario = SCENARIOS[scenario_name]

            min_demand, max_demand = MOTORCYCLE_DEMAND[tic_name]
            parking_demand = random.randint(min_demand, max_demand)

            raining = False

            if random.random() < RAIN_PROBABILITY:
                raining = True
                parking_demand = int(parking_demand * RAIN_DEMAND_BOOST)

            overflow = max(0, parking_demand - BASEMENT_CAPACITY)
            overflow = min(overflow, MAX_EXTERNAL_OVERFLOW)

            self.total_overflow += overflow

            sync_issue = random.random() < scenario["sync_fail_rate"]

            if sync_issue:
                self.total_sync_errors += 1

            min_requests, max_requests = CARPOOL_REQUESTS[tic_name]
            requests = random.randint(min_requests, max_requests)

            cancellations = 0

            for _ in range(requests):
                if random.random() < scenario["cancellation_rate"]:
                    cancellations += 1

            self.total_cancellations += cancellations

            # =========================================
            # LOG
            # =========================================

            self.add_log("")
            self.add_log(f"===== {tic_name} =====")

            if raining:
                self.add_log("Weather: Rain detected")
            else:
                self.add_log("Weather: Normal")

            self.add_log(f"Parking demand: {parking_demand}")
            self.add_log(f"Overflow vehicles: {overflow}")

            if sync_issue:
                self.add_log("Synchronization issue detected")

            self.add_log(f"Carpool requests: {requests}")
            self.add_log(f"Cancellations: {cancellations}")

            previous_matches = self.total_matches

            for i in range(requests):
                env.process(
                    self.process_carpool(env, i, scenario["match_rate"])
                )

            yield env.timeout(1)

            daily_matches = self.total_matches - previous_matches
            self.add_log(f"Successful matches: {daily_matches}")

            self.tics_list.append(tic_name)
            self.daily_parking_demand.append(parking_demand)
            self.daily_overflow.append(overflow)
            self.daily_matches.append(daily_matches)

    # =====================================================
    # GRAPHS
    # =====================================================

    def show_graphs(self):

        # Limpiar gráficas anteriores
        for widget in self.graph_area.winfo_children():
            widget.destroy()

        # =====================================================
        # FIGURE CONFIG
        # =====================================================

        fig = plt.Figure(figsize=(5.2, 7.2), dpi=100)

        gs = fig.add_gridspec(3, 1, hspace=0.55)

        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])

        # =====================================================
        # GRAPH 1 - PARKING DEMAND
        # =====================================================

        ax1.bar(self.tics_list, self.daily_parking_demand)
        ax1.axhline(y=BASEMENT_CAPACITY, linestyle='--')
        ax1.set_title("Parking Demand", fontsize=10, pad=10)
        ax1.set_ylabel("Motorcycles", fontsize=8)
        ax1.tick_params(axis='x', labelsize=8)
        ax1.tick_params(axis='y', labelsize=8)

        # =====================================================
        # GRAPH 2 - OVERFLOW
        # =====================================================

        ax2.plot(self.tics_list, self.daily_overflow, marker='o', linewidth=2)
        ax2.set_title("Overflow", fontsize=10, pad=10)
        ax2.set_ylabel("Vehicles", fontsize=8)
        ax2.tick_params(axis='x', labelsize=8)
        ax2.tick_params(axis='y', labelsize=8)

        # =====================================================
        # GRAPH 3 - CARPOOL MATCHES
        # =====================================================

        ax3.bar(self.tics_list, self.daily_matches)
        ax3.set_title("Carpool Matches", fontsize=10, pad=10)
        ax3.set_ylabel("Matches", fontsize=8)
        ax3.tick_params(axis='x', labelsize=8)
        ax3.tick_params(axis='y', labelsize=8)

        # =====================================================
        # CANVAS
        # =====================================================

        canvas = FigureCanvasTkAgg(fig, master=self.graph_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    # =====================================================
    # RUN
    # =====================================================

    def run_simulation(self):

        self.total_matches = 0
        self.failed_matches = 0
        self.total_overflow = 0
        self.total_sync_errors = 0
        self.total_cancellations = 0

        self.tics_list.clear()
        self.daily_parking_demand.clear()
        self.daily_overflow.clear()
        self.daily_matches.clear()

        self.log_text.delete(1.0, tk.END)

        scenario = self.scenario_var.get()

        self.add_log("SMART CAMPUS MOBILITY SIMULATION")
        self.add_log("--------------------------------")
        self.add_log(f"Scenario: {scenario.upper()}")

        env = simpy.Environment()
        env.process(self.campus_generator(env))
        env.run(until=SIMULATION_TIME)

        self.add_log("")
        self.add_log("===== FINAL RESULTS =====")
        self.add_log(f"Total matches: {self.total_matches}")
        self.add_log(f"Failed matches: {self.failed_matches}")
        self.add_log(f"Overflow vehicles: {self.total_overflow}")
        self.add_log(f"Sync failures: {self.total_sync_errors}")
        self.add_log(f"Driver cancellations: {self.total_cancellations}")

        # =========================================
        # UPDATE STATS PANEL
        # =========================================

        self.stats_label.config(
            text=(
                f"Scenario: {scenario.upper()}\n\n"
                f"Successful Matches: {self.total_matches}\n"
                f"Failed Matches: {self.failed_matches}\n"
                f"Overflow Vehicles: {self.total_overflow}\n"
                f"Sync Failures: {self.total_sync_errors}\n"
                f"Cancellations: {self.total_cancellations}"
            )
        )

        self.show_graphs()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CampusSimulation(root)
    root.mainloop()
