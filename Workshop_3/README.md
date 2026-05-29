# Workshop 3 – Campus Parking and Exit Carpool Coordinator

## 1. Workshop Overview

This workshop develops a **robust conceptual design and project management framework** for the *Campus Parking and Exit Carpool Coordinator*, an information system that manages parking capacity at the engineering campuses and coordinates shared trips from campus to key city zones during peak departure windows.  

The work builds on Workshops 1 and 2, which revealed **severe parking saturation**, daily motorcycle overflow to public streets, bottlenecks at the Calle 40 basement entrance, and strong dependence on informal coordination through messaging apps.  

In Workshop 3 the original *Sustainable Transportation Coordinator* concept (inter‑campus carpooling + bike sharing) is **refined**: bike‑sharing is considered infeasible in the short term, and the scope is narrowed to campus parking management and exit‑time carpooling.

---

## 2. Main Contents

### 2.1 System Evolution

- Summary of Workshop 1: empirical analysis of transport and parking conditions (field observation, parking measurements, survey with 51 users).  
- Summary of Workshop 2: initial layered architecture with a student app, security dashboard, integration with vehicle and user registries, and a data/monitoring layer.  
- Scope refinement: renaming of the system to **Campus Parking and Exit Carpool Coordinator** and focus on parking inventory, reservation policies, and exit‑time carpool flows.

### 2.2 Architecture Refinement

The architecture is organised conceptually into four layers:

- **Client Layer:** student web/mobile interface and security/operations dashboard.  
- **Application Layer:** Authentication Service, Parking Inventory Service, Parking Allocation & Policy Engine, Exit Carpool Matching Service, Notification & Messaging Service. 
- **Integration Layer:** logical adapters to institutional user and vehicle registries.  
- **Data & Monitoring Layer:** conceptual repositories for users, vehicles, parking states, carpool offers, audit logs and operational indicators.

The design is **technology‑agnostic**: services, responsibilities and interfaces are defined, but no concrete stack or implementation is specified.

### 2.3 Risk Management

A structured risk analysis is performed for technical and security threats at the Calle 40 campus, including:

- Data desynchronization between the app and the real parking state.  
- Chat service downtime during peak hours.  
- Unauthorized users accessing the platform.  
- Data breaches exposing sensitive user information. 

Each risk is described with **category, impact/probability, mitigation strategy and contingency plan**, following ISO‑style risk management guidance.

### 2.4 Quality and Project Management

Workshop 3 also defines:

- **Quality framework:** alignment with ISO 31000 and ISO/IEC 25010 for reliability, performance and security.  
- **Project management structure:** phased work plan, responsibilities and deliverables to guide a future implementation, without writing production code in this workshop.[file:20]

---

## 3. Deliverables in This Folder

- `WORKSHOP 3.pdf` – full Workshop 3 document (robust design and project management).  

Use the main repository README to navigate between Workshop 1, Workshop 2 and this Workshop 3.
