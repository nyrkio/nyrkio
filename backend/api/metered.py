import os
import stripe
import logging
from datetime import datetime, timedelta

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "foo")

logger = logging.getLogger(__file__)


CPU_HOURS_METER = "runner-cpu-hours"
CPU_HOURS_VALUE = "cpu-hours"  # This is the "value" field


def report_cpu_hours_consumed(timestamp, stripe_customer_id, cpu_hours, unique_id):
    if not isinstance(timestamp, datetime):
        logger.error(
            "report_cpu_hours_consumed: Timestamp must be of the format datetime."
        )
        return
    if timestamp < datetime.utcnow() - timedelta(days=30):
        logger.error(f"timestamp was too old:  {timestamp}")
        return

    logger.info(
        "Reporting ec2 consumption to stripe: %s :: %s %s cpu-hours (%s)",
        timestamp,
        stripe_customer_id,
        cpu_hours,
        unique_id,
    )

    cpu_hours_reported = None
    try:
        # Despite the name, this includes the HTTP POST
        cpu_hours_reported = stripe.billing.MeterEvent.create(
            event_name=CPU_HOURS_METER,
            payload={
                CPU_HOURS_VALUE: cpu_hours,
                "stripe_customer_id": stripe_customer_id,
            },
            identifier=unique_id,  # For idempotency
            timestamp=int(timestamp.timestamp()),
        )
    except stripe.InvalidRequestError as e:
        logger.info(
            "Got stripe.InvalidRequestError. This might be harmless / unavoidable, Stripe among other things returns this when I first sent an event once, Stripe told me to fix something, now it complains that an event with the same id exists and I can't change it..."
        )
        logger.warning(e)
    finally:
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


def generate_unique_nyrkio_id(raw_line_item):
    k = raw_line_item["unique_key"]
    return f"{k['nyrkio_unique_id']}_{k['unique_time_slot']}"
