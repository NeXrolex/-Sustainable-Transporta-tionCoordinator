# Sustainable Transportation Coordinator

**Universidad Distrital Francisco José de Caldas**  
**School of Engineering - Computer Engineering Program**  
**Course:** Systems Analysis & Design (Semester 2026-I)  
**Professor:** Eng. Carlos Andrés Sierra, M.Sc.  

### Team Members
- Julián David Muñoz Revelo (20251020042)
- Nicolás Acero Ladino (20251020044)
- Santiago Alexander García Bermeo (20242020268)
- Miguel Mateo Guillén Guzmán (20251020080)

---

## About the Project
The **Sustainable Transportation Coordinator** is a systems engineering project designed to solve mobility, communication, and parking bottlenecks for students traveling between university campuses (Calle 40, Calle 34, and ECCI). The project aims to formalize the university's carpooling culture through a secure, structured, and efficient platform.

---

## Repository Structure

### [Workshop 1: Systems Analysis](workshop_1/)
In the first phase of the project, we conducted a holistic systems analysis to identify the main transportation and parking problems at the Faculty of Engineering. We analyzed external factors, collected primary data through student surveys, and evaluated system sensitivity and complexity.

**Deliverables:**
- [Workshop 1 Document (PDF)](workshop_1/Workshop%20No.1.pdf)
- [Survey Data & Analysis](workshop_1/Data/)
- [Observation Images](workshop_1/Observation_Images/)

---

### [Workshop 2: Systems Design](Workshop_2/)
This workshop translates the analytical findings from Workshop 1 into a comprehensive systems design blueprint. 

#### Methodology
The design process involved defining the system architecture, required modules, and data flows to satisfy the functional requirements. We applied systems engineering principles such as modularity, scalability, and security, while focusing on risk mitigation for factors like unpredictable traffic conditions and community trust.

#### Key Design Decisions
- **Three-layer Architecture:** The system is divided into Client Interfaces (App/Dashboard), Application Services (Integration/Matching), and Data Layers.
- **Security & Trust:** Mandatory institutional email verification and connection to the university's vehicle database to ensure a safe environment.
- **Complexity Handling:** Implementation of a *Manual Status Update* module to handle unpredictable traffic delays without relying on complex automated GPS tracking.
- **System Resilience:** Integration of *Transaction Logs* to prevent data loss of active trips during network outages or server restarts.

**Deliverables:**
- [Workshop 2 System Design Document (PDF)](Workshop_2/Workshop_2.pdf)
- [Architecture Diagrams Source Files](Workshop_2/Diagrams/)
  - [System Architecture Diagram](Workshop_2/Diagrams/Graf.png)
  - [System Flowchart](Workshop_2/Diagrams/DiagramTwo.jpg)
  - [Integration and Data Flow Diagram](Workshop_2/Diagrams/DiagramThree.jpeg)

---
> *This repository is maintained for academic purposes as part of the Systems Analysis & Design course.*
