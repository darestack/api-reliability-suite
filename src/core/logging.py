import logging
import structlog
import sys
from src.core.config import settings

def configure_logging():
  # 1. Define shared processors (used by both structlog and stdlib)
  shared_processors = [
    structlog.contextvars.merge_contextvars, # Add global context
    structlog.processors.add_log_level,      # Add log level
    structlog.processors.TimeStamper(fmt="iso"), # Add timestamp
  ]

  # 2. Configure structlog defaults
  structlog.configure(
    processors=shared_processors + [
        # Prepare event dict for stdlib formatting instead of rendering to JSON here
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
  )

  # 3. Configure standard library logging
  handler = logging.StreamHandler(sys.stdout)
  
  # Use structlog's ProcessorFormatter to render the final JSON
  formatter = structlog.stdlib.ProcessorFormatter(
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.JSONRenderer(),
    ],
    foreign_pre_chain=shared_processors,
  )
  handler.setFormatter(formatter)

  root_logger = logging.getLogger()
  # Avoid adding duplicate handlers (e.g. on reload)
  # Ideally check if handler of this type exists, but for now simple check:
  found = False
  for h in root_logger.handlers:
      if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout:
          # Assuming it's our handler or similar
           h.setFormatter(formatter) # Update formatter just in case
           found = True
           break
  
  if not found:
      root_logger.addHandler(handler)
  
  root_logger.setLevel(settings.LOG_LEVEL.upper())