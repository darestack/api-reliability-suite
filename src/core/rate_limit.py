from slowapi import Limiter
from slowapi.util import get_remote_address

# The Limiter
# - get_remote_address: Uses the client's IP to track limits.
# - default_limits: Can be set globally, but we'll apply them per-route for flexibility.
limiter = Limiter(key_func=get_remote_address)