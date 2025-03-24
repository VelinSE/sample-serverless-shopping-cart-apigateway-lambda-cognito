from contextlib import contextmanager
from datetime import datetime

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from fault_injection import ResourceAnomalySimulator
from random import uniform
import psutil

resource = Resource(attributes={SERVICE_NAME: "otel-collector"})

class OtelTracer(object):
    def __init_tracer__(self, name: str):
        provider = TracerProvider(
            resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces"))
        provider.add_span_processor(processor)

        # Sets the global default tracer provider
        trace.set_tracer_provider(provider)

        # Creates a tracer from the global tracer provider
        tracer = trace.get_tracer(name)

        return tracer

    def __init__(self, name):
        self.tracer = self.__init_tracer__(name)
        self.otel_meter = OtelMeter(name)

    @contextmanager
    def start_trace(self, name):
        with self.tracer.start_as_current_span(name) as current:
            try:
                current.set_attribute("start_time", datetime.now().isoformat())

                mem_result = ResourceAnomalySimulator.simulate_high_memory_usage(probability=0.05, duration=uniform(0.05, 1))
                if mem_result > 0:
                    self.otel_meter.add_memory_fault(mem_result)

                cpu_result = ResourceAnomalySimulator.simulate_high_cpu_usage(probability=0.05, duration=uniform(0.05, 1))
                if cpu_result > 0:
                    self.otel_meter.add_cpu_fault(cpu_result)

                yield current

            finally:
                current.set_attribute("end_time", datetime.now().isoformat())

class OtelMeter(object):
    def __init_meter(self, name: str):
        exporter = OTLPMetricExporter(endpoint="http://otel-collector:4318/v1/metrics")
        # exporter = ConsoleMetricExporter()
        metric_reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)
        provider = MeterProvider(metric_readers=[metric_reader], resource=resource)

        # Sets the global default meter provider
        metrics.set_meter_provider(provider)

        # Creates a meter from the global meter provider
        meter = metrics.get_meter(name)

        return meter

    def __init__(self, name: str):
        self.meter = self.__init_meter(name)

        # Create ObservableGauges for CPU and memory usage
        cpu_usage_gauge = self.meter.create_observable_gauge(
            name="cpu_usage",
            description="System CPU usage percentage",
            callbacks=[lambda options: self.__get_cpu_usage_observer()],
            unit="percent"
        )

        memory_usage_gauge = self.meter.create_observable_gauge(
            name="memory_usage",
            description="System memory usage percentage",
            callbacks=[lambda options: self.__get_memory_usage_observer()],
            unit="percent"
        )

        self.memory_fault_counter = self.meter.create_counter(
            name="memory_fault_counter",
            unit="integer",
            description="Counts times the memory fault has been triggered"
        )

        self.cpu_fault_counter = self.meter.create_counter(
            name="cpu_fault_counter",
            unit="integer",
            description="Counts times the cpu fault has been triggered"
        )

    def add_memory_fault(self, allocated_memory):
        self.memory_fault_counter.add(1, { "allocated_memory": allocated_memory})

    def add_cpu_fault(self, allocated_memory):
        self.memory_fault_counter.add(1, { "allocated_memory": allocated_memory})

    def __get_cpu_usage_observer(self):
        """
        Returns CPU usage as a list of (labelset, value) or just a single float.
        psutil.cpu_percent() returns a float representing system-wide CPU
        utilization as a percentage.
        """
        # CPU usage in percent (0.0 - 100.0)
        return [metrics.Observation(psutil.cpu_percent(interval=0.1))]

    def __get_memory_usage_observer(self):
        """
        Returns memory usage as a percentage of total memory.
        psutil.virtual_memory().percent returns the percentage usage.
        """
        # Memory usage in percent
        return [metrics.Observation(psutil.virtual_memory().percent)]
