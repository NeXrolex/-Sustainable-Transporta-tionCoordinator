import simpy
import random
import matplotlib.pyplot as plt
import tkinter as tk

from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =========================================================
# CAMPUS PARKING & EXIT CARPOOL COORDINATOR
# Behavior-Oriented Simulation
# Workshop 4
# =========================================================

SIMULATION_TIME = 60

# =========================================================
# POPULATION
# =========================================================

TOTAL_STUDENTS = 500

INITIAL_ADOPTION = 30
INITIAL_TRUST = 50

DRIVER_RATIO = 0.15

AVERAGE_CAPACITY = 3

BASEMENT_CAPACITY = 110

MAX_OVERFLOW = 90

# =========================================================
# WEEK DAYS
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
# DEMAND
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

# =========================================================
# SCENARIOS
# =========================================================

SCENARIOS = {

    "baseline": {

        "sync_fail_rate": 0.10,
        "cancel_rate": 0.12,
        "adoption_bonus": 0.0,
        "description": "Normal operation"
    },

    "optimization": {

        "sync_fail_rate": 0.03,
        "cancel_rate": 0.05,
        "adoption_bonus": 0.1,
        "description": "Priority parking incentive"
    },

    "failure": {

        "sync_fail_rate": 0.35,
        "cancel_rate": 0.25,
        "adoption_bonus": -0.3,
        "description": "Critical failures"
    }
}

# =========================================================
# MAIN CLASS
# =========================================================

class BehaviorCampusSimulation:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Smart Campus Mobility Simulator - Behavior Model"
        )

        self.root.geometry("1450x850")

        self.root.configure(
            bg="#e8edf2"
        )

        # =============================================
        # STYLE
        # =============================================

        style = ttk.Style()

        style.theme_use("clam")

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
        # SYSTEM STATE
        # =============================================

        self.adoption = INITIAL_ADOPTION

        self.trust = INITIAL_TRUST

        self.whatsapp_usage = 100 - INITIAL_ADOPTION

        self.total_matches = 0

        self.total_cancellations = 0

        self.total_sync_failures = 0

        self.total_overflow = 0

        # =============================================
        # GRAPH DATA
        # =============================================

        self.days = []

        self.saturation_history = []

        self.adoption_history = []

        self.trust_history = []

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

        header.pack(
            fill="x",
            pady=(10, 0)
        )

        title = ttk.Label(
            header,
            text="Smart Campus Mobility Simulator",
            style="Title.TLabel"
        )

        title.pack()

        subtitle = ttk.Label(
            header,
            text="Behavior-Oriented Simulation",
            style="Subtitle.TLabel"
        )

        subtitle.pack(
            pady=(0, 10)
        )

        # =============================================
        # TOP PANEL
        # =============================================

        top_panel = tk.Frame(
            self.root,
            bg="#e8edf2"
        )

        top_panel.pack(
            fill="x",
            padx=15
        )

        # =============================================
        # CONTROL CARD
        # =============================================

        control_card = tk.Frame(
            top_panel,
            bg="white"
        )

        control_card.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            control_card,
            text="Simulation Scenario",
            bg="white",
            fg="#1d3557",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        self.scenario_var = tk.StringVar(
            value="optimization"
        )

        scenario_combo = ttk.Combobox(
            control_card,
            textvariable=self.scenario_var,
            values=[
                "baseline",
                "optimization",
                "failure"
            ],
            width=25,
            state="readonly"
        )

        scenario_combo.pack(
            anchor="w",
            padx=15,
            pady=5
        )

        run_button = ttk.Button(
            control_card,
            text="Run Simulation",
            style="Custom.TButton",
            command=self.run_simulation
        )

        run_button.pack(
            anchor="w",
            padx=15,
            pady=(10, 15)
        )

        # =============================================
        # STATS CARD
        # =============================================

        self.stats_card = tk.Frame(
            top_panel,
            bg="#1d3557",
            width=300
        )

        self.stats_card.pack(
            side="right",
            padx=(15, 0),
            fill="y"
        )

        tk.Label(
            self.stats_card,
            text="System Overview",
            bg="#1d3557",
            fg="white",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.stats_label = tk.Label(
            self.stats_card,
            text="Press 'Run Simulation' to begin.",
            justify="left",
            bg="#1d3557",
            fg="white",
            font=("Consolas", 9)
        )

        self.stats_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

        # =============================================
        # MAIN CONTENT
        # =============================================

        content = tk.Frame(
            self.root,
            bg="#e8edf2"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # =============================================
        # LOG PANEL
        # =============================================

        log_container = tk.Frame(
            content,
            bg="white"
        )

        log_container.pack(
            side="left",
            fill="both",
            expand=True
        )

        tk.Label(
            log_container,
            text="Simulation Activity Log",
            bg="white",
            fg="#1d3557",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 8)
        )

        self.log_text = tk.Text(
            log_container,
            height=20,
            bg="#f7f9fb",
            fg="#222222",
            relief="flat",
            font=("Consolas", 9),
            wrap=tk.WORD
        )

        self.log_text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # =============================================
        # GRAPH PANEL
        # =============================================

        graph_container = tk.Frame(
            content,
            bg="white",
            width=500
        )

        graph_container.pack(
            side="right",
            fill="both",
            padx=(15, 0)
        )

        tk.Label(
            graph_container,
            text="System Metrics",
            bg="white",
            fg="#1d3557",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 8)
        )

        self.graph_area = tk.Frame(
            graph_container,
            bg="white"
        )

        self.graph_area.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

    # =====================================================
    # LOG
    # =====================================================

    def add_log(self, message):

        self.log_text.insert(
            tk.END,
            message + "\n"
        )

        self.log_text.see(
            tk.END
        )

        self.root.update()

    # =====================================================
    # MAIN BEHAVIOR MODEL
    # =====================================================

    def campus_behavior_generator(self, env):

        while True:

            day_number = int(env.now) + 1

            tic_name = TIC_NAMES[
                int(env.now) % 7
            ]

            scenario_name = self.scenario_var.get()

            scenario = SCENARIOS[
                scenario_name
            ]

            # =========================================
            # CURRENT USERS
            # =========================================

            app_users = int(
                TOTAL_STUDENTS *
                (self.adoption / 100)
            )

            whatsapp_users = (
                TOTAL_STUDENTS -
                app_users
            )

            # =========================================
            # DRIVERS
            # =========================================

            drivers = int(
                app_users *
                DRIVER_RATIO
            )

            available_seats = (
                drivers *
                AVERAGE_CAPACITY
            )

            # =========================================
            # PARKING DEMAND
            # =========================================

            min_demand, max_demand = MOTORCYCLE_DEMAND[
                tic_name
            ]

            parking_demand = random.randint(
                min_demand,
                max_demand
            )

            # =========================================
            # CARPOOL EFFECT
            # =========================================

            reduced_motorcycles = int(
                available_seats * 0.45
            )

            parking_demand = max(
                0,
                parking_demand -
                reduced_motorcycles
            )

            overflow = max(
                0,
                parking_demand -
                BASEMENT_CAPACITY
            )

            overflow = min(
                overflow,
                MAX_OVERFLOW
            )

            self.total_overflow += overflow

            saturation = min(
                100,
                (parking_demand /
                 BASEMENT_CAPACITY) * 100
            )

            # =========================================
            # MATCH GENERATION
            # =========================================

            passengers_needed = max(
                0,
                app_users - drivers
            )

            possible_matches = min(
                available_seats,
                passengers_needed
            )

            match_rate = (
                self.trust / 100
            )

            successful_matches = int(
                possible_matches *
                match_rate *
                random.uniform(
                    0.80,
                    1.00
                )
            )

            self.total_matches += (
                successful_matches
            )

            # =========================================
            # CANCELLATIONS
            # =========================================

            cancellations = int(
                successful_matches *
                scenario["cancel_rate"]
            )

            self.total_cancellations += (
                cancellations
            )

            # =========================================
            # SYNCHRONIZATION FAILURE
            # =========================================

            sync_failure = (
                random.random()
                <
                scenario[
                    "sync_fail_rate"
                ]
            )

            if sync_failure:

                self.total_sync_failures += 1

            # =========================================
            # FEEDBACK LOOP 1
            # PARKING SATURATION
            # =========================================

            if saturation > 90:

                self.adoption += random.uniform(
                    0.05,
                    0.25
                )

            elif saturation < 60:

                self.adoption -= random.uniform(
                    0.1,
                    0.4
                )

            # =========================================
            # FEEDBACK LOOP 2
            # SUCCESSFUL MATCHES
            # =========================================

            trust_gain = (
                successful_matches
                * 0.015
            )

            self.trust += trust_gain

            # =========================================
            # FEEDBACK LOOP 3
            # CANCELLATIONS
            # =========================================

            trust_loss = (
                cancellations
                * 0.25
            )

            self.trust -= trust_loss

            # =========================================
            # FEEDBACK LOOP 4
            # DESYNCHRONIZATION
            # =========================================

            if sync_failure:

                self.trust -= random.uniform(
                    1,
                    3
                )

            # =========================================
            # INCENTIVE PROGRAM
            # =========================================

            self.adoption += (
                scenario[
                    "adoption_bonus"
                ]
            )

            # =========================================
            # BOUNDARIES
            # =========================================

            self.trust = max(
                0,
                min(
                    100,
                    self.trust
                )
            )

            self.adoption = max(
                15,
                min(
                    40,
                    self.adoption
                )
            )

            # =========================================
            # WHATSAPP USAGE
            # =========================================

            self.whatsapp_usage = max(
                0,
                100 -
                self.adoption
            )

            # =========================================
            # STORE HISTORY
            # =========================================

            self.days.append(
                day_number
            )

            self.saturation_history.append(
                saturation
            )

            self.adoption_history.append(
                self.adoption
            )

            self.trust_history.append(
                self.trust
            )

            # =========================================
            # LOG
            # =========================================

            self.add_log("")

            self.add_log(
                f"===== DAY {day_number} ({tic_name}) ====="
            )

            self.add_log(
                f"Parking Saturation: "
                f"{saturation:.1f}%"
            )

            self.add_log(
                f"Overflow Vehicles: "
                f"{overflow}"
            )

            self.add_log(
                f"App Adoption: "
                f"{self.adoption:.1f}%"
            )

            self.add_log(
                f"Trust Score: "
                f"{self.trust:.1f}%"
            )

            self.add_log(
                f"WhatsApp Usage: "
                f"{self.whatsapp_usage:.1f}%"
            )

            self.add_log(
                f"Drivers Available: "
                f"{drivers}"
            )

            self.add_log(
                f"Successful Matches: "
                f"{successful_matches}"
            )

            self.add_log(
                f"Cancellations: "
                f"{cancellations}"
            )

            if sync_failure:

                self.add_log(
                    "Synchronization Failure Detected"
                )

            else:

                self.add_log(
                    "Synchronization Status: OK"
                )

            yield env.timeout(1)

            # =====================================================
    # GRAPHS
    # =====================================================

    def show_graphs(self):

        for widget in self.graph_area.winfo_children():
            widget.destroy()

        fig = plt.Figure(
            figsize=(5.2, 7.2),
            dpi=100
        )

        gs = fig.add_gridspec(
            3,
            1,
            hspace=0.55
        )

        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])

        # =========================================
        # GRAPH 1
        # PARKING SATURATION
        # =========================================

        ax1.plot(
            self.days,
            self.saturation_history,
            marker="o",
            linewidth=2
        )

        ax1.set_title(
            "Parking Saturation %",
            fontsize=10,
            pad=10
        )

        ax1.set_ylabel(
            "%",
            fontsize=8
        )

        ax1.tick_params(
            axis='x',
            labelsize=8
        )

        ax1.tick_params(
            axis='y',
            labelsize=8
        )

        # =========================================
        # GRAPH 2
        # APP ADOPTION
        # =========================================

        ax2.plot(
            self.days,
            self.adoption_history,
            marker="o",
            linewidth=2
        )

        ax2.set_title(
            "Platform Adoption %",
            fontsize=10,
            pad=10
        )

        ax2.set_ylabel(
            "%",
            fontsize=8
        )

        ax2.tick_params(
            axis='x',
            labelsize=8
        )

        ax2.tick_params(
            axis='y',
            labelsize=8
        )

        # =========================================
        # GRAPH 3
        # TRUST
        # =========================================

        ax3.plot(
            self.days,
            self.trust_history,
            marker="o",
            linewidth=2
        )

        ax3.set_title(
            "Trust Score %",
            fontsize=10,
            pad=10
        )

        ax3.set_ylabel(
            "%",
            fontsize=8
        )

        ax3.tick_params(
            axis='x',
            labelsize=8
        )

        ax3.tick_params(
            axis='y',
            labelsize=8
        )

        canvas = FigureCanvasTkAgg(
            fig,
            master=self.graph_area
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            pady=10
        )

    # =====================================================
    # RUN
    # =====================================================

    def run_simulation(self):

        self.adoption = INITIAL_ADOPTION

        self.trust = INITIAL_TRUST

        self.whatsapp_usage = (
            100 - INITIAL_ADOPTION
        )

        self.total_matches = 0

        self.total_cancellations = 0

        self.total_sync_failures = 0

        self.total_overflow = 0

        self.days.clear()

        self.saturation_history.clear()

        self.adoption_history.clear()

        self.trust_history.clear()

        self.log_text.delete(
            1.0,
            tk.END
        )

        scenario = self.scenario_var.get()

        self.add_log(
            "SMART CAMPUS MOBILITY SIMULATION"
        )

        self.add_log(
            "--------------------------------"
        )

        self.add_log(
            f"Scenario: {scenario.upper()}"
        )

        env = simpy.Environment()

        env.process(
            self.campus_behavior_generator(env)
        )

        env.run(
            until=SIMULATION_TIME
        )

        average_saturation = sum(
            self.saturation_history
        ) / len(
            self.saturation_history
        )

        # =========================================
        # FINAL RESULTS
        # =========================================

        self.add_log("")

        self.add_log(
            "===== FINAL RESULTS ====="
        )

        self.add_log(
            f"Final Adoption: "
            f"{self.adoption:.1f}%"
        )

        self.add_log(
            f"Final Trust: "
            f"{self.trust:.1f}%"
        )

        self.add_log(
            f"Average Saturation: "
            f"{average_saturation:.1f}%"
        )

        self.add_log(
            f"WhatsApp Usage: "
            f"{self.whatsapp_usage:.1f}%"
        )

        self.add_log(
            f"Successful Matches: "
            f"{self.total_matches}"
        )

        self.add_log(
            f"Overflow Vehicles: "
            f"{self.total_overflow}"
        )

        self.add_log(
            f"Sync Failures: "
            f"{self.total_sync_failures}"
        )

        self.add_log(
            f"Cancellations: "
            f"{self.total_cancellations}"
        )

        # =========================================
        # UPDATE PANEL
        # =========================================

        self.stats_label.config(

            text=(

                f"Scenario: "
                f"{scenario.upper()}\n\n"

                f"Final Adoption: "
                f"{self.adoption:.1f}%\n"

                f"Trust Score: "
                f"{self.trust:.1f}%\n"

                f"Average Saturation: "
                f"{average_saturation:.1f}%\n"

                f"Successful Matches: "
                f"{self.total_matches}\n"

                f"WhatsApp Usage: "
                f"{self.whatsapp_usage:.1f}%\n"

                f"Overflow Vehicles: "
                f"{self.total_overflow}\n"

                f"Sync Failures: "
                f"{self.total_sync_failures}\n"

                f"Cancellations: "
                f"{self.total_cancellations}"
            )
        )

        self.show_graphs()

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BehaviorCampusSimulation(root)

    root.mainloop()