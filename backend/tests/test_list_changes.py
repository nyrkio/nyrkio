import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from bson.objectid import ObjectId
from backend.db.list_changes import change_points_per_commit, _set_parameters


class TestSetParameters:
    """Test the _set_parameters function that builds MongoDB query"""

    def test_set_parameters_basic(self):
        """Test basic parameter setting"""
        user_id = ObjectId()
        test_name_prefix = "test/path"
        meta = {"change_points_timestamp": datetime(2024, 1, 1)}
        config = {
            "core": {
                "max_pvalue": 0.001,
                "min_magnitude": 0.05,
            }
        }

        query = _set_parameters(user_id, test_name_prefix, meta, config)

        assert isinstance(query, list)
        assert len(query) > 0

        # Check match stage
        match_stage = query[0]
        assert "$match" in match_stage
        assert match_stage["$match"]["_id.user_id"] == user_id
        assert match_stage["$match"]["_id.max_pvalue"] == 0.001
        assert match_stage["$match"]["_id.min_magnitude"] == 0.05

    def test_set_parameters_with_string_user_id(self):
        """Test parameter setting with string user_id"""
        user_id_str = str(ObjectId())
        test_name_prefix = "test"
        meta = {"change_points_timestamp": datetime(2024, 1, 1)}
        config = {"core": {}}

        query = _set_parameters(user_id_str, test_name_prefix, meta, config)

        match_stage = query[0]
        assert isinstance(match_stage["$match"]["_id.user_id"], ObjectId)

    def test_set_parameters_with_trailing_slash(self):
        """Test that _set_parameters handles prefix with trailing slash"""
        user_id = ObjectId()
        test_name_prefix = "test/path/"
        meta = {"change_points_timestamp": datetime(2024, 1, 1)}
        config = {"core": {}}

        query = _set_parameters(user_id, test_name_prefix, meta, config)

        match_stage = query[0]
        # _set_parameters receives the prefix as-is (slash removal happens in caller)
        assert match_stage["$match"]["_id.test_name"]["$regex"] == "^test/path/(/.*)?$"

    def test_set_parameters_empty_prefix(self):
        """Test with empty test_name_prefix"""
        user_id = ObjectId()
        test_name_prefix = ""
        meta = {}
        config = {}

        query = _set_parameters(user_id, test_name_prefix, meta, config)

        match_stage = query[0]
        assert "$regex" in match_stage["$match"]["_id.test_name"]

    def test_set_parameters_default_values(self):
        """Test that default values are used when config is empty"""
        user_id = ObjectId()
        test_name_prefix = "test"
        meta = {}
        config = {}

        query = _set_parameters(user_id, test_name_prefix, meta, config)

        match_stage = query[0]
        # Should use defaults: max_pvalue=0.001, min_magnitude=0.05
        assert match_stage["$match"]["_id.max_pvalue"] == 0.001
        assert match_stage["$match"]["_id.min_magnitude"] == 0.05

    def test_set_parameters_with_commit_filter(self):
        """Test that commit filter is added when provided"""
        user_id = ObjectId()
        test_name_prefix = "test"
        meta = {}
        config = {}
        commit = "abc123"

        query = _set_parameters(user_id, test_name_prefix, meta, config, commit)

        # Should have an additional match stage for commit
        # The commit filter is appended at the end
        last_stage = query[-1]
        assert "$match" in last_stage

    def test_set_parameters_default_timestamp(self):
        """Test that default timestamp is used when meta is empty"""
        user_id = ObjectId()
        test_name_prefix = "test"
        meta = {}
        config = {}

        query = _set_parameters(user_id, test_name_prefix, meta, config)

        match_stage = query[0]
        assert match_stage["$match"]["meta.change_points_timestamp"]["$gte"] == datetime(
            1970, 1, 1
        )

    def test_set_parameters_custom_timestamp(self):
        """Test with custom timestamp in meta"""
        user_id = ObjectId()
        test_name_prefix = "test"
        custom_time = datetime(2023, 6, 15, 12, 30)
        meta = {"change_points_timestamp": custom_time}
        config = {}

        query = _set_parameters(user_id, test_name_prefix, meta, config)

        match_stage = query[0]
        assert match_stage["$match"]["meta.change_points_timestamp"]["$gte"] == custom_time


class TestChangePointsPerCommit:
    """Test the change_points_per_commit function"""

    @pytest.mark.anyio
    async def test_change_points_per_commit_basic(self):
        """Test basic change_points_per_commit functionality"""
        user_id = ObjectId()
        test_name_prefix = "test/path"

        mock_store = Mock()
        mock_config = {"core": {"max_pvalue": 0.001, "min_magnitude": 0.05}}
        mock_meta = {"change_points_timestamp": datetime(2024, 1, 1)}
        mock_store.get_user_config = AsyncMock(return_value=(mock_config, mock_meta))

        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=[{"_id": "test", "data": "value"}])

        mock_aggregate = Mock(return_value=mock_cursor)
        mock_db = Mock()
        mock_db.change_points.aggregate = mock_aggregate
        mock_store.db = mock_db

        with patch("backend.db.list_changes.DBStore", return_value=mock_store):
            result = await change_points_per_commit(user_id, test_name_prefix)

        assert isinstance(result, list)
        assert len(result) == 1
        mock_store.get_user_config.assert_called_once_with(user_id)
        mock_aggregate.assert_called_once()

    @pytest.mark.anyio
    async def test_change_points_per_commit_with_commit_filter(self):
        """Test change_points_per_commit with commit filter"""
        user_id = ObjectId()
        test_name_prefix = "test"
        commit = "abc123"

        mock_store = Mock()
        mock_config = {}
        mock_meta = {}
        mock_store.get_user_config = AsyncMock(return_value=(mock_config, mock_meta))

        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=[])

        mock_aggregate = Mock(return_value=mock_cursor)
        mock_db = Mock()
        mock_db.change_points.aggregate = mock_aggregate
        mock_store.db = mock_db

        with patch("backend.db.list_changes.DBStore", return_value=mock_store):
            result = await change_points_per_commit(user_id, test_name_prefix, commit)

        assert isinstance(result, list)
        # Verify aggregate was called with query including commit filter
        called_query = mock_aggregate.call_args[0][0]
        assert isinstance(called_query, list)

    @pytest.mark.anyio
    async def test_change_points_per_commit_empty_results(self):
        """Test change_points_per_commit returns empty list when no results"""
        user_id = ObjectId()
        test_name_prefix = "nonexistent"

        mock_store = Mock()
        mock_config = {}
        mock_meta = {}
        mock_store.get_user_config = AsyncMock(return_value=(mock_config, mock_meta))

        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=[])

        mock_aggregate = Mock(return_value=mock_cursor)
        mock_db = Mock()
        mock_db.change_points.aggregate = mock_aggregate
        mock_store.db = mock_db

        with patch("backend.db.list_changes.DBStore", return_value=mock_store):
            result = await change_points_per_commit(user_id, test_name_prefix)

        assert result == []

    @pytest.mark.anyio
    async def test_change_points_per_commit_with_org_id(self):
        """Test change_points_per_commit with organization ID as string"""
        # Use a valid ObjectId string format (24 hex characters)
        org_id = str(ObjectId())
        test_name_prefix = "org/test"

        mock_store = Mock()
        mock_config = {}
        mock_meta = {}
        mock_store.get_user_config = AsyncMock(return_value=(mock_config, mock_meta))

        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=[])

        mock_aggregate = Mock(return_value=mock_cursor)
        mock_db = Mock()
        mock_db.change_points.aggregate = mock_aggregate
        mock_store.db = mock_db

        with patch("backend.db.list_changes.DBStore", return_value=mock_store):
            result = await change_points_per_commit(org_id, test_name_prefix)

        assert isinstance(result, list)
        mock_store.get_user_config.assert_called_once_with(org_id)

    @pytest.mark.anyio
    async def test_change_points_per_commit_multiple_results(self):
        """Test change_points_per_commit with multiple change points"""
        user_id = ObjectId()
        test_name_prefix = "test"

        mock_store = Mock()
        mock_config = {"core": {"max_pvalue": 0.01, "min_magnitude": 0.1}}
        mock_meta = {"change_points_timestamp": datetime(2024, 1, 1)}
        mock_store.get_user_config = AsyncMock(return_value=(mock_config, mock_meta))

        mock_results = [
            {
                "_id": {"git_commit": "commit1", "test_name": "test/a"},
                "time": datetime(2024, 1, 1),
                "metric_name": ["metric1"],
            },
            {
                "_id": {"git_commit": "commit2", "test_name": "test/b"},
                "time": datetime(2024, 1, 2),
                "metric_name": ["metric2"],
            },
            {
                "_id": {"git_commit": "commit3", "test_name": "test/c"},
                "time": datetime(2024, 1, 3),
                "metric_name": ["metric3"],
            },
        ]

        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=mock_results)

        mock_aggregate = Mock(return_value=mock_cursor)
        mock_db = Mock()
        mock_db.change_points.aggregate = mock_aggregate
        mock_store.db = mock_db

        with patch("backend.db.list_changes.DBStore", return_value=mock_store):
            result = await change_points_per_commit(user_id, test_name_prefix)

        assert len(result) == 3
        assert result[0]["_id"]["git_commit"] == "commit1"
        assert result[1]["_id"]["git_commit"] == "commit2"
        assert result[2]["_id"]["git_commit"] == "commit3"

    @pytest.mark.anyio
    async def test_change_points_per_commit_root_prefix(self):
        """Test with root prefix (empty string)"""
        user_id = ObjectId()
        test_name_prefix = ""

        mock_store = Mock()
        mock_config = {}
        mock_meta = {}
        mock_store.get_user_config = AsyncMock(return_value=(mock_config, mock_meta))

        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=[])

        mock_aggregate = Mock(return_value=mock_cursor)
        mock_db = Mock()
        mock_db.change_points.aggregate = mock_aggregate
        mock_store.db = mock_db

        with patch("backend.db.list_changes.DBStore", return_value=mock_store):
            result = await change_points_per_commit(user_id, test_name_prefix)

        assert isinstance(result, list)
        # Verify query was built correctly with empty prefix
        called_query = mock_aggregate.call_args[0][0]
        match_stage = called_query[0]
        assert "$regex" in match_stage["$match"]["_id.test_name"]
