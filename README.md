# Sustainable Transportation Coordinator

**Universidad Distrital Francisco José de Caldas**  
School of Engineering – Computer Engineering Program  
Course: Systems Analysis & Design (Semester 2026‑I)  
Professor: Eng. Carlos Andrés Sierra, M.Sc.

## Team Members

- Julián David Muñoz Revelo (20251020042)  
- Nicolás Acero Ladino (20251020044)  
- Santiago Alexander García Bermeo (20242020268)  
- Miguel Mateo Guillén Guzmán (20251020080)  

---

## About the Project

The **Sustainable Transportation Coordinator** is a systems engineering project designed to address mobility, communication and parking bottlenecks affecting students at the Faculty of Engineering, with a focus on the Calle 40, Calle 34 and ECCI campuses.[file:12]  

Across the three workshops, the project **evolves** from a broad sustainable mobility concept (inter‑campus carpooling and bike sharing) to a more feasible and focused solution called the **Campus Parking and Exit Carpool Coordinator**, which concentrates on campus parking management and exit‑time carpooling while keeping the initial analyses as context.[file:20]

---

## Repository Structure

- `workshop_1/` – Systems Analysis  
- `Workshop_2/` – Systems Design  
- `Workshop_3/` – Robust System Design and Project Management  
- `Catch_Up/` – Project poster and consolidated catch‑up material  

---

## Workshop 1: Systems Analysis

**Folder:** [`workshop_1`](./workshop_1)

In the first phase of the project, we conducted a **holistic systems analysis** to identify the main transportation and parking problems at the Faculty of Engineering.[file:12] We analysed external factors, collected primary data through student surveys, performed direct observations at the Calle 40 campus, and evaluated system sensitivity and complexity.[file:12]

**Deliverables:**

- [`Workshop No.1.pdf`](./workshop_1/Workshop%20No.1.pdf) – full analysis report.  
- [`Data/`](./workshop_1/Data) – survey data and analysis.  
- [`Observation_Images/`](./workshop_1/Observation_Images) – pictures documenting parking and access conditions.  
- [`README.md`](./workshop_1/README.md) – summary of goals, methodology and findings.

---

## Workshop 2: Systems Design

**Folder:** [`Workshop_2`](./Workshop_2)

This workshop translates the analytical findings from Workshop 1 into a **comprehensive systems design blueprint**.[file:11]

### Methodology

The design process involved defining the **system architecture, core modules and data flows** to satisfy the functional and non‑functional requirements.[file:11] We applied systems engineering principles such as modularity, scalability and security, with explicit attention to risk factors like unpredictable traffic conditions and community trust.[file:11]

### Key Design Decisions

- **Layered Architecture:** the system is divided into Client Interfaces (student app and security dashboard), Application Services (integration and matching) and Data Layers.[file:11]  
- **Security & Trust:** mandatory institutional email verification and connection to the university’s vehicle database to ensure a closed, trusted community.[file:11]  
- **Complexity Handling:** a **Manual Status Update** module allows drivers and staff to adjust trip status in response to unpredictable traffic, without depending on complex GPS tracking.[file:11]  
- **System Resilience:** integration of **transaction logs** and connection‑pooling strategies to avoid the loss of active trips during network outages or server restarts.[file:11]

### Deliverables

- [`Workshop_2.pdf`](./Workshop_2/Workshop_2.pdf) – system design document.  
- [`Diagrams/`](./Workshop_2/Diagrams) – source files for the diagrams.  
- [System Architecture Diagram](./Workshop_2/Diagrams/Graf.png)  
- [System Flowchart](./Workshop_2/Diagrams/DiagramTwo.jpg)  
- [Integration and Data Flow Diagram](./Workshop_2/Diagrams/DiagramThree.jpeg)  
- [`README.md`](./Workshop_2/README.md) – workshop summary.

---

## Workshop 3: Robust System Design and Project Management

**Folder:** [`Workshop_3`](./Workshop_3)

In Workshop 3, the project is **refined and re‑scoped** into the **Campus Parking and Exit Carpool Coordinator**, an information system that manages parking capacity at the engineering campuses and coordinates shared trips from campus to key city zones during peak departure windows.[file:20]  

The workshop focuses on **conceptual design only**: no production software is implemented. Instead, the team strengthens the architecture, defines risk and quality frameworks, and prepares a project management plan for a future implementation.[file:20]

### Scope Evolution

- Original concept: *Sustainable Transportation Coordinator* (inter‑campus carpool + bike‑sharing).  
- Final scope in Workshop 3: **Campus Parking and Exit Carpool Coordinator**, centred on parking inventory/reservation, policy‑based prioritisation of shared vehicles, and exit‑time carpool matching.[file:20]

### Main Contributions

- **Architecture Refinement:**  
  - Layered conceptual architecture with client, application, integration and data/monitoring layers.  
  - Specific services for authentication, parking inventory, parking allocation & policy, exit‑time carpool matching and notifications.[file:20]

- **Conceptual Web Interfaces:**  
  - Student web/mobile interface with dashboard, parking module and exit‑time carpool module.  
  - Security and operations dashboard to monitor occupancy, manage access and review policy violations.[file:20]

- **Risk Management:**  
  - Identification of technical and security risks (data desynchronization, chat downtime, unauthorized users, data breaches, etc.).  
  - Mitigation and contingency strategies aligned with ISO‑style risk management practices.[file:20]

- **Quality and Project Management Framework:**  
  - Quality criteria aligned with ISO 31000 and ISO/IEC 25010 (reliability, performance, security).  
  - High‑level project plan and responsibilities to guide a future implementation.[file:20]

### Deliverables

- [`WORKSHOP 3.pdf`](./Workshop_3/WORKSHOP%203.pdf) – robust design and project management document.  
- `demo/` – additional diagrams or demo artefacts (if used during the workshop).  
- [`README.md`](./Workshop_3/README.md) – summary of Workshop 3 scope and contents.

---

## Catch‑Up and Final Artifacts

**Folder:** [`Catch_Up`](./Catch_Up)

- Project poster and consolidated documentation connecting all three workshops.  
- Final “Sustainable Transportation Coordinator / Campus Parking and Exit Carpool Coordinator” narrative.

This repository collects all **analysis, design and planning artefacts** required for the Systems Analysis & Design course project.
