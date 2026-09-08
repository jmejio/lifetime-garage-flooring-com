---
name: prd-architecture-review
description: Polish PRD documents for sound software architecture by providing interactive recommendations. Reviews solution design, component decomposition, separation of concerns, and architectural decisions to ensure modularity, MVC patterns, and adherence to software development best practices. Presents one improvement recommendation at a time, asking for user agreement, and either implements the change into the PRD or skips it. ALWAYS trigger this skill whenever the user wants to improve a PRD (product requirements document) in markdown or text format by reviewing its architecture, design patterns, modularity, or wants to ensure the proposed solution will support modular, maintainable code structure before implementing.
---

# PRD Architecture Review Skill (Interactive)

## Overview

This skill **polishes PRDs interactively** by identifying and implementing architectural improvements one recommendation at a time. Instead of generating a report, it:

1. **Analyzes** the PRD for architectural soundness
2. **Identifies** improvement opportunities (critical issues, important improvements, suggestions)
3. **Presents** recommendations **one at a time** to the user
4. **Gets agreement** before making changes
5. **Updates** the PRD directly or skips based on user feedback
6. **Continues** until all recommendations have been reviewed

## Architectural Evaluation Criteria

The skill focuses on:

- **Modularity & Component Design** — Are components properly separated and reusable?
- **Separation of Concerns** — Does the architecture follow MVC or layered patterns?
- **Design Patterns** — Are established patterns (factory, observer, adapter, etc.) used appropriately?
- **Scalability & Maintainability** — Will the design support growth and future changes?
- **Implementation Feasibility** — Are decisions clear enough for developers to follow?

## When to Use This Skill

Use this skill when you:
- Have a markdown or text-based PRD ready for architecture improvement
- Want to polish solution designs before implementation
- Need to ensure your architecture follows modularity and separation of concerns principles
- Want interactive guidance on design pattern improvements
- Are converting requirements into implementation issues and want a clean, well-architected PRD

## Interactive Review Workflow

### Phase 1: Initial Analysis

When you share a PRD:

1. **Read the entire PRD** — Understand the feature context, current state, and proposed solution
2. **Identify architectural patterns** — Extract the primary pattern (MVC, layered, microservices, component-based, event-driven, etc.)
3. **Map components/modules** — List major components and their interactions
4. **Scan for issues** — Look for problems across these areas:

**Modularity Assessment:**
- Are component boundaries clear and well-defined?
- Are dependencies between modules explicit and minimal?
- Are components reusable across different contexts?
- Is encapsulation properly applied?

**Separation of Concerns:**
- Is business logic separated from presentation?
- Is persistence logic isolated in a data access layer?
- Are services/controllers properly orchestrating between layers?
- Is there clear, one-directional data flow?

**Design Patterns:**
- What patterns are implicit or explicit in the design?
- Are established patterns (Strategy, Observer, Factory, Adapter, etc.) used appropriately?
- Are anti-patterns present (god objects, circular dependencies, layer skipping, tight coupling)?

**Clarity & Feasibility:**
- Are architectural decisions clear for implementation?
- Are component interactions well-defined?
- Would developers understand how to implement?

### Phase 2: Categorize Recommendations

Organize all findings into priority levels:

**Critical Issues** (must address)
- Circular dependencies between components
- Mixed concerns (business logic in UI, queries in controllers)
- Unclear component boundaries
- Missing abstraction layers
- Implementation ambiguity that blocks developers

**Important Issues** (should address)
- Tight coupling between components
- Potential reusability problems
- Missing or unclear interfaces/contracts
- Scalability concerns for future growth
- Testing difficulties due to design

**Suggestions** (nice to have)
- Alternative patterns that might fit better
- Opportunities for increased modularity
- Performance or maintainability improvements
- Better extensibility for future features

### Phase 3: Present Recommendations Interactively

For **each recommendation** (start with critical, then important, then suggestions):

**1. Present the Issue**
- Clearly state what the concern is
- Explain why it matters to the architecture
- Reference the specific section of the PRD

**2. Suggest the Improvement**
- Propose a specific, concrete change
- Explain the reasoning
- Show the current text and proposed replacement

**3. Show the Impact**
- How does this improve modularity, separation of concerns, or clarity?
- What becomes easier or safer with this change?

**4. Ask for Agreement**
- "Do you agree with this improvement?"
- Offer three options: Yes / No / Ask a clarifying question

**5. Act on Response**
- **If Yes:** Implement the change into the PRD immediately and show the updated section
- **If No:** Skip this recommendation and move to the next one without pushing back
- **If clarifying question:** Answer the question and re-present the recommendation

### Phase 4: Summary and Next Steps

After all recommendations are reviewed:
- Confirm the final state of the PRD
- Offer to make any additional adjustments
- Ask if they're ready to proceed with implementation

## Recommendation Presentation Format

Each recommendation should be presented clearly:

---

**Recommendation #X: [Title of improvement]**

**Priority:** Critical / Important / Suggestion

**Issue:** 
[Clear, concise description of the architectural concern]

**Why it matters:** 
[1-2 sentences on impact to modularity, maintainability, or clarity]

**Current section (from your PRD):**
```
[Show the existing text that needs improvement]
```

**Proposed change:**
```
[Show the suggested replacement or addition]
```

**Impact:**
[How this change improves the architecture]

**Do you agree with this improvement?**
- Yes (I'll implement it)
- No (Skip this recommendation)
- Ask a clarifying question

---

## Common Architectural Anti-Patterns to Watch For

- **God Object** — One class/module doing too much
- **Circular Dependencies** — A depends on B, B depends on A
- **Tight Coupling** — Hard to test or modify one component without others
- **Layer Skipping** — UI calling directly into database, bypassing business logic
- **Missing Abstractions** — Implementation details exposed that should be hidden
- **Unclear Interfaces** — Components interacting in undefined ways
- **Distributed Monolith** — Multiple services tightly coupled to one another
- **Mixed Concerns** — Business logic mixed with presentation or persistence

## Design Patterns to Look For

**Structural Patterns:**
- Adapter — Convert incompatible interfaces
- Facade — Simplify complex subsystems
- Proxy — Control access to another object
- Decorator — Add behavior dynamically

**Behavioral Patterns:**
- Observer/Pub-Sub — Decouple event producers from consumers
- Strategy — Select algorithms at runtime
- Factory — Create objects without specifying classes
- Command — Encapsulate requests as objects

**Creational Patterns:**
- Singleton — Single instance across app
- Builder — Construct complex objects step-by-step
- Dependency Injection — Invert control of dependencies

**Architectural Patterns:**
- MVC — Model-View-Controller separation
- Layered Architecture — Clear separation of concerns
- Microservices — Independent, loosely coupled services
- Event-Driven — Services communicate via events

## Layers in MVC/Layered Architecture

**Presentation/View Layer:**
- Focused solely on displaying data and capturing user input
- No business logic embedded in UI code
- Responsibilities: user interaction, data formatting for display, event handling

**Business Logic/Model Layer:**
- Business logic independent of presentation or persistence
- Clear data structures and validation rules
- Responsibilities: data integrity, business rules enforcement, domain logic

**Service/Controller Layer:**
- Orchestrates between Model and Presentation layers
- Handles requests, validates input, coordinates responses
- Responsibilities: request routing, state management, coordination, transactions

**Data Access/Persistence Layer:**
- All database/storage logic isolated here
- Abstract behind consistent interfaces (repository, DAO)
- Responsibilities: CRUD operations, data transformation, query execution

## Tips for Effective PRD Polishing

- **Read the full PRD first** — Understand context before suggesting changes
- **Look for implicit architecture** — Design patterns aren't always named explicitly
- **Be specific with examples** — Show exactly what text to change and what it becomes
- **Explain rationale** — Help user understand why the change improves architecture
- **Respect user decisions** — If they decline a recommendation, move on gracefully
- **Build on accepted changes** — Some recommendations may become relevant after others are accepted
- **Consider the tech stack** — Tailor recommendations to web, mobile, backend, or hybrid contexts
- **Flag vague language** — If implementation clarity is missing, address it