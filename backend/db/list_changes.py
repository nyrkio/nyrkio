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
    # if this was a path to something then each part is a directory name.
    if test_name_prefix[-1] != "/":
        test_name_prefix += "/"

    query = _set_parameters(user_or_org_id, test_name_prefix, meta, config, commit)
    print(query)
    docs = await db.change_points.aggregate(query).to_list(None)
    print(docs)
    return docs


def _set_parameters(user_or_org_id, test_name_prefix, meta, config, commit=None):
    uid = user_or_org_id
    if isinstance(user_or_org_id, str):
        uid = ObjectId(user_or_org_id)

    CHANGE_POINTS_PER_COMMIT = [
        {
            "$match": {
                "_id.user_id": uid,
                "_id.test_name": {"$regex": f"^{test_name_prefix}.*"},
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
                "commitObjects": {
                    "$zip": {
                        "inputs": [
                            "$cp.v.attributes.git_commit",
                            "$cp.v.attributes.git_repo",
                            "$cp.v.attributes.branch",
                            "$cp.v.time",
                        ],
                    },
                },
            },
        },
        {
            "$unwind": "$commitObjects",
        },
        {
            "$addFields": {
                "commit": {
                    "$arrayElemAt": ["$commitObjects", 0],
                },
                "repo": {
                    "$arrayElemAt": ["$commitObjects", 1],
                },
                "branch": {
                    "$arrayElemAt": ["$commitObjects", 2],
                },
                "time": {
                    "$arrayElemAt": ["$commitObjects", 3],
                },
            },
        },
        {
            "$group": {
                "_id": {
                    "commit": "$commit",
                    "user_id": "$_id.user_id",
                    "max_pvalue": "$_id.max_pvalue",
                    "min_magnitude": "$_id.min_magnitude",
                },
                "repo": {
                    "$last": "$repo",
                },
                "branch": {
                    "$last": "$branch",
                },
                "commit_timestamp": {
                    "$last": "$time",
                },
                "change_points_timestamp": {
                    "$max": "$meta.change_points_timestamp",
                },
            },
        },
    ]

    #     {
    #         "$addFields": {
    #             "cp": {"$objectToArray": "$change_points"},
    #             "test_name": "$_id.test_name",
    #         }
    #     },
    #     {
    #         "$unwind": "$change_points",
    #     },
    #     {
    #         "$addFields": {
    #             "cpArr": {
    #                 "$objectToArray": "$change_points",
    #             },
    #         },
    #     },
    #     {
    #         "$addFields": {
    #             "commitObjects": {
    #                 "$zip": {
    #                     "inputs": [
    #                         "$cpArr.v.attributes.git_commit",
    #                         "$cpArr.v.attributes.git_repo",
    #                         "$cpArr.v.attributes.branch",
    #                         "$cpArr.v.time",
    #                     ],
    #                 },
    #             },
    #         },
    #     },
    #     {
    #         "$unwind": "$commitObjects",
    #     },
    #     {
    #         "$addFields": {
    #             "commit": {
    #                 "$arrayElemAt": ["$commitObjects", 0],
    #             },
    #             "repo": {
    #                 "$arrayElemAt": ["$commitObjects", 1],
    #             },
    #             "branch": {
    #                 "$arrayElemAt": ["$commitObjects", 2],
    #             },
    #             "time": {
    #                 "$arrayElemAt": ["$commitObjects", 4],
    #             },
    #         },
    #     },
    #     {
    #         "$group": {
    #             "_id": {
    #                 "commit": "$commit",
    #                 "user_id": "$user_id",
    #                 "max_pvalue": "$change_points._id.max_pvalue",
    #                 "min_magnitude": "$change_points._id.min_magnitude",
    #             },
    #             "repo": {
    #                 "$last": {"$arrayElemAt": ["$repo", -1]}
    #             },
    #             "branch": {
    #                 "$last": {"$arrayElemAt": ["$branch", -1]},
    #             },
    #             "commit_timestamp": {
    #                 "$last": {"$arrayElemAt": ["$time", -1]},
    #             },
    #             "change_points_timestamp": {
    #                 "$max": "$meta.change_points_timestamp",
    #             },
    #         },
    #     },
    # ]
    query = CHANGE_POINTS_PER_COMMIT
    if commit is not None:
        query.append({"$match": {"$_id.commit": commit}})
    return query
