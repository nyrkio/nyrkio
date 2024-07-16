from backend.api.changes import _calc_changes
from backend.db.db import (
    DBStore,
)
import logging


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
        user_id = str(user.id)
        # print(user_id)
        test_names = await db.get_test_names(user.id)
        # print(test_names)
        for test_name in test_names:
            # print("precompute_cached_change_points: " +str(user.email) + " " + test_name)
            series, changes, is_cached = await _calc_changes(test_name, user_id)
            if not is_cached:
                do_n_in_one_task -= 1
                logging.info(
                    f"Computed new change points for user={user_id}, test_name={test_name}."
                )
                print(
                    f"Computed new change points for user={user_id} ({user.email}), test_name={test_name}."
                )
                # We found a result series that didn't have cached change points and have now computed
                # the chánge points and cached them. Time to exit this task and let the next invocation
                # compute the next set of change points.
                # We do this to split up the background computation into smaller chunks, to avoid hogging
                # the cpu for minutes at a time and to consume infinite amounts of memory when python
                # and numpy don't release the memory quickly enough.
                if do_n_in_one_task == 0:
                    return []

    print("It appears as everything is cached and there's nothing to do?")
    return []
