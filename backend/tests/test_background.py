import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.api.background import (
    precompute_cached_change_points,
    precompute_summaries_non_leaf,
    precompute_summaries_leaves,
    make_new_summary,
    set_pop,
    is_leaf,
    get_leaves,
)


class TestHelperFunctions:
    """Test helper utility functions"""

    def test_make_new_summary(self):
        """Test creation of empty summary structure"""
        summary = make_new_summary()
        assert summary["total_change_points"] == 0
        assert summary["newest_time"] is None
        assert summary["newest_test_name"] is None
        assert summary["oldest_time"] is None
        assert summary["oldest_test_name"] is None
        assert summary["newest_change_point"] is None
        assert summary["oldest_change_point"] is None
        assert summary["largest_change"] is None
        assert summary["largest_test_name"] is None

    def test_set_pop_removes_and_returns_item(self):
        """Test set_pop removes and returns an item from set"""
        test_set = {"a", "b", "c"}
        item = set_pop(test_set)
        assert item in ["a", "b", "c"]
        assert len(test_set) == 2
        assert item not in test_set

    def test_set_pop_with_single_item(self):
        """Test set_pop with a single item"""
        test_set = {"only_one"}
        item = set_pop(test_set)
        assert item == "only_one"
        assert len(test_set) == 0

    def test_is_leaf_true_for_leaf_nodes(self):
        """Test is_leaf correctly identifies leaf nodes"""
        all_nodes = ["a", "a/b", "a/b/c", "x", "x/y"]
        assert is_leaf("a/b/c", all_nodes) is True
        assert is_leaf("x/y", all_nodes) is True

    def test_is_leaf_false_for_non_leaf_nodes(self):
        """Test is_leaf correctly identifies non-leaf nodes"""
        all_nodes = ["a", "a/b", "a/b/c"]
        assert is_leaf("a", all_nodes) is False
        assert is_leaf("a/b", all_nodes) is False

    def test_is_leaf_single_node(self):
        """Test is_leaf with a single node"""
        all_nodes = ["a"]
        assert is_leaf("a", all_nodes) is True

    def test_get_leaves_returns_only_leaf_nodes(self):
        """Test get_leaves returns only leaf nodes"""
        all_nodes = ["_id", "a", "a/b", "a/b/c", "x", "x/y"]
        leaves = get_leaves(all_nodes)
        assert "a/b/c" in leaves
        assert "x/y" in leaves
        assert "a" not in leaves
        assert "a/b" not in leaves
        assert "x" not in leaves
        assert "_id" not in leaves

    def test_get_leaves_all_leaves(self):
        """Test get_leaves when all nodes are leaves"""
        all_nodes = ["_id", "a", "b", "c"]
        leaves = get_leaves(all_nodes)
        assert len(leaves) == 3
        assert "a" in leaves
        assert "b" in leaves
        assert "c" in leaves

    def test_get_leaves_empty_list(self):
        """Test get_leaves with empty list"""
        all_nodes = []
        leaves = get_leaves(all_nodes)
        assert leaves == []


class TestPrecomputeSummariesLeaves:
    """Test precompute_summaries_leaves function"""

    @pytest.mark.anyio
    async def test_precompute_summaries_leaves_single_change_point(self):
        """Test precomputing summaries for a test with a single change point"""
        mock_store = Mock()
        mock_cache = {}
        mock_store.get_summaries_cache = AsyncMock(return_value=mock_cache)
        mock_store.save_summaries_cache = AsyncMock()

        # Create mock change point
        mock_cp = Mock()
        mock_cp.time = 100
        mock_cp.forward_change_percent = Mock(return_value=50.0)
        mock_cp.to_json = Mock(return_value={"time": 100, "change": 50.0})

        # Create mock analyzed series
        mock_analyzed_series = Mock()
        mock_analyzed_series.change_points = {"metric1": [mock_cp]}

        changes = {"test_metric": mock_analyzed_series}
        test_name = "test/example"
        user_id = "user123"

        with patch("backend.api.background.DBStore", return_value=mock_store):
            await precompute_summaries_leaves(test_name, changes, user_id)

        # Verify the cache was updated correctly
        mock_store.get_summaries_cache.assert_called_once_with(user_id)
        mock_store.save_summaries_cache.assert_called_once()

        # Check that summary was created
        saved_cache = mock_store.save_summaries_cache.call_args[0][1]
        assert test_name in saved_cache
        summary = saved_cache[test_name]
        assert summary["total_change_points"] == 1
        assert summary["newest_time"] == 100
        assert summary["newest_test_name"] == test_name

    @pytest.mark.anyio
    async def test_precompute_summaries_leaves_multiple_change_points(self):
        """Test precomputing summaries with multiple change points"""
        mock_store = Mock()
        mock_cache = {}
        mock_store.get_summaries_cache = AsyncMock(return_value=mock_cache)
        mock_store.save_summaries_cache = AsyncMock()

        # Create multiple mock change points
        mock_cp1 = Mock()
        mock_cp1.time = 100
        mock_cp1.forward_change_percent = Mock(return_value=50.0)
        mock_cp1.to_json = Mock(return_value={"time": 100, "change": 50.0})

        mock_cp2 = Mock()
        mock_cp2.time = 200
        mock_cp2.forward_change_percent = Mock(return_value=75.0)
        mock_cp2.to_json = Mock(return_value={"time": 200, "change": 75.0})

        mock_cp3 = Mock()
        mock_cp3.time = 150
        mock_cp3.forward_change_percent = Mock(return_value=100.0)
        mock_cp3.to_json = Mock(return_value={"time": 150, "change": 100.0})

        mock_analyzed_series = Mock()
        mock_analyzed_series.change_points = {"metric1": [mock_cp1, mock_cp2, mock_cp3]}

        changes = {"test_metric": mock_analyzed_series}
        test_name = "test/example"
        user_id = "user123"

        with patch("backend.api.background.DBStore", return_value=mock_store):
            await precompute_summaries_leaves(test_name, changes, user_id)

        saved_cache = mock_store.save_summaries_cache.call_args[0][1]
        summary = saved_cache[test_name]

        # Should have 3 change points
        assert summary["total_change_points"] == 3
        # Newest time should be 200
        assert summary["newest_time"] == 200
        # Oldest time should be 100
        assert summary["oldest_time"] == 100
        # Largest change should be 100.0
        assert summary["largest_change"] == 100.0


class TestPrecomputeSummariesNonLeaf:
    """Test precompute_summaries_non_leaf function"""

    @pytest.mark.anyio
    async def test_precompute_summaries_non_leaf_simple_tree(self):
        """Test precomputing non-leaf summaries for simple tree"""
        mock_store = Mock()

        # Create cache with leaf summaries
        mock_cache = {
            "_id": "cache_id",
            "a/b/c": {
                "total_change_points": 1,
                "newest_time": 100,
                "newest_test_name": "a/b/c",
                "oldest_time": 100,
                "oldest_test_name": "a/b/c",
                "newest_change_point": {"time": 100},
                "oldest_change_point": {"time": 100},
                "largest_change": 50.0,
                "largest_test_name": "a/b/c",
                "largest_change_point": {"change": 50.0},
            },
        }

        mock_store.get_summaries_cache = AsyncMock(return_value=mock_cache)
        mock_store.save_summaries_cache = AsyncMock()

        user_id = "user123"

        with patch("backend.api.background.DBStore", return_value=mock_store):
            await precompute_summaries_non_leaf(user_id)

        # Verify save was called
        mock_store.save_summaries_cache.assert_called_once_with(user_id, mock_cache)


class TestPrecomputeCachedChangePoints:
    """Test precompute_cached_change_points main function"""

    @pytest.mark.anyio
    async def test_precompute_with_no_users(self):
        """Test precompute with no users or orgs"""
        mock_store = Mock()
        mock_store.list_users = AsyncMock(return_value=[])
        mock_store.list_orgs = AsyncMock(return_value=[])

        with patch("backend.api.background.DBStore", return_value=mock_store):
            result = await precompute_cached_change_points()

        assert result == []
        mock_store.list_users.assert_called_once()
        mock_store.list_orgs.assert_called_once()

    @pytest.mark.anyio
    async def test_precompute_with_cached_results(self):
        """Test precompute when all results are already cached"""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"

        mock_store = Mock()
        mock_store.list_users = AsyncMock(return_value=[mock_user])
        mock_store.get_test_names = AsyncMock(return_value=["test1"])
        mock_store.list_orgs = AsyncMock(return_value=[])

        with patch("backend.api.background.DBStore", return_value=mock_store):
            # Mock _calc_changes to return cached results
            with patch("backend.api.background._calc_changes") as mock_calc:
                mock_calc.return_value = (Mock(), Mock(), True)  # is_cached=True
                with patch(
                    "backend.api.background.precompute_summaries_non_leaf"
                ) as mock_summary:
                    mock_summary.return_value = None
                    result = await precompute_cached_change_points()

        assert result == []

    @pytest.mark.anyio
    async def test_precompute_with_uncached_results(self):
        """Test precompute when results need to be computed"""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"

        mock_store = Mock()
        mock_store.list_users = AsyncMock(return_value=[mock_user])
        mock_store.get_test_names = AsyncMock(return_value=["test1"])
        mock_store.list_orgs = AsyncMock(return_value=[])

        with patch("backend.api.background.DBStore", return_value=mock_store):
            with patch("backend.api.background._calc_changes") as mock_calc:
                # First call returns uncached, subsequent calls return cached
                mock_calc.return_value = (Mock(), Mock(), False)  # is_cached=False
                with patch(
                    "backend.api.background.precompute_summaries_non_leaf"
                ) as mock_summary:
                    mock_summary.return_value = None
                    result = await precompute_cached_change_points()

        # Should return empty list after computing
        assert result == []

    @pytest.mark.anyio
    async def test_precompute_handles_exceptions(self):
        """Test that precompute handles exceptions gracefully"""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"

        mock_store = Mock()
        mock_store.list_users = AsyncMock(return_value=[mock_user])
        mock_store.get_test_names = AsyncMock(return_value=["test1", "test2"])
        mock_store.list_orgs = AsyncMock(return_value=[])

        with patch("backend.api.background.DBStore", return_value=mock_store):
            with patch("backend.api.background._calc_changes") as mock_calc:
                # First call raises exception, second succeeds
                mock_calc.side_effect = [
                    Exception("Test error"),
                    (Mock(), Mock(), True),
                ]
                with patch(
                    "backend.api.background.precompute_summaries_non_leaf"
                ) as mock_summary:
                    mock_summary.return_value = None
                    result = await precompute_cached_change_points()

        # Should continue processing after exception
        assert result == []

    @pytest.mark.anyio
    async def test_precompute_respects_batch_limit(self):
        """Test that precompute respects the batch limit of 150"""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"

        # Create 151 test names to exceed the limit
        test_names = [f"test{i}" for i in range(151)]

        mock_store = Mock()
        mock_store.list_users = AsyncMock(return_value=[mock_user])
        mock_store.get_test_names = AsyncMock(return_value=test_names)
        mock_store.list_orgs = AsyncMock(return_value=[])

        with patch("backend.api.background.DBStore", return_value=mock_store):
            with patch("backend.api.background._calc_changes") as mock_calc:
                # All return uncached
                mock_calc.return_value = (Mock(), Mock(), False)
                with patch(
                    "backend.api.background.precompute_summaries_non_leaf"
                ) as mock_summary:
                    mock_summary.return_value = None
                    result = await precompute_cached_change_points()

        # Should exit early after 150 computations
        assert result == []
        # _calc_changes should be called exactly 150 times before exiting
        assert mock_calc.call_count == 150

    @pytest.mark.anyio
    async def test_precompute_processes_orgs(self):
        """Test that precompute processes organizations"""
        mock_store = Mock()
        mock_store.list_users = AsyncMock(return_value=[])
        mock_store.list_orgs = AsyncMock(return_value=["org123"])
        mock_store.get_test_names = AsyncMock(return_value=["org_test1"])

        with patch("backend.api.background.DBStore", return_value=mock_store):
            with patch("backend.api.background._calc_changes") as mock_calc:
                mock_calc.return_value = (Mock(), Mock(), True)
                with patch(
                    "backend.api.background.precompute_summaries_non_leaf"
                ) as mock_summary:
                    mock_summary.return_value = None
                    result = await precompute_cached_change_points()

        assert result == []
        # Verify org was processed
        mock_store.get_test_names.assert_called_with("org123")
