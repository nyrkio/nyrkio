import os
import stripe
import logging
from datetime import datetime, timedelta

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "foo")

logger = logging.getLogger(__file__)


CPU_HOURS_METER = "runner-cpu-hours"


def report_cpu_hours_consumed(stripe_customer_id, cpu_hours, unique_id):
    logger.info(
        "Reporting ec2 consumption to stripe: %s %s cpu-hours (%s)",
        stripe_customer_id,
        cpu_hours,
        unique_id,
    )
    # Despite the name, this includes the HTTP POST
    cpu_hours_reported = stripe.billing.MeterEvent.create(
        event_name=CPU_HOURS_METER,
        payload={"value": cpu_hours, "stripe_customer_id": stripe_customer_id},
        identifier=unique_id,  # For idempotency
    )
    logger.debug(cpu_hours_reported)


def query_meter_consumption(stripe_customer_id):
    now = datetime.utcnow()
    return stripe.billing.Analytics.MeterUsage.list(
        customer=stripe_customer_id,
        meters=[CPU_HOURS_METER],
        value_grouping_window="month",  # Options: day, week, month, quarter, year
        time_range={
            "gte": (now - timedelta(months=15)).isoformat(),
            "lte": now.isoformat(),
        },
    )
