# Workshop 4 - System Simulation and Validation

This folder contains the materials developed for **Workshop 4** of the project **Campus Parking and Exit Carpool Coordination**.

## Structure

### `simulation/`
This folder contains the simulation artifacts used to validate the proposed system under different scenarios.

Included files:

- `Process-Oriented-Simulation.py`  
  Simulation focused on operational system behavior, including parking demand, overflow generation, carpool request handling, matching, cancellations, and synchronization issues. 

- `Behavior-Oriented-Simulation.py`  
  Simulation focused on behavioral system dynamics, including adoption, trust, WhatsApp dependence, parking saturation, and long-term participation effects. 

- `RUN_INSTRUCTIONS.txt`  
  File containing the detailed instructions required to run both simulations and interpret their outputs. 

- `Workshop_4.pdf`  
  Final report for Workshop 4, including methodology, scenarios, results, validation, complexity analysis, and recommendations. 

## Purpose

The purpose of Workshop 4 is to validate the proposed socio-technical system through computational simulation. The project is evaluated under three conditions: **baseline**, **optimization**, and **failure**, in order to test operational behavior, adoption dynamics, trust evolution, and system sensitivity to disruption. 

## Simulation Scope

The simulation stage is divided into two complementary approaches:

- The **Process-Oriented Simulation** evaluates short-term operational performance, especially parking demand, overflow, matching efficiency, and disruption caused by cancellations or synchronization failures.

- The **Behavior-Oriented Simulation** evaluates medium-term behavioral viability, especially adoption growth, trust degradation, dependence on informal coordination, and the effect of scenario conditions on continued participation. 

## Main Scenarios

The models are tested under three scenario types:

- **Baseline:** normal operation without strong support mechanisms. 
- **Optimization:** improved reliability and institutional support.
- **Failure:** stress conditions with stronger disruption, cancellations, and synchronization problems. 

## Main Findings

The simulation results support several important conclusions:

- The 110-space basement capacity is insufficient on high-demand days without coordination mechanisms. 
- Improved matching performance reduces overflow significantly.
- Adoption does not grow sustainably without incentives and service reliability. 
- Trust degrades when cancellations and synchronization failures accumulate.
- Rain combined with Friday demand creates a critical overload condition

## Execution Notes

Detailed setup and execution steps are provided in `RUN_INSTRUCTIONS.txt`. 

## Project Context

Workshop 4 builds directly on the previous phases of the project:

- **Workshop 1:** empirical diagnosis of parking saturation and informal coordination. 
- **Workshop 2:** conceptual system architecture and operational structure. 
- **Workshop 3:** socio-technical refinement, risk analysis, accountability perspective, and implementation strategy.

## Note

This repository section documents the simulation and validation stage of the project. The workshop focuses on evaluating system behavior and design feasibility before any controlled pilot implementation is considered. 
