import csv
import io
import json
import gzip
import logging
import boto3
from datetime import datetime


logger = logging.getLogger(__file__)


def check_for_new_usage_report(seen_previously):
    s3client = boto3.resource("s3")
    bucket_name = "nyrkiorunnersusage"
    bucket = s3client.Bucket(bucket_name)

    runner_usage_reports = list(
        filter(
            lambda o: o.key.endswith("/NyrkioRunnersByUser-00001.csv.gz"),
            bucket.objects.all(),
        )
    )
    runner_usage_reports.sort(key=lambda o: o.key)
    for r in runner_usage_reports:
        if r.key == seen_previously:
            remaining_are_new = True
            continue
        if remaining_are_new:
            return True
    return False


def get_latest_runner_usage(seen_previously=None):
    s3client = boto3.resource("s3")
    bucket_name = "nyrkiorunnersusage"
    bucket = s3client.Bucket(bucket_name)
    logger.info(str(bucket))
    # The filenames are like this
    # NyrkioRunnersUsageDaily/NyrkioRunnersByUser/data/BILLING_PERIOD=2025-12/2025-12-28T13:14:37.728Z-8c5a76cc-57d0-437d-851b-064e27aa8b06/NyrkioRunnersByUser-00001.csv.gz
    runner_usage_reports = list(
        filter(
            lambda o: o.key.endswith("/NyrkioRunnersByUser-00001.csv.gz"),
            bucket.objects.all(),
        )
    )
    if seen_previously:
        runner_usage_reports = list(
            filter(
                lambda s: s.key > seen_previously,
                runner_usage_reports,
            )
        )
    # print(runner_usage_reports)
    runner_usage_reports.sort(key=lambda o: o.key)
    logger.debug(str(runner_usage_reports))
    latest_report = (
        str(runner_usage_reports[-1].key) if runner_usage_reports else seen_previously
    )

    pivot = {}
    raw = {}
    logger.debug(str(runner_usage_reports))
    for latest_csv_obj in runner_usage_reports:
        # print(latest_csv_obj)

        # Download a csv file
        buf = io.BytesIO()
        obj = bucket.Object(latest_csv_obj.key)
        obj.download_fileobj(buf)
        buf.seek(0)
        csv_text = gzip.decompress(buf.read()).decode("utf-8")
        csv_buf = io.StringIO(csv_text)
        # print(csv_text)
        csv_data = csv.reader(csv_buf, delimiter=",", quotechar='"')
        # print(csv_data)
        column = {}
        filtered = []
        for row in csv_data:
            if not column:
                # first row
                for col in row:
                    column = dict((row[i], i) for i in range(len(row)))
                continue
            if row[column["line_item_usage_account_name"]] != "nyrkio-gh-runners":
                continue
            if row[column["line_item_product_code"]] != "AmazonEC2":
                continue
            if row[column["pricing_unit"]] != "Hrs":
                continue
            filtered.append(row)

        filtered.sort(key=lambda r: r[column["line_item_usage_start_date"]])
        for row in filtered:
            cost_category = row[column["cost_category"]]
            nyrkio_user_dict = json.loads(cost_category)
            nyrkio_user_id = nyrkio_user_dict.get(
                "by_nyrkio_user", "000000000000000000000000"
            )

            parts = str(latest_csv_obj.key).split("/")
            aws_timestamp = datetime.fromisoformat(parts[4])
            d, m, r = _ensure_buckets(pivot, raw, nyrkio_user_id, aws_timestamp)

            get_meta = ["resource_tags", "product"]
            get_labels = [
                "product_servicecode",
                "product_region_code",
                "product_usagetype",
                "line_item_usage_type",
                "line_item_usage_start_date",
                "identity_line_item_id",
                "identity_time_interval",
                "line_item_usage_end_date",
                "line_item_usage_start_date",
                "pricing_currency",
                "pricing_unit",
            ]
            # coming_soon = [
            # "cpus",
            # "nyrkio_price_per_hour",
            # "ec2_instance_type",
            # "nyrkio_instance_type",
            # "nyrkio_unique_id",
            # ]
            get_values = ["pricing_public_on_demand_cost", "line_item_usage_amount"]

            meta = dict((k, json.loads(row[column[k]])) for k in get_meta)
            labels = dict([(k, row[column[k]]) for k in get_labels])
            values = dict([(k, row[column[k]]) for k in get_values])
            aws_idempotent = (
                labels["line_item_usage_start_date"],
                labels["line_item_usage_end_date"],
                labels["identity_line_item_id"],
            )
            aws_idempotent_str = (
                str(labels["line_item_usage_start_date"])
                + str(labels["line_item_usage_end_date"])
                + str(labels["identity_line_item_id"])
            )

            d[labels["pricing_unit"]] = d.get(labels["pricing_unit"], 0.0) + float(
                values["line_item_usage_amount"]
            )
            d[labels["pricing_currency"]] = d.get(
                labels["pricing_currency"], 0.0
            ) + float(values["pricing_public_on_demand_cost"])
            d["count"] = d.get("count", 0) + 1
            d[aws_idempotent] = d.get(aws_idempotent, 0) + 1
            d["meta"] = d.get("meta", {}) + [meta]
            d["labels"] = d.get("labels", {}) + [labels]

            m[labels["pricing_unit"]] = m.get(labels["pricing_unit"], 0.0) + float(
                values["line_item_usage_amount"]
            )
            m[labels["pricing_currency"]] = m.get(
                labels["pricing_currency"], 0.0
            ) + float(values["pricing_public_on_demand_cost"])
            m["count"] = m.get("count", 0) + 1
            m[aws_idempotent_str] = m.get(aws_idempotent, 0) + 1
            m["meta"] = m.get("meta", {}) + [meta]
            m["labels"] = m.get("labels", {}) + [labels]

    return pivot, latest_report


def _ensure_buckets(pivot, raw, user_id, timestamp):
    daily_bucket = datetime.strftime("%Y%m%d")
    monthly_bucket = datetime.strftime("%Y%m")
    # print(user_id)
    if user_id not in pivot:
        pivot[user_id] = {"daily": {}, "monthly": {}}
    if daily_bucket not in pivot[user_id]["daily"][daily_bucket]:
        pivot[user_id]["daily"][daily_bucket] = {}
    if monthly_bucket not in pivot[user_id]["monthly"][monthly_bucket]:
        pivot[user_id]["monthly"][monthly_bucket] = {}

    dobj = pivot[user_id]["daily"][daily_bucket]
    mobj = pivot[user_id]["monthly"][monthly_bucket]

    if user_id not in raw:
        raw[user_id] = {}

    return dobj, mobj, raw


# if __name__ == "__main__":
#     print(json.dumps(get_latest_runner_usage(), indent=4, sort_keys=True))
