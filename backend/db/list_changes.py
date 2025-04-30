from typing import Any
from bson.objectid import ObjectId

from backend.db.db import DBStore


async def change_points_per_commit(
    user_or_org_id: Any, test_name_prefix: str, commit: str = None
):
    store = DBStore()

    # the match is not on arbitrary prefix, rather only on full "parts", that is,
    # if this was a path to something then each part is a directory name.
    if test_name_prefix[-1] != "/":
        test_name_prefix += "/"

    query = _set_parameters(user_or_org_id, test_name_prefix, commit)

    return await store.get_collection_valid_change_points(query)


CHANGE_POINTS_PER_COMMIT = [
    {
        "$match": {
            "user_id": "XXXXXXXXXX",
        }
    },
    {"$unwind": "$change_points"},
    {
        "$addFields": {
            "cp": {"$objectToArray": "$change_points.change_points"},
            "test_name": "$change_points._id.test_name",
        }
    },
    {"$match": {"test_name": "XXXXXXXXXX"}},
    {"$project": {"change_points.change_points": False}},
    {"$unwind": "$cp"},
    {
        "$addFields": {
            "commitObjects": {
                "$zip": {
                    "inputs": [
                        "$cp.v.attributes.git_commit",
                        "$cp.v.attributes.git_repo",
                        "$cp.v.attributes.branch",
                        "$cp.v.time",
                    ]
                }
            }
        }
    },
    {"$unwind": "$commitObjects"},
    {
        "$addFields": {
            "commit": {"$arrayElemAt": ["$commitObjects", 0]},
            "repo": {"$arrayElemAt": ["$commitObjects", 1]},
            "branch": {"$arrayElemAt": ["$commitObjects", 2]},
            "time": {"$arrayElemAt": ["$commitObjects", 4]},
        }
    },
    {
        "$group": {
            "_id": {
                "commit": "$commit",
                "user_id": "$user_id",
                "max_pvalue": "$change_points._id.max_pvalue",
                "min_magnitude": "$change_points._id.min_magnitude",
            },
            "repo": {"$push": "$repo"},
            "branch": {"$push": "$branch"},
        }
    },
]


def _set_parameters(user_or_org_id, test_name_prefix, commit=None):
    uid = user_or_org_id
    if isinstance(user_or_org_id, str):
        uid = ObjectId(user_or_org_id)

    # Mainly be careful not to modify the template itself
    query = CHANGE_POINTS_PER_COMMIT
    query[0] = {
        "$match": {
            "user_id": uid,
        }
    }
    query[3] = {"$match": {"test_name": {"$regex": f"^{test_name_prefix}.*"}}}
    if commit is not None:
        query.append({"$match": {"$_id.commit": commit}})
    return query
