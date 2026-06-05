import tkinter as tk
from tkinter import ttk
import simpy
import random
import math
from collections import deque

# =========================================================
# CONSTANTS
# =========================================================

TOTAL_SPACES     = 110
CARPOOL_SPACES   = 12          # spaces reserved for carpool (blue)
BLOCKED_SPACES   = 5           # permanently blocked spaces
SIM_SPEED        = 0.05        # seconds per simulated minute
RAIN_PROBABILITY = 0.35
RAIN_BOOST       = 1.35
OVERFLOW_ALERT   = 0.90        # 90% → saturation warning

# ─── State identifiers ────────────────────────────────────
AVAILABLE  = "AVAILABLE"
RESERVED   = "RESERVED"
OCCUPIED   = "OCCUPIED"
BLOCKED    = "BLOCKED"
PRIORITY   = "PRIORITY"

# ─── Colors per state ─────────────────────────────────────
STATE_COLOR = {
    AVAILABLE : "#27ae60",
    RESERVED  : "#f1c40f",
    OCCUPIED  : "#e74c3c",
    BLOCKED   : "#7f8c8d",
    PRIORITY  : "#2980b9",
}

# ─── Arrival/departure probability per hour block ─────────
# Perfil real: desde las 6 empieza a llegar gente.
# De 8 a 14 el parqueadero está prácticamente lleno —
# salidas muy bajas, casi no hay rotación.
# A las 12 es casi imposible conseguir cupo.
# Desde las 14 empieza la rotación y a las 16-17 la salida masiva.
HOURLY_PROFILE = [
    (0,  6,  0.00, 0.00),   # Madrugada – cerrado
    (6,  7,  0.60, 0.02),   # Llegadas tempranas, se empieza a llenar
    (7,  8,  0.85, 0.01),   # Rush intenso – llena al 95%+ al terminar
    (8,  9,  0.50, 0.01),   # Sigue llenándose, casi sin salidas → 100%
    (9,  10, 0.20, 0.01),   # Ya lleno, muy poca rotación
    (10, 11, 0.15, 0.01),   # Lleno total, mínimas salidas
    (11, 12, 0.10, 0.01),   # Prácticamente sin cupos
    (12, 13, 0.10, 0.02),   # Hora pico: lleno, casi nadie sale
    (13, 14, 0.08, 0.04),   # Levísima rotación, aún muy lleno
    (14, 15, 0.10, 0.12),   # Empieza algo de rotación ~85-90%
    (15, 16, 0.08, 0.18),   # Más salidas ~75%
    (16, 17, 0.04, 0.35),   # Salidas aceleradas
    (17, 18, 0.02, 0.55),   # Éxodo fuerte
    (18, 20, 0.01, 0.80),   # Éxodo masivo
    (20, 24, 0.00, 0.40),   # Últimos vehículos
]

BG_DARK   = "#0f1923"
BG_CARD   = "#162230"
BG_PANEL  = "#1a2b3c"
FG_WHITE  = "#ecf0f1"
FG_MUTED  = "#8899aa"
ACCENT    = "#3498db"

# =========================================================
# PARKING SPACE – FINITE STATE AUTOMATON
# =========================================================

class ParkingSpace:
    """
    Finite-state automaton for a single parking space.

    Valid transitions
    ─────────────────
    AVAILABLE  → RESERVED  (vehicle books the spot)
    RESERVED   → OCCUPIED  (vehicle arrives)
    OCCUPIED   → AVAILABLE (vehicle leaves)
    AVAILABLE  → BLOCKED   (maintenance / event)
    BLOCKED    → AVAILABLE (maintenance ends)
    AVAILABLE  → PRIORITY  (carpool slot activated)
    PRIORITY   → OCCUPIED  (carpool vehicle parks)
    OCCUPIED   → AVAILABLE (carpool vehicle leaves – same exit)
    """

    TRANSITIONS = {
        AVAILABLE : [RESERVED, BLOCKED, PRIORITY],
        RESERVED  : [OCCUPIED],
        OCCUPIED  : [AVAILABLE],
        BLOCKED   : [AVAILABLE],
        PRIORITY  : [OCCUPIED],
    }

    def __init__(self, space_id: int, initial_state: str = AVAILABLE):
        self.space_id = space_id
        self.state    = initial_state

    def can_transition(self, new_state: str) -> bool:
        return new_state in self.TRANSITIONS.get(self.state, [])

    def transition(self, new_state: str) -> bool:
        if self.can_transition(new_state):
            self.state = new_state
            return True
        return False


# =========================================================
# SIMULATION ENGINE (SimPy)
# =========================================================

class ParkingSimEngine:

    def __init__(self, callback_tick):
        self.callback_tick   = callback_tick
        self.env             = simpy.Environment()
        self._running        = False
        self._after_id       = None

        # Spaces: first CARPOOL_SPACES are priority-capable,
        # last BLOCKED_SPACES start blocked
        self.spaces = []
        for i in range(TOTAL_SPACES):
            if i >= TOTAL_SPACES - BLOCKED_SPACES:
                self.spaces.append(ParkingSpace(i, BLOCKED))
            else:
                self.spaces.append(ParkingSpace(i, AVAILABLE))

        # Stats
        self.sim_hour        = 6       # simulation starts at 06:00
        self.sim_minute      = 0
        self.raining         = False
        self.rejected        = 0
        self.carpool_active  = 0
        self.coordinated     = 0
        self.day_finished    = False

    # ── helpers ───────────────────────────────────────────

    def _count(self, state):
        return sum(1 for s in self.spaces if s.state == state)

    def _free_spaces(self, state=AVAILABLE):
        return [s for s in self.spaces if s.state == state]

    def _arrival_prob(self):
        h = self.sim_hour
        for (h0, h1, ap, _) in HOURLY_PROFILE:
            if h0 <= h < h1:
                p = ap
                if self.raining:
                    p = min(1.0, p * RAIN_BOOST)
                return p
        return 0.00

    def _depart_prob(self):
        h = self.sim_hour
        for (h0, h1, _, dp) in HOURLY_PROFILE:
            if h0 <= h < h1:
                return dp
        return 0.00

    # ── SimPy process ─────────────────────────────────────

    def _tick_process(self, env):
        while True:
            # ── advance clock ──
            self.sim_minute += 1
            if self.sim_minute >= 60:
                self.sim_minute = 0
                self.sim_hour  += 1
                self.raining    = random.random() < RAIN_PROBABILITY

            # ── end of day ──
            if self.sim_hour >= 24:
                self.day_finished = True
                self.callback_tick()
                return

            ap = self._arrival_prob()
            h  = self.sim_hour

            # Peak hours allow up to 3 arrivals per tick
            if 6 <= h < 8:
                max_arrivals = 3
            elif h == 8:
                max_arrivals = 2
            else:
                max_arrivals = 1

            num_arrivals = sum(
                1 for _ in range(max_arrivals) if random.random() < ap
            )

            for _ in range(num_arrivals):
                is_carpool = random.random() < 0.15
                if is_carpool:
                    slots  = self._free_spaces(AVAILABLE)
                    pslots = [s for s in slots if s.space_id < CARPOOL_SPACES]
                    target = pslots[0] if pslots else (slots[0] if slots else None)
                    if target:
                        if target.space_id < CARPOOL_SPACES:
                            target.transition(PRIORITY)
                            target.transition(OCCUPIED)
                            self.carpool_active += 1
                            self.coordinated    += 1
                        else:
                            target.transition(RESERVED)
                            target.transition(OCCUPIED)
                    else:
                        self.rejected += 1
                else:
                    slots  = self._free_spaces(AVAILABLE)
                    normal = [s for s in slots if s.space_id >= CARPOOL_SPACES]
                    target = normal[0] if normal else (slots[0] if slots else None)
                    if target:
                        if random.random() < 0.10:
                            target.transition(RESERVED)
                            if random.random() < 0.80:
                                target.transition(OCCUPIED)
                        else:
                            target.transition(RESERVED)
                            target.transition(OCCUPIED)
                    else:
                        self.rejected += 1

            # ── departures ──
            dp = self._depart_prob()
            for space in self.spaces:
                if space.state == OCCUPIED and random.random() < dp:
                    space.transition(AVAILABLE)
                    if self.carpool_active > 0:
                        self.carpool_active = max(0, self.carpool_active - 1)

            # ── unblock randomly ──
            for space in self.spaces:
                if space.state == BLOCKED and random.random() < 0.002:
                    space.transition(AVAILABLE)

            self.callback_tick()
            yield env.timeout(1)

    def start(self, root):
        self._running = True
        self.env.process(self._tick_process(self.env))
        self._root = root
        self._schedule(root)

    def _schedule(self, root):
        if self._running:
            self.env.step()
            self._after_id = root.after(
                int(SIM_SPEED * 1000), self._schedule, root
            )

    def stop(self):
        self._running = False
        if self._after_id:
            self._root.after_cancel(self._after_id)

    def reset(self):
        self.stop()
        self.__init__(self.callback_tick)


# =========================================================
# MAIN APPLICATION
# =========================================================

class ParkingAutomatonApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Campus Parking Automaton  ·  Universidad Distrital")
        self.root.geometry("1520x900")
        self.root.minsize(1200, 760)
        self.root.configure(bg=BG_DARK)

        self._sim_running = False
        self.engine = ParkingSimEngine(self._on_tick)

        self._build_ui()
        self._draw_grid()
        self._refresh_metrics()

    # ======================================================
    # UI CONSTRUCTION
    # ======================================================

    def _build_ui(self):
        # ── top bar ───────────────────────────────────────
        topbar = tk.Frame(self.root, bg=BG_DARK, height=60)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(
            topbar,
            text="⬡  CAMPUS PARKING AUTOMATON",
            bg=BG_DARK, fg=ACCENT,
            font=("Segoe UI", 15, "bold")
        ).pack(side="left", padx=20, pady=12)

        tk.Label(
            topbar,
            text="Facultad de Ingeniería  ·  Universidad Distrital",
            bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 9)
        ).pack(side="left", padx=5, pady=12)

        # controls on the right
        ctrl = tk.Frame(topbar, bg=BG_DARK)
        ctrl.pack(side="right", padx=15)

        self._btn_run = tk.Button(
            ctrl, text="▶  START",
            bg=ACCENT, fg="white",
            font=("Segoe UI", 9, "bold"),
            bd=0, padx=14, pady=6, cursor="hand2",
            activebackground="#2471a3",
            command=self._toggle_sim
        )
        self._btn_run.pack(side="left", padx=4)

        tk.Button(
            ctrl, text="↺  RESET",
            bg=BG_CARD, fg=FG_WHITE,
            font=("Segoe UI", 9, "bold"),
            bd=0, padx=14, pady=6, cursor="hand2",
            activebackground=BG_PANEL,
            command=self._reset_sim
        ).pack(side="left", padx=4)

        tk.Label(
            ctrl, text="Speed",
            bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 8)
        ).pack(side="left", padx=(12, 2))

        self._speed_var = tk.DoubleVar(value=SIM_SPEED)
        speed_slider = ttk.Scale(
            ctrl, from_=0.01, to=0.20,
            orient="horizontal", length=90,
            variable=self._speed_var,
            command=self._on_speed_change
        )
        speed_slider.pack(side="left")

        # ── main layout ───────────────────────────────────
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # LEFT: sidebar
        self._sidebar = tk.Frame(body, bg=BG_DARK, width=230)
        self._sidebar.pack(side="left", fill="y", padx=(0, 8))
        self._sidebar.pack_propagate(False)

        # CENTER: grid only
        center = tk.Frame(body, bg=BG_DARK)
        center.pack(side="left", fill="both", expand=True)

        # grid card
        grid_card = tk.Frame(center, bg=BG_CARD, bd=0)
        grid_card.pack(fill="both", expand=True)

        grid_header = tk.Frame(grid_card, bg=BG_CARD)
        grid_header.pack(fill="x", padx=12, pady=(10, 6))

        tk.Label(
            grid_header, text="PARKING GRID  —  110 SPACES",
            bg=BG_CARD, fg=FG_WHITE,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        self._clock_label = tk.Label(
            grid_header, text="06:00",
            bg=BG_CARD, fg=ACCENT,
            font=("Consolas", 18, "bold")
        )
        self._clock_label.pack(side="right", padx=(0, 10))

        self._weather_label = tk.Label(
            grid_header, text="☀  Día normal",
            bg=BG_CARD, fg="#f1c40f",
            font=("Segoe UI", 10)
        )
        self._weather_label.pack(side="right", padx=10)

        # legend
        legend_frame = tk.Frame(grid_card, bg=BG_CARD)
        legend_frame.pack(fill="x", padx=12, pady=(0, 8))
        for state, color in STATE_COLOR.items():
            dot = tk.Frame(legend_frame, bg=color, width=12, height=12)
            dot.pack(side="left")
            tk.Label(
                legend_frame, text=state,
                bg=BG_CARD, fg=FG_MUTED,
                font=("Segoe UI", 7, "bold")
            ).pack(side="left", padx=(3, 12))

        # canvas for grid
        self._grid_canvas = tk.Canvas(
            grid_card, bg=BG_CARD,
            height=240, highlightthickness=0
        )
        self._grid_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # saturation alert
        self._alert_label = tk.Label(
            grid_card, text="",
            bg=BG_CARD, fg="#e74c3c",
            font=("Segoe UI", 9, "bold")
        )
        self._alert_label.pack(pady=(0, 6))

        # ── sidebar content ───────────────────────────────
        self._build_sidebar()

    def _build_sidebar(self):

        def card(parent, title):
            f = tk.Frame(parent, bg=BG_CARD, bd=0)
            f.pack(fill="x", pady=(0, 8))
            tk.Label(
                f, text=title,
                bg=BG_CARD, fg=ACCENT,
                font=("Segoe UI", 8, "bold")
            ).pack(anchor="w", padx=12, pady=(10, 4))
            return f

        def stat_row(parent, label, var, color=FG_WHITE):
            row = tk.Frame(parent, bg=BG_CARD)
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(
                row, text=label,
                bg=BG_CARD, fg=FG_MUTED,
                font=("Segoe UI", 8), width=18, anchor="w"
            ).pack(side="left")
            lbl = tk.Label(
                row, textvariable=var,
                bg=BG_CARD, fg=color,
                font=("Consolas", 10, "bold"), width=6, anchor="e"
            )
            lbl.pack(side="right")
            return lbl

        # ── occupancy card ────────────────────────────────
        oc = card(self._sidebar, "◉  OCCUPANCY")
        self._v_avail   = tk.StringVar(value="—")
        self._v_reserv  = tk.StringVar(value="—")
        self._v_occup   = tk.StringVar(value="—")
        self._v_block   = tk.StringVar(value="—")
        self._v_prior   = tk.StringVar(value="—")
        self._v_pct     = tk.StringVar(value="—")

        stat_row(oc, "Available",   self._v_avail,  STATE_COLOR[AVAILABLE])
        stat_row(oc, "Reserved",    self._v_reserv, STATE_COLOR[RESERVED])
        stat_row(oc, "Occupied",    self._v_occup,  STATE_COLOR[OCCUPIED])
        stat_row(oc, "Blocked",     self._v_block,  STATE_COLOR[BLOCKED])
        stat_row(oc, "Priority",    self._v_prior,  STATE_COLOR[PRIORITY])

        prog_frame = tk.Frame(oc, bg=BG_CARD)
        prog_frame.pack(fill="x", padx=12, pady=(6, 4))
        tk.Label(
            prog_frame, text="Occupancy",
            bg=BG_CARD, fg=FG_MUTED,
            font=("Segoe UI", 8)
        ).pack(side="left")
        tk.Label(
            prog_frame, textvariable=self._v_pct,
            bg=BG_CARD, fg=FG_WHITE,
            font=("Consolas", 10, "bold")
        ).pack(side="right")

        self._occ_bar_bg = tk.Frame(oc, bg="#1e3a4a", height=8)
        self._occ_bar_bg.pack(fill="x", padx=12, pady=(0, 10))
        self._occ_bar    = tk.Frame(self._occ_bar_bg, bg=STATE_COLOR[AVAILABLE], height=8)
        self._occ_bar.place(relx=0, rely=0, relwidth=0.0, relheight=1.0)

        # ── carpool card ──────────────────────────────────
        cc = card(self._sidebar, "🚗  CARPOOL")
        self._v_carpool_active = tk.StringVar(value="—")
        self._v_coordinated    = tk.StringVar(value="—")
        self._v_prior_used     = tk.StringVar(value="—")

        stat_row(cc, "Active carpools",  self._v_carpool_active, STATE_COLOR[PRIORITY])
        stat_row(cc, "Coordinated",      self._v_coordinated,    "#9b59b6")
        stat_row(cc, "Priority used",    self._v_prior_used,     STATE_COLOR[PRIORITY])
        tk.Frame(cc, bg=BG_CARD, height=6).pack()

        # ── events card ───────────────────────────────────
        ev = card(self._sidebar, "⚡  EVENTS")
        self._v_rejected = tk.StringVar(value="—")
        stat_row(ev, "Rejected vehicles", self._v_rejected, "#e74c3c")
        tk.Frame(ev, bg=BG_CARD, height=6).pack()

        # ── automaton transitions card ────────────────────
        tr = card(self._sidebar, "🔀  AUTOMATON STATES")
        transitions = [
            ("AVAILABLE → RESERVED",  STATE_COLOR[RESERVED]),
            ("RESERVED → OCCUPIED",   STATE_COLOR[OCCUPIED]),
            ("OCCUPIED → AVAILABLE",  STATE_COLOR[AVAILABLE]),
            ("AVAILABLE → BLOCKED",   STATE_COLOR[BLOCKED]),
            ("BLOCKED → AVAILABLE",   STATE_COLOR[AVAILABLE]),
            ("AVAILABLE → PRIORITY",  STATE_COLOR[PRIORITY]),
            ("PRIORITY → OCCUPIED",   STATE_COLOR[OCCUPIED]),
        ]
        for txt, col in transitions:
            row = tk.Frame(tr, bg=BG_CARD)
            row.pack(fill="x", padx=8, pady=1)
            dot = tk.Frame(row, bg=col, width=8, height=8)
            dot.pack(side="left", pady=3)
            tk.Label(
                row, text=txt,
                bg=BG_CARD, fg=FG_MUTED,
                font=("Segoe UI", 7)
            ).pack(side="left", padx=4)
        tk.Frame(tr, bg=BG_CARD, height=6).pack()

    # ======================================================
    # PARKING GRID DRAWING
    # ======================================================

    def _draw_grid(self):
        self._grid_canvas.update_idletasks()
        self._cell_ids = []

        canvas = self._grid_canvas
        w = canvas.winfo_width() or 900
        cols   = 22
        rows   = math.ceil(TOTAL_SPACES / cols)
        margin = 10
        cell_w = (w - 2 * margin) / cols
        cell_h = 28
        canvas.config(height=int(rows * cell_h + 2 * margin + 10))

        for i, space in enumerate(self.engine.spaces):
            col = i % cols
            row = i // cols
            x0  = margin + col * cell_w + 1
            y0  = margin + row * cell_h + 1
            x1  = x0 + cell_w - 3
            y1  = y0 + cell_h - 3

            rect = canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=STATE_COLOR[space.state],
                outline=BG_DARK, width=1
            )
            txt = canvas.create_text(
                (x0 + x1) / 2, (y0 + y1) / 2,
                text=str(i + 1),
                fill="white",
                font=("Segoe UI", 6, "bold")
            )
            self._cell_ids.append((rect, txt))

    def _refresh_grid(self):
        canvas  = self._grid_canvas
        w       = canvas.winfo_width() or 900
        cols    = 22
        margin  = 10
        cell_w  = (w - 2 * margin) / cols
        cell_h  = 28

        for i, space in enumerate(self.engine.spaces):
            rect, _ = self._cell_ids[i]
            col = i % cols
            row = i // cols
            x0  = margin + col * cell_w + 1
            y0  = margin + row * cell_h + 1
            x1  = x0 + cell_w - 3
            y1  = y0 + cell_h - 3
            canvas.coords(rect, x0, y0, x1, y1)
            canvas.itemconfig(rect, fill=STATE_COLOR[space.state])

    # ======================================================
    # METRICS PANEL
    # ======================================================

    def _refresh_metrics(self):
        e   = self.engine
        occ = e._count(OCCUPIED)
        ava = e._count(AVAILABLE)
        res = e._count(RESERVED)
        blk = e._count(BLOCKED)
        pri = e._count(PRIORITY)

        pct = (occ + res) / TOTAL_SPACES

        self._v_avail.set(str(ava))
        self._v_reserv.set(str(res))
        self._v_occup.set(str(occ))
        self._v_block.set(str(blk))
        self._v_prior.set(str(pri))
        self._v_pct.set(f"{pct:.0%}")
        self._v_rejected.set(str(e.rejected))
        self._v_carpool_active.set(str(e.carpool_active))
        self._v_coordinated.set(str(e.coordinated))
        self._v_prior_used.set(str(e._count(PRIORITY) + e.carpool_active))

        bar_color = (
            "#e74c3c" if pct >= OVERFLOW_ALERT
            else "#f39c12" if pct >= 0.70
            else STATE_COLOR[AVAILABLE]
        )
        self._occ_bar.place(relwidth=min(pct, 1.0))
        self._occ_bar.config(bg=bar_color)

        self._clock_label.config(
            text=f"{e.sim_hour:02d}:{e.sim_minute:02d}"
        )

        if e.raining:
            self._weather_label.config(
                text="🌧  Lluvia  (+35% demanda)", fg="#74b9ff"
            )
        else:
            self._weather_label.config(
                text="☀  Día normal", fg="#f1c40f"
            )

        if pct >= 1.0:
            self._alert_label.config(
                text="⛔  OVERFLOW — PARQUEADERO LLENO  ·  "
                     f"Vehículos rechazados: {e.rejected}"
            )
        elif pct >= OVERFLOW_ALERT:
            self._alert_label.config(
                text=f"⚠  SATURACIÓN  —  {pct:.0%} ocupado"
            )
        else:
            self._alert_label.config(text="")

    # ======================================================
    # SIMULATION CONTROL
    # ======================================================

    def _on_tick(self):
        self._refresh_grid()
        self._refresh_metrics()

        if self.engine.day_finished and self._sim_running:
            self._sim_running = False
            self.engine.stop()
            self._btn_run.config(
                text="✔  DÍA TERMINADO",
                bg="#27ae60",
                activebackground="#1e8449"
            )
            self._alert_label.config(
                text="✔  Simulación completada — 06:00 → 24:00",
                fg="#2ecc71"
            )

    def _toggle_sim(self):
        if self.engine.day_finished:
            return
        if not self._sim_running:
            self._sim_running = True
            self._btn_run.config(text="⏸  PAUSE", bg="#c0392b",
                                 activebackground="#96281b")
            self.engine.start(self.root)
        else:
            self._sim_running = False
            self._btn_run.config(text="▶  RESUME", bg=ACCENT,
                                 activebackground="#2471a3")
            self.engine.stop()

    def _reset_sim(self):
        self._sim_running = False
        self._btn_run.config(text="▶  START", bg=ACCENT,
                             activebackground="#2471a3")
        self.engine.reset()
        self.engine.callback_tick = self._on_tick
        self._alert_label.config(text="", fg="#e74c3c")
        self._draw_grid()
        self._refresh_metrics()

    def _on_speed_change(self, _=None):
        global SIM_SPEED
        SIM_SPEED = self._speed_var.get()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app  = ParkingAutomatonApp(root)
    root.mainloop()
