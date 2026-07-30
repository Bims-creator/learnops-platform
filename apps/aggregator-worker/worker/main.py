import json
import logging

from prometheus_client import Counter, start_http_server

from worker.db import get_connection, init_db, upsert_event
from worker.redis_client import EVENTS_QUEUE_KEY, client as redis_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("aggregator-worker")

EVENTS_PROCESSED = Counter("learnops_events_processed_total", "Learning events processed")
EVENTS_FAILED = Counter("learnops_events_failed_total", "Learning events that failed processing")


def main():
    start_http_server(9000)
    log.info("Metrics server listening on :9000/metrics")

    conn = get_connection()
    init_db(conn)
    log.info("Connected to Postgres, table ensured")

    log.info("Waiting for events on Redis list '%s'...", EVENTS_QUEUE_KEY)
    while True:
        _, raw = redis_client.blpop(EVENTS_QUEUE_KEY)
        try:
            event = json.loads(raw)
            upsert_event(conn, event)
            EVENTS_PROCESSED.inc()
            log.info("Processed event for student_id=%s", event["student_id"])
        except Exception:
            EVENTS_FAILED.inc()
            log.exception("Failed to process event: %s", raw)


if __name__ == "__main__":
    main()
