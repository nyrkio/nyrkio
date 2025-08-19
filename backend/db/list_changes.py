from typing import Any

from bson.objectid import ObjectId
from datetime import datetime

from backend.db.db import DBStore


async def change_points_per_commit(
    user_or_org_id: Any, test_name_prefix: str, commit: str = None
):
    store = DBStore()
    db = store.db

    config, meta = await store.get_user_config(user_or_org_id)

    # the match is not on arbitrary prefix, rather only on full "parts", that is,
    # # if this was a path to something then each part is a directory name.
    # if test_name_prefix != "" and test_name_prefix[-1] != "/":
    #     test_name_prefix += "/"
    # if test_name_prefix == "/":
    #     test_name_prefix = ""
    if test_name_prefix != "" and test_name_prefix[-1] == "/":
        test_name_prefix = test_name_prefix[:-1]

    query = _set_parameters(user_or_org_id, test_name_prefix, meta, config, commit)
    # print(query)
    docs = await db.change_points.aggregate(query).to_list(None)
    # print(docs)
    return docs


def _set_parameters(user_or_org_id, test_name_prefix, meta, config, commit=None):
    uid = user_or_org_id
    if isinstance(user_or_org_id, str):
        uid = ObjectId(user_or_org_id)

    CHANGE_POINTS_PER_COMMIT = [
        {
            "$match": {
                "_id.user_id": uid,
                "_id.test_name": {"$regex": f"^{test_name_prefix}(/.*)?$"},
                "_id.max_pvalue": config.get("core", {}).get("max_pvalue", 0.001),
                "_id.min_magnitude": config.get("core", {}).get("min_magnitude", 0.05),
                "meta.change_points_timestamp": {
                    "$gte": meta.get("change_points_timestamp", datetime(1970, 1, 1)),
                },
            },
        },
        {
            "$addFields": {
                "cp": {
                    "$objectToArray": "$change_points",
                },
                "test_name": "$_id.test_name",
            },
        },
        {
            "$unwind": "$cp",
        },
        {
            "$addFields": {
                "cp2": {
                    "$objectToArray": "$cp.v.change_points",
                },
                "data": {
                    "$objectToArray": "$cp.v.data",
                },
            },
        },
        {
            "$unwind": "$cp2",
        },
        {
            "$match": {
                "cp2.v.0": {
                    "$exists": 1,
                },
            },
        },
        {
            "$unwind": "$cp2.v",
        },
        {
            "$unwind": "$data",
        },
        {
            "$project": {
                "_id": True,
                "meta": True,
                "commit": {
                    "$arrayElemAt": [
                        "$cp.v.attributes.git_commit",
                        "$cp2.v.index",
                    ],
                },
                "repo": {
                    "$arrayElemAt": [
                        "$cp.v.attributes.git_repo",
                        "$cp2.v.index",
                    ],
                },
                "branch": {
                    "$arrayElemAt": [
                        "$cp.v.attributes.branch",
                        "$cp2.v.index",
                    ],
                },
                "time": {
                    "$arrayElemAt": [
                        "$cp.v.time",
                        "$cp2.v.index",
                    ],
                },
                "data_value": {
                    "$arrayElemAt": [
                        "$data.v",
                        "$cp2.v.index",
                    ],
                },
                "metric_name": "$cp2.v.metric",
                "metric_name_control": "$cp2.k",
                "direction": "$metrics.direction",
                "unit": "$metrics.unit",
                "test_name": "$test_name",
                "cp_values": "$cp2.v",
            },
        },
        {
            "$group": {
                "_id": {
                    "git_commit": "$commit",
                    "user_id": {
                        "$toString": "$_id.user_id",
                    },
                    "max_pvalue": "$_id.max_pvalue",
                    "min_magnitude": "$_id.min_magnitude",
                    "test_name": "$test_name",
                },
                "time": {
                    "$last": "$time",
                },
                "time_min": {
                    "$min": "$time",
                },
                "time_max": {
                    "$max": "$time",
                },
                "metric_name": {
                    "$push": "$metric_name",
                },
                "metric_name_control": {
                    "$push": "$metric_name_control",
                },
                "direction": {
                    "$last": "$direction",
                },
                "unit": {
                    "$last": "$unit",
                },
                "git_repo": {
                    "$last": "$repo",
                },
                "branch": {
                    "$last": "$branch",
                },
                "data_value": {
                    "$push": "$data_value",
                },
                "cp_values": {
                    "$push": "$cp_values",
                },
                "change_points_timestamp": {
                    "$max": "$meta.change_points_timestamp",
                },
                "commitObjects": {
                    "$push": "$commitObjects",
                },
            },
        },
        {
            "$project": {
                "_id": True,
                "time": True,
                "time_min_max": ["$time_min", "$time_max"],
                "test_name": "$_id.test_name",
                "attributes": {
                    "git_repo": "$git_repo",
                    "test_name": "$_id.test_name",
                    "branch": "$branch",
                },
                "metric": {
                    "_name_control": "$metric_name_control",
                    "name": "$metric_name",
                    "unit": "(omitted)",
                    "value": "$data_value",
                    "direction": "$direction",
                },
                "cp_values": "$cp_values",
                "meta": {
                    "change_points_timestamp": "$change_points_timestamp",
                },
            },
        },
        {
            "$sort": {
                "time": -1,
                "_id.git_commit": 1,
                "test_name": 1,
            }
        },
    ]

    query = CHANGE_POINTS_PER_COMMIT
    if commit is not None:
        query.append({"$match": {"$_id.commit": commit}})
    return query
