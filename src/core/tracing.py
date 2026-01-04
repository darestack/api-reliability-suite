from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def configure_tracing(app):
  # 1. Define the resouce
  resource = Resource.create({SERVICE_NAME: "api-reliability-suite"})

  # 2. Create a TracerProvider
  provider = TracerProvider(resource=resource)

  # 3. Add a processor + exporter (prints span to console for learning)
  processor = BatchSpanProcessor(ConsoleSpanExporter())
  provider.add_span_processor(processor)

  # 4. Set this provider as the global default
  trace.set_tracer_provider(provider)

  # 5. Auto-instrument FastAPI 
  FastAPIInstrumentor.instrument_app(app)