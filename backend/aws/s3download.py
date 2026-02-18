import csv
import io
import json
import gzip
import logging
import boto3
from datetime import datetime
from bson.objectid import ObjectId
from backend.db.db import DBStore

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


async def get_latest_runner_usage(seen_previously=None):
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

    r = []

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
        r = []

        for row in filtered:
            cost_category = row[column["cost_category"]]
            nyrkio_user_dict = json.loads(cost_category)
            billable_user_id = nyrkio_user_dict.get(
                "by_nyrkio_user", "000000000000000000000000"
            )

            plan_info = None
            if billable_user_id == "000000000000000000000000":
                # Not a real user, skip database queries
                plan_info = {
                    "stripe_customer_id": None,
                    "nyrkio_org_id": None,
                    "nyrkio_user_id": billable_user_id,
                    "billable_user_id": billable_user_id,
                    "email": "internal use",
                    "plan": "internal",
                    "type": "internal",
                }
            else:
                # In general the billable nyrkio user will always have a user.billable subscription active
                # It will be checked before they can launch any cloud resource in the first place. But...
                # there will be glitches, so let's not assume anything.
                plan_info = (
                    await get_user_info(billable_user_id) if billable_user_id else None
                )
                if not plan_info:
                    logger.debug(
                        "get_latest_runner_usage: billable_user_id is None, next row"
                    )
                    continue

            logger.debug(plan_info)
            nyrkio_user_id = plan_info.get("nyrkio_user_id", billable_user_id)

            parts = str(latest_csv_obj.key).split("/")
            date_part = parts[4].split("Z-")[0]  # TODO: python 3.11 supports Z
            aws_timestamp = datetime.fromisoformat(date_part)

            # r = _ensure_buckets(raw, nyrkio_user_id)

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
                "product_instance_type",
            ]

            get_values = ["pricing_public_on_demand_cost", "line_item_usage_amount"]

            meta = dict((k, json.loads(row[column[k]])) for k in get_meta)
            labels = dict([(k, row[column[k]]) for k in get_labels])
            values = dict([(k, row[column[k]]) for k in get_values])
            aws_idempotent = (
                labels["line_item_usage_start_date"],
                labels["line_item_usage_end_date"],
                labels["identity_line_item_id"],
            )
            # aws_idempotent_str = (
            #     str(labels["line_item_usage_start_date"])
            #     + str(labels["line_item_usage_end_date"])
            #     + str(labels["identity_line_item_id"])
            # )

            # raw lineitems, we probably use this with Stripe
            r.append(
                {
                    "unique_key": {
                        "nyrkio_unique_id": meta["resource_tags"].get(
                            "user_nyrkio_unique_id",
                            labels["identity_line_item_id"],  # Fallback
                        ),
                        "unique_time_slot": labels["line_item_usage_start_date"],
                        "unique_time_slot_end": labels["line_item_usage_end_date"],
                    },
                    # Just for the record then
                    "additional_unique_keys": {
                        "aws_idempotent": aws_idempotent,
                        "identity_line_item_id": labels["identity_line_item_id"],
                    },
                    "user": {
                        "billable_nyrkio_user_id": nyrkio_user_id,
                        "nyrkio_user": meta["resource_tags"].get("nyrkio_user"),
                        "nyrkio_org": meta["resource_tags"].get("nyrkio_org"),
                        "stripe_customer_id": plan_info["stripe_customer_id"],
                        "user_email": plan_info["email"],
                    },
                    "plan_info": plan_info,
                    "consumption": {
                        "nyrkio_cpu_hours": float(values["line_item_usage_amount"])
                        * float(meta["product"].get("vcpu", 0)),
                        "hours": float(values["line_item_usage_amount"]),
                        "aws_cost": float(values["pricing_public_on_demand_cost"]),
                        "vcpu": float(meta["product"].get("vcpu", 0)),
                    },
                    # Link back to githubbillable_user_id workflow, and other meta data
                    "github": {
                        "github_event_id": meta["resource_tags"].get(
                            "user_github_event_id"
                        ),
                        "github_job_html_url": meta["resource_tags"].get(
                            "user_github_job_html_url"
                        ),
                        "github_job_id": meta["resource_tags"].get(
                            "user_github_job_id"
                        ),
                        "github_job_run_id": meta["resource_tags"].get(
                            "user_github_job_run_id",
                            meta["resource_tags"].get("github_job_run_id"),
                        ),
                        "github_job_run_attempt": meta["resource_tags"].get(
                            "user_github_job_run_attempt",
                            meta["resource_tags"].get("github_job_run_attempt"),
                        ),
                        "user_launched_at": meta["resource_tags"].get(
                            "user_launched_at"
                        ),
                    },
                    "report": latest_csv_obj.key,
                    "report_aws_timestamp": aws_timestamp.isoformat(),
                }
            )
        # Exit at the end of the loop that corresponds to a single ec2 report
        # In an earlier version this was to keep MongoDB docs below 16 MB, now it's more to keep this computation small
        return r, latest_csv_obj.key

    return r, latest_report


plan_type = {
    "runner_postpaid_10": "stripe_meter",
    "runner_prepaid_100": "stripe_meter",
    "simple_enterprise_monthly": "nyrkio_meter",
    "simple_enterprise_yearly": "nyrkio_meter",
    "simple_business_monthly": "nyrkio_meter",
    "simple_business_yearly": "nyrkio_meter",
}


async def get_user_info(billable_user_id):
    db = DBStore()
    db_user_id = None
    org_id = None

    # fix: On 2026-02-16 we used entire User object as the AWS tag. If this is the full object, then we just want the user_id
    garbage = "{'_id': ObjectId('"
    if isinstance(billable_user_id, str) and billable_user_id.startswith(garbage):
        save_id = billable_user_id[len(garbage) :]
        billable_user_id = save_id[: len("65cb6070382a77fd520899de")]

    if isinstance(billable_user_id, dict):
        if "_id" in billable_user_id:
            billable_user_id = billable_user_id["_id"]

    # user or org
    if len(billable_user_id) > 20:
        db_user_id = (
            billable_user_id
            if isinstance(billable_user_id, ObjectId)
            else ObjectId(billable_user_id)
        )
    else:
        org_id = (
            billable_user_id
            if isinstance(billable_user_id, int)
            else int(billable_user_id)
        )
        config, _ = await db.get_user_config(org_id)
        plan = config.get("billing_runners", {})
        db_user_id = plan.get("paid_by", None)

    if not db_user_id:
        logger.error(
            f"Couldn't find a meaningful billable nyrkio user for {billable_user_id} {db_user_id}"
        )
        return None

    user = await db.get_user_without_any_fastapi_nonsense(db_user_id)
    if not user:
        logger.error(f"User {billable_user_id} {db_user_id} NOT FOUND in database")
        return None
    email = user["email"]
    plan = user.get("billing_runners")
    if plan is None:
        if user.get("billing"):
            plan = user.get("billing")

    if plan is None:
        logger.error(
            f"Did not find billing info for {billable_user_id} ({db_user_id} {email})"
        )
        return None

    return {
        "stripe_customer_id": plan["customer_id"],
        "nyrkio_org_id": org_id,
        "nyrkio_user_id": db_user_id,
        "billable_user_id": billable_user_id,
        "email": email,
        "plan": plan["plan"],
        "type": plan_type[plan["plan"]],
    }
