from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from src.core.config import settings


def configure_tracing(app):
  """
  In production, we send traces (spans) to a central collector (OTLP).
  In development, we just print them to the console for easy debugging.
  """
  # 1. Choose the exporter based on settings
  if settings.OTLP_ENDPOINT:
    # Production: Send to a real collector (Jaeger/Tempo/Honeycomb)
    exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT)
  else:
    # Development: Just print to terminal
    exporter = ConsoleSpanExporter()

  # 2. Define the resource (identifies this service in the dashboard)
  resource = Resource.create({SERVICE_NAME: settings.PROJECT_NAME})

  # 3. Create a TracerProvider
  provider = TracerProvider(resource=resource)

  # 4. Add a processor using the chosen exporter
  processor = BatchSpanProcessor(exporter)
  provider.add_span_processor(processor)

  # 5. Set this provider as the global default
  trace.set_tracer_provider(provider)

  # 6. Auto-instrument FastAPI
  FastAPIInstrumentor.instrument_app(app)