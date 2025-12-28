import csv
import io
import json
import gzip
import logging
import boto3


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
    runner_usage_reports = list(
        filter(
            lambda o: o.key.endswith("/NyrkioRunnersByUser-00001.csv.gz"),
            bucket.objects.all(),
        )
    )
    # print(runner_usage_reports)
    runner_usage_reports.sort(key=lambda o: o.key)
    logger.info(str(runner_usage_reports))
    latest_report = runner_usage_reports[-1] if runner_usage_reports else None
    if seen_previously:
        temp = []
        start_collecting = False
        for r in runner_usage_reports:
            if r.key == seen_previously:
                start_collecting = True
                continue
            if start_collecting:
                temp.append(r)
                latest_report = r.key

        runner_usage_reports = temp

    pivot = {}
    logger.info(str(runner_usage_reports))
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
        for row in csv_data:
            if not column:
                # first row
                for col in row:
                    column = dict((row[i], i) for i in range(len(row)))
                continue

            cost_category = row[column["cost_category"]]
            nyrkio_user_dict = json.loads(cost_category)
            nyrkio_user_id = nyrkio_user_dict.get(
                "by_nyrkio_user", "000000000000000000000000"
            )
            # print(nyrkio_user_id)
            if nyrkio_user_id not in pivot:
                pivot[nyrkio_user_id] = {}
            if row[column["product_servicecode"]] not in pivot[nyrkio_user_id]:
                pivot[nyrkio_user_id][row[column["product_servicecode"]]] = 0.0

            pivot[nyrkio_user_id][row[column["product_servicecode"]]] += float(
                row[column["pricing_public_on_demand_cost"]]
            )

    return pivot, latest_report


# if __name__ == "__main__":
#     print(json.dumps(get_latest_runner_usage(), indent=4, sort_keys=True))
