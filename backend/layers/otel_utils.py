from contextlib import contextmanager
from datetime import datetime

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

class OtelTracer(object):
    def __init_tracer__(self, name: str):
        provider = TracerProvider(
            resource=Resource(attributes={
            SERVICE_NAME: "otel-collector"
        }))
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces"))
        provider.add_span_processor(processor)

        # Sets the global default tracer provider
        trace.set_tracer_provider(provider)

        # Creates a tracer from the global tracer provider
        tracer = trace.get_tracer(name)

        return tracer

    def __init__(self, name):
        self.tracer = self.__init_tracer__(name)

    @contextmanager
    def start_trace(self, name):
        with self.tracer.start_as_current_span(name) as current:
            try:
                current.set_attribute("start_time", datetime.now().isoformat())
                yield current

            finally:
                current.set_attribute("end_time", datetime.now().isoformat())