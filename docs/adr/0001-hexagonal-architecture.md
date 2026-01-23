# 1. Use Hexagonal Architecture (Ports and Adapters)

Date: 2026-01-22

## Status

Accepted

## Context

We are building a high-reliability API that needs to be:

1.  **Testable**: Business logic should be testable without spinning up Docker or databases.
2.  **Flexible**: We may need to swap providers (e.g., switch OpenAI for Groq) without rewriting the core application.
3.  **Maintainable**: Clear separation of concerns is required to prevent "Spaghetti Code."

Traditional "Layered Architecture" (Controller -> Service -> Repository) often leads to tight coupling where the Service layer knows too much about the database or HTTP implementations.

## Decision

We will adopt **Hexagonal Architecture** (also known as Ports and Adapters).

*   **The Domain (Core)**: Pure Python code. Contains `src/domain` (Models) and `src/services` (Business Rules). It has NO dependencies on `fastapi`, `sqlmodel`, or external libraries.
*   **Ports (Interfaces)**: Abstract Base Classes defined in the Core that describe *what* needs to be done (e.g., `UserRepositoryProtocol`).
*   **Adapters (Infrastructure)**: Concrete implementations that "plug in" to the ports (e.g., `SQLUserRepository`, `FastAPIController`).

## Consequences

### Positive
*   **Isolation**: We can test the Core with 100% coverage using simple Mocks/Fakes, running in milliseconds.
*   **Swap-ability**: Changing the LLM provider is as simple as writing a new Adapter class.
*   **Clarity**: It is obvious where business rules live vs. where infrastructure code lives.

### Negative
*   **Boilerplate**: Requires defining Interfaces/Protocols (`ABC`) before writing implementation.
*   **Complexity**: Slightly higher learning curve for junior developers compared to simple MVC.
