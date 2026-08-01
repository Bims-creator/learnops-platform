resource "google_logging_metric" "event_processing_failures" {
  name   = "learnops_event_processing_failures"
  filter = "resource.type=\"k8s_container\" AND resource.labels.namespace_name=\"learnops\" AND resource.labels.container_name=\"aggregator-worker\" AND textPayload:\"Failed to process event\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "learnops-platform-alerts"
  type         = "email"
  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_alert_policy" "event_processing_failures" {
  display_name = "LearnOps: event processing failures"
  combiner      = "OR"

  conditions {
    display_name = "Event processing failures > 0"
    condition_threshold {
      filter          = "resource.type=\"k8s_container\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.event_processing_failures.name}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "300s"
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}
