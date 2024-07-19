from backend.api.changes import _calc_changes
from backend.db.db import DBStore, User


async def precompute_cached_change_points():
    """
    When new test results are POSTed (to /result/test_name_path) we immediately calculate and cache
    the change points for that test. However, the pre_computed change points can become invalidated
    for various reasons, for example if the user changes the algorithm parameters in UserSettings.
    When that happens, this function will find and recompute the change points.

    Thanks to this function, change points should almost always be ready and returned fast when a
    user is viewing a dashboard or otherwise issuing a GET.

    Also, the /results/test_name/summary end point may cause a re-compute of change points for all
    of your test result data, which can take minutes but more importantly will consume all memory
    and OOM. A goal of this background task is to compute the change points in smaller chunks so that
    won't happen.
    """
    do_n_in_one_task = 50
    db = DBStore()
    all_users = await db.list_users()
    for user in all_users:
        user_id = user.id
        test_names = await db.get_test_names(user.id)
        for test_name in test_names:
            # print("precompute_cached_change_points: " +str(user.email) + " " + test_name)
            series, changes, is_cached = await _calc_changes(test_name, user_id)

            if not is_cached:
                do_n_in_one_task -= 1
                print(
                    f"Computed new change points for user={user_id} ({user.email}), test_name={test_name}."
                )
                # The summary data could in fact naturally be part of AnalyzedSeries, but it started as
                # a side project and so its data is too.
                await precompute_summaries_leaves(test_name, changes, user)
                # We found a result series that didn't have cached change points and have now computed
                # the chánge points and cached them. Time to exit this task and let the next invocation
                # compute the next set of change points.
                # We do this to split up the background computation into smaller chunks, to avoid hogging
                # the cpu for minutes at a time and to consume infinite amounts of memory when python
                # and numpy don't release the memory quickly enough.
                if do_n_in_one_task == 0:
                    return []

        await precompute_summaries_non_leaf(user)

    print("It appears as everything is cached and there's nothing more to do?")
    return []


# async def precompute_summaries(
#     changes_batch: List[Tuple[str, List[Dict[str, AnalyzedSeries]]]], user: User
# ):
#     test_names = [n for n,l in changes_batch]
#     print("Pre-compute summaries for " + str(user.id) + " " + test_names)
#     store = DBStore()
#     cache = await store.get_summaries_cache(user.id)
#     test_name_prefix_todo = []
#
#     # First just create a summary for each test / leaf node
#     for test_name, changes in changes_batch:
#         summary = make_new_summary()
#         for metric_name, analyzed_series in changes.items():
#             for metric_name, cp_list in analyzed_series.change_points.items():
#                 for cp in cp_list:
#                     first = summary["total_change_points"] == 0
#                     if first or summary["newest_time"] < cp.time:
#                         summary["newest_time"] = cp.time
#                         summary["newest_test_name"] = test_name
#                         summary["newest_change_point"] = cp
#                     if first or summary["oldest_time"] > cp.time:
#                         summary["oldest_time"] = cp.time
#                         summary["oldest_test_name"] = test_name
#                         summary["oldest_change_point"] = cp
#                     if first or abs(summary["largest_change"]) < abs(
#                         cp.forward_change_percent()
#                     ):
#                         summary["largest_change"] = cp.forward_change_percent()
#                         summary["largest_test_name"] = test_name
#                         summary["largest_change_point"] = cp
#
#                     summary["total_change_points"] += 1
#
#         cache[test_name] = summary
#         test_name_parts = test_name.split("/")
#         if len(test_name_parts) > 1:
#             test_name_prefix_todo.append("/".join(test_name_parts[:-1]))
#
#     print("Once all leaf nodes are in the cache, go through each prefix and create a summary of its leaves")
#     non_leaf_cache = {}
#     while len(test_name_prefix_todo) > 0:
#         summary = make_new_summary()
#
#         # Get a prefix of the full test_names for which we just computed summaries
#         test_name_parts = test_name_prefix_todo.pop()
#         test_name_prefix = "/".join(test_name_parts)
#
#         # Once we are done with this, we'll continue up the tree until we find the root of everything
#         if len(test_name_parts) > 1:
#             test_name_prefix_todo.append("/".join(test_name_parts[:-1]))
#
#         prefix_leaves = []
#         for k in cache.keys():
#             if k.startswith(test_name_prefix):
#                 prefix_leaves.append[k]
#
#         leaf_summaries = [cache[leaf] for leaf in prefix_leaves]
#
#         for leaf_summary in leaf_summaries:
#             for k in summary.keys():
#                 if k == "total_change_points":
#                     summary[k] = summary[k] + leaf_summary[k]
#                 if summary["newest_time"] < leaf_summary["newest_time"]:
#                     summary["newest_time"] = leaf_summary["newest_time"]
#                     summary["newest_test_name"] = leaf_summary["newest_test_name"]
#                     summary["newest_change_point"] = leaf_summary["newest_change_point"]
#                 if summary["oldest_time"] > leaf_summary["oldest_time"]:
#                     summary["oldest_time"] = leaf_summary["oldest_time"]
#                     summary["oldest_test_name"] = leaf_summary["oldest_test_name"]
#                     summary["oldest_change_point"] = leaf_summary["oldest_change_point"]
#                 if abs(summary["largest_change"]) < abs(leaf_summary["largest_change"]):
#                     summary["largest_change"] = leaf_summary["largest_change"]
#                     summary["largest_test_name"] = leaf_summary["largest_test_name"]
#                     summary["largest_change_point"] = leaf_summary[
#                         "largest_change_point"
#                     ]
#
#             non_leaf_cache[test_name_prefix] = summary
#     # Finally just combine the two into one huge cache
#     cache.update(non_leaf_cache)
#     await store.save_summaries_cache(user.id, cache)


async def precompute_summaries_non_leaf(user: User):
    # This still OOMs with the CrateDB dataset (700+ timeseries)
    # Disabling for now. We'll just have summaries for the first level until this is fixed
    return
    print(
        "Once all leaf nodes are in the cache, go through each prefix and create a summary of its leaves"
    )

    store = DBStore()
    cache = await store.get_summaries_cache(user.id)
    non_leaf_cache = {}
    test_names = cache.keys()
    test_name_prefix_todo = set(
        [("/".join(prefix.split("/"))[:-1]) for prefix in test_names]
    )
    while len(test_name_prefix_todo) > 0:
        summary = make_new_summary()

        # Get a prefix of the full test_names for which we just computed summaries
        test_name_parts = set_pop(test_name_prefix_todo)
        test_name_prefix = "/".join(test_name_parts)

        # Once we are done with this, we'll continue up the tree until we find the root of everything
        if len(test_name_parts) > 1:
            test_name_prefix_todo.add("/".join(test_name_parts[:-1]))

        prefix_leaves = []
        for k in cache.keys():
            if k.startswith(test_name_prefix):
                prefix_leaves.append(k)

        leaf_summaries = [cache[leaf] for leaf in prefix_leaves]

        for leaf_summary in leaf_summaries:
            summary["total_change_points"] = (
                summary["total_change_points"] + leaf_summary["total_change_points"]
            )
            if summary["newest_time"] < leaf_summary["newest_time"]:
                summary["newest_time"] = leaf_summary["newest_time"]
                summary["newest_test_name"] = leaf_summary["newest_test_name"]
                summary["newest_change_point"] = leaf_summary["newest_change_point"]
            if summary["oldest_time"] > leaf_summary["oldest_time"]:
                summary["oldest_time"] = leaf_summary["oldest_time"]
                summary["oldest_test_name"] = leaf_summary["oldest_test_name"]
                summary["oldest_change_point"] = leaf_summary["oldest_change_point"]
            if abs(summary["largest_change"]) < abs(leaf_summary["largest_change"]):
                summary["largest_change"] = leaf_summary["largest_change"]
                summary["largest_test_name"] = leaf_summary["largest_test_name"]
                summary["largest_change_point"] = leaf_summary["largest_change_point"]

            non_leaf_cache[test_name_prefix] = summary
    # Finally just combine the two into one huge cache
    cache.update(non_leaf_cache)
    await store.save_summaries_cache(user.id, cache)


async def precompute_summaries_leaves(test_name, changes, user):
    print("Pre-compute summary for " + str(user.id) + " " + test_name)
    store = DBStore()
    cache = await store.get_summaries_cache(user.id)
    summary = make_new_summary()
    for metric_name, analyzed_series in changes.items():
        for metric_name, cp_list in analyzed_series.change_points.items():
            for cp in cp_list:
                first = summary["total_change_points"] == 0
                if first or summary["newest_time"] < cp.time:
                    summary["newest_time"] = cp.time
                    summary["newest_test_name"] = test_name
                    summary["newest_change_point"] = cp.to_json()
                if first or summary["oldest_time"] > cp.time:
                    summary["oldest_time"] = cp.time
                    summary["oldest_test_name"] = test_name
                    summary["oldest_change_point"] = cp.to_json()
                if first or abs(summary["largest_change"]) < abs(
                    cp.forward_change_percent()
                ):
                    summary["largest_change"] = cp.forward_change_percent()
                    summary["largest_test_name"] = test_name
                    summary["largest_change_point"] = cp.to_json()

                summary["total_change_points"] += 1

        cache[test_name] = summary
    # print(cache)
    # TODO:The way this ended up, this could rather be done as a MongoDB update. This avoids a race
    # condition in the DB layer. Otoh if we only run this task in a single thread, nobody else is
    # writing to this record.
    # TODO: Should add a timestamp or done/todo switch to this document. Now we continuosly recompute
    # the non-leaf nodes even if nothing changed. For example, a simple model would be to flip the
    # value to "todo" whenever leaf summaries are updated, and "done" when non-leaf summaries are
    # written. In the same update, of course.
    await store.save_summaries_cache(user.id, cache)


def make_new_summary():
    return {
        "total_change_points": 0,
        "newest_time": None,
        "newest_test_name": None,
        "oldest_time": None,
        "oldest_test_name": None,
        "newest_change_point": None,
        "oldest_change_point": None,
        "largest_change": None,
        "largest_test_name": None,
    }


def set_pop(myset):
    for item in myset:
        myset.remove(item)
        return item
