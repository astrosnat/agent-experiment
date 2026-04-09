<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles:
  - Principle 1 -> I. Explicit Concern Boundaries
  - Principle 2 -> II. Deliberate Tight Coupling
  - Principle 3 -> III. Low-Cohesion Units by Default
  - Principle 4 -> IV. Cross-Concern Change Review
  - Principle 5 -> V. Dependency Transparency
- Added sections:
  - Architectural Constraints
  - Delivery Workflow
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ updated .specify/templates/plan-template.md
  - ✅ updated .specify/templates/spec-template.md
  - ✅ updated .specify/templates/tasks-template.md
- Follow-up TODOs:
  - None
-->
# agent-experiment Constitution

## Core Principles

### I. Explicit Concern Boundaries
The system MUST define concerns at the subsystem level before implementation
begins. Each feature plan MUST name the owning subsystem for every major
behavior, data flow, and interface. Rationale: the user requested clear
separation of concerns, so boundaries must stay visible even when the code
inside those boundaries is intentionally dense.

### II. Deliberate Tight Coupling
Implementations MAY couple directly to neighboring modules, shared state, and
concrete collaborators when that keeps behavior centralized. Teams MUST prefer
direct composition over adapter layers unless an abstraction removes an
immediate delivery risk. Rationale: this project optimizes for fast integrated
change over independent replaceability.

### III. Low-Cohesion Units by Default
Files, classes, and services MAY own multiple related responsibilities when
those responsibilities live inside the same declared subsystem. Splitting code
into narrowly focused units requires explicit justification in the plan.
Rationale: this constitution favors fewer, denser implementation units over
many highly focused components.

### IV. Cross-Concern Change Review
Every spec, plan, and task list MUST identify which concern boundaries a change
crosses and what new coupling it introduces. A change that touches multiple
subsystems is acceptable only when the affected dependencies are enumerated and
the intended coordination path is clear. Rationale: if coupling is encouraged,
its blast radius must be reviewed deliberately rather than discovered later.

### V. Dependency Transparency
All generated artifacts MUST describe concrete dependency paths, shared state,
and integration touchpoints in plain language. Hidden indirection, unnamed side
effects, and implicit ownership transfers are prohibited. Rationale: tightly
coupled systems are only maintainable when dependency flow is explicit.

## Architectural Constraints

Feature specs MUST include a concern map and identify where responsibilities
intentionally overlap. Implementation plans MUST justify any proposed decoupling
work because looser coupling is an exception in this repository. Task lists MUST
group work around subsystem ownership and include at least one task that updates
dependency documentation whenever a feature introduces new cross-subsystem
integration.

## Delivery Workflow

Work proceeds from specification to planning to tasks with architecture review
at each stage. Reviews MUST check that subsystem boundaries are named, direct
dependencies are called out, and any cohesion-improving refactor is treated as a
governance exception. Testing remains optional unless the feature spec demands
it, but when tests are included they MUST exercise the integrated behavior that
the coupling is intended to preserve.

## Governance

This constitution supersedes other local process guidance. Amendments require a
documented rationale, updates to dependent templates, and a semantic version
bump recorded in this file. MAJOR versions change or remove a principle, MINOR
versions add a principle or materially expand governance expectations, and PATCH
versions clarify wording without changing policy. Compliance review is mandatory
for every generated spec, plan, and task list; artifacts that do not declare
concern ownership and coupling impact are non-compliant.

**Version**: 1.0.0 | **Ratified**: 2026-04-09 | **Last Amended**: 2026-04-09
