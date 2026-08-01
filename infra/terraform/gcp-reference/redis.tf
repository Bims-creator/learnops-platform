# Memorystore is the lift-and-shift equivalent of the redis.yaml Deployment -
# same queue semantics, minimal app changes beyond pointing REDIS_URL at it.
#
# A more idiomatic GCP-native redesign would replace the Redis list-based
# queue with Pub/Sub instead: durable, at-least-once delivery, no capacity
# planning for queue depth. That's a bigger app-level change than this
# migration scopes for - noted here as a real future option, not implemented,
# in the spirit of pragmatism over a rewrite.

resource "google_redis_instance" "learnops" {
  name           = "learnops-${var.environment}"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region

  authorized_network = google_compute_network.vpc.id
  redis_version       = "REDIS_7_2"
}
