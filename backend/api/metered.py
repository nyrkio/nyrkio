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
def query_meter_consumption(stripe_customer_id):
    # now = datetime.utcnow()

    # Get subscription
    #     subscription = stripe.Subscription.retrieve(subscription_id)
    #     items = [item["id"] for item in subscription["items"]["data"]]
    #     usage = []
    #     meters = []
    #     for item in items:
    #         if item["price"]["recurring"]["usage_type"] == "metered":
    #             usage.append(item)
    #
    #             meter_id = item["plan"]["meter"]
    #             m = stripe.billing.Meter(meter_id)
    #     .list_event_summaries(
    #     "mtr_test_61Q8nQMqIFK9fRQmr41CMAXJrFdZ5MnA",
    #     customer="cus_Pp40waj64hdRxb",
    #     start_time=1711584000,
    #     end_time=1711666800,
    #     value_grouping_window="hour",
    #     )
    m = stripe.billing.Meter("mtr_61TtBEvjlAsWJr0H041DIPO697lkhTY8")
    daily = m.list_event_summaries(
        "mtr_61TtBEvjlAsWJr0H041DIPO697lkhTY8",
        customer=stripe_customer_id,
        start_time=int(datetime(2025, 1, 1).timestamp()),
        end_time=int(datetime(2026, 12, 31).timestamp()),
        value_grouping_window="day",
    )
    return daily
    # return usage, meters
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
