# Workshop 2 - System Design

**Sustainable Transportation Coordinator**  
Systems Analysis & Design - Semester 2026-I

## Overview
This workshop translates the analytical findings from Workshop 1 into a comprehensive systems design for the Sustainable Transportation Coordinator. The proposed solution focuses on addressing parking bottlenecks and formalizing the carpooling culture among university students to improve transportation between campuses (Calle 40, Calle 34, and ECCI).

## Methodology
The design process involved defining the system architecture, required modules, and data flows to satisfy the functional requirements established in the previous analysis phase. We applied core systems engineering principles—such as modularity, scalability, and security—while prioritizing risk mitigation for factors like unpredictable traffic conditions and the need for community trust.

## Key Design Decisions
- **Three-layer Architecture:** The system is divided into Client Interfaces (Mobile App/Web Dashboard), Application Services (Integration/Matching Engine), and Data Layers.
- **Security & Trust:** Implementation of mandatory institutional email verification and connection to the university's vehicle database to ensure a safe environment.
- **Complexity Handling:** Creation of a *Manual Status Update* module to handle unpredictable traffic delays without relying on complex, error-prone automated GPS tracking.
- **System Resilience:** Integration of *Transaction Logs* within the persistence layer to prevent data loss of active trips during network outages or temporary server restarts.

## Deliverables

### Documentation
- [System Design Document (PDF)](Workshop_2.pdf)

### Visual Design Representations
- [Diagrams Directory](Diagrams/)
  - [Figure 1: System Architecture Diagram](Diagrams/Graf.png)
  - [Figure 2: System Flowchart](Diagrams/DiagramTwo.jpg)
  - [Figure 3: Integration and Data Flow Architecture](Diagrams/DiagramThree.jpeg)
