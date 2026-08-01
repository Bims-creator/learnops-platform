from prometheus_client import Counter

EVENTS_INGESTED = Counter("learnops_events_ingested_total", "Learning events accepted by ingest-api")
