import pybreaker
from prometheus_client import Gauge
import structlog

logger = structlog.get_logger()

# Define Prometheus metrics for Circuit Breaker
circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "State of the circuit breaker (0: Closed, 1: Open, 2: Half-Open)",
    ["name"],
)


class PrometheusListener(pybreaker.CircuitBreakerListener):
    """
    Listener that updates Prometheus metrics when circuit breaker state changes.
    """

    def state_change(self, cb, old_state, new_state):
        state_value = 0
        if new_state.name == "open":
            state_value = 1
        elif new_state.name == "half-open":
            state_value = 2

        circuit_breaker_state.labels(name=cb.name).set(state_value)
        logger.info(
            "circuit_breaker_state_change",
            name=cb.name,
            old_state=old_state.name,
            new_state=new_state.name,
        )


# Initialize the Circuit Breaker
# Trips if 5 failures occur
external_api_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    listeners=[PrometheusListener()],
    name="external_api_breaker",
)
