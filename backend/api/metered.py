import os
import stripe
import logging
from datetime import datetime, timedelta, timezone

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
    if timestamp < datetime.now(timezone.utc) - timedelta(days=30):
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
            "Got stripe.InvalidRequestError. This might be harmless / unavoidable in small quantities?"
        )
        logger.warning(e)
    finally:
        logger.debug(cpu_hours_reported)


# def query_meter_consumption(stripe_customer_id, subscription_id):
def query_meter_consumption(subscription_id):
    # now = datetime.utcnow()

    # Get subscription
    subscription = stripe.Subscription.retrieve(subscription_id)
    items = [item["id"] for item in subscription["items"]["data"]]
    usage = []
    for item in items:
        data = stripe.SubscriptionItem.list_usage_record_summaries(item)
        usage.append(data)

        for record in data:
            print(f"Period: {record.period.start} to {record.period.end}")
            print(f"Usage: {record.total_usage}")
            print("---")

    from pprint import pprint

    pprint(usage)
    pprint(items)
    return usage
    # usage_data = stripe.billing.Analytics.MeterUsage.list(
    #     customer="cus_123456789",
    #     meters=["your_meter_name"],
    #     value_grouping_window="day",  # See daily growth
    #     time_range={
    #         "gt": int(start_of_month),
    #         "lte": now
    #     }
    # )
    #
    # # Print daily usage
    # for day in usage_data.data:
    #     print(f"Date: {day.window_start}")
    #     print(f"Usage: {day.total_value}")

    # stripe.Balance.retrieve(
    #     customer=stripe_customer_id,
    #     meters=[CPU_HOURS_METER],
    #     value_grouping_window="month",  # Options: day, week, month, quarter, year
    #     time_range={
    #         "gte": (now - timedelta(months=15)).timestamp(),
    #         "lte": now.timestamp(),
    #     },
    # )

    # return stripe.billing.Analytics.MeterUsage.list(
    #     customer=stripe_customer_id,
    #     meters=[CPU_HOURS_METER],
    #     value_grouping_window="month",  # Options: day, week, month, quarter, year
    #     time_range={
    #         "gte": (now - timedelta(months=15)).timestamp(),
    #         "lte": now.timestamp(),
    #     },
    # )


def generate_unique_nyrkio_id(raw_line_item):
    k = raw_line_item["unique_key"]
    return f"{k['nyrkio_unique_id']}_{k['unique_time_slot']}"
