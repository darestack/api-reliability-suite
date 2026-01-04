import logging
import sys
import structlog
from logging.handlers import RotatingFileHandler
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

  root_logger = logging.getLogger()
  root_logger.setLevel(settings.LOG_LEVEL.upper())

  # 3. Configure standard library logging
  console_handler = logging.StreamHandler(sys.stdout)
  
  # Use structlog's ProcessorFormatter to render the final JSON
  console_formatter = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=shared_processors,
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer(),
    ],
  )
  console_handler.setFormatter(console_formatter)

  # File Handler
  # Rotate after 10MB, keeps last 5 files
  file_handler = RotatingFileHandler("app.json", maxBytes=10*1024*1024, backupCount=5)
  file_formatter = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=shared_processors,
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.JSONRenderer(),
    ],
  )
  file_handler.setFormatter(file_formatter)

  # Add both handlers
  root_logger.handlers = [console_handler, file_handler]