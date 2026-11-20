# Design

```mermaid
flowchart LR
  A[Applicant form] --> R[Requirements engine<br/>rules/term_life.yaml]
  R --> U[Upload docs]
  U --> C[Instant checks]
  C -->|issues| W[Underwriter console]
  C -->|clean| W
  W -->|confirm flags| M[One combined request]
  M -->|outbox - simulated email| T[Applicant tracker]
  T --> U
  W -->|human decision| D[Approve / Decline / Refer]
```

**Statuses:** REQUIREMENTS_PENDING → UNDER_REVIEW → DECIDED
**Key decisions:** rules in YAML (changeable without code); all issues returned together; approval blocked with open issues;
role check on underwriter endpoints; audit log for every action; AI optional, gets issue text only, verified + fallback.
