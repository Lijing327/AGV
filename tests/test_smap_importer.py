"""
.smap 导入器单元测试
"""
import pytest
import json
import os
import tempfile
from app.services.smap_importer import import_smap, bezier_length


class TestBezierLength:
    """测试贝塞尔曲线长度估算"""

    def test_bezier_length_straight_line(self):
        """测试直线（控制点在起终点连线上）应返回起终点距离"""
        p0 = (0.0, 0.0)
        p1 = (1.0, 1.0)  # 在直线上
        p2 = (2.0, 2.0)  # 在直线上
        p3 = (3.0, 3.0)  # 终点

        length = bezier_length(p0, p1, p2, p3, segments=50)
        expected = (3.0 ** 2 + 3.0 ** 2) ** 0.5  # sqrt(18) ≈ 4.2426

        assert abs(length - expected) < 0.1, f"Expected ~{expected}, got {length}"

    def test_bezier_length_curved(self):
        """测试曲线长度应大于直线距离"""
        p0 = (0.0, 0.0)
        p1 = (5.0, 0.0)  # 控制点偏离直线
        p2 = (5.0, 5.0)
        p3 = (0.0, 5.0)

        curved_length = bezier_length(p0, p1, p2, p3, segments=50)
        straight_length = (0.0 ** 2 + 5.0 ** 2) ** 0.5  # 5.0

        assert curved_length > straight_length, "曲线长度应大于直线距离"


class TestImportSmap:
    """测试 .smap 导入功能"""

    @pytest.fixture
    def valid_smap_data(self):
        """有效的 .smap 测试数据"""
        return {
            "header": {
                "mapType": "2D-Map",
                "mapName": "test_map",
                "minPos": {"x": -5.0, "y": -5.0},
                "maxPos": {"x": 10.0, "y": 10.0},
                "resolution": 0.02,
                "version": "1.0.6"
            },
            "normalPosList": [],  # 不使用
            "advancedPointList": [
                {
                    "instanceName": "node_1",
                    "className": "NormalPoint",
                    "pos": {"x": 0.0, "y": 0.0}
                },
                {
                    "instanceName": "node_2",
                    "className": "ChargingPoint",
                    "pos": {"x": 5.0, "y": 0.0}
                },
                {
                    "instanceName": "node_3",
                    "className": "ParkingPoint",
                    "pos": {"x": 5.0, "y": 5.0}
                },
            ],
            "advancedCurveList": [
                {
                    "instanceName": "edge_1",
                    "className": "BezierPath",
                    "startPos": {"instanceName": "node_1"},
                    "endPos": {"instanceName": "node_2"},
                    "controlPos1": {"x": 2.5, "y": 1.0},
                    "controlPos2": {"x": 2.5, "y": -1.0}
                },
                {
                    "instanceName": "edge_2",
                    "className": "NormalPath",
                    "startPos": {"instanceName": "node_2"},
                    "endPos": {"instanceName": "node_3"}
                }
            ]
        }

    @pytest.fixture
    def smap_file(self, valid_smap_data):
        """创建临时的 .smap 文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".smap", delete=False, encoding="utf-8") as f:
            json.dump(valid_smap_data, f)
            temp_path = f.name

        yield temp_path

        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_parse_nodes(self, smap_file):
        """测试节点解析：节点数量正确、字段正确"""
        graph = import_smap(smap_file)

        # 验证节点数量
        assert len(graph.nodes) == 3, f"Expected 3 nodes, got {len(graph.nodes)}"

        # 验证节点字段
        node_1 = next(n for n in graph.nodes if n.id == "node_1")
        assert node_1.x == 0.0
        assert node_1.y == 0.0
        assert node_1.type == "NormalPoint"

        node_2 = next(n for n in graph.nodes if n.id == "node_2")
        assert node_2.x == 5.0
        assert node_2.y == 0.0
        assert node_2.type == "ChargingPoint"

        node_3 = next(n for n in graph.nodes if n.id == "node_3")
        assert node_3.x == 5.0
        assert node_3.y == 5.0
        assert node_3.type == "ParkingPoint"

    def test_parse_edges(self, smap_file):
        """测试边解析：edges 数量正确、source/target 都在 nodes 中"""
        graph = import_smap(smap_file)

        # 验证边数量
        assert len(graph.edges) == 2, f"Expected 2 edges, got {len(graph.edges)}"

        # 验证边的属性
        edge_1 = next(e for e in graph.edges if e.id == "edge_1")
        assert edge_1.source == "node_1"
        assert edge_1.target == "node_2"
        assert edge_1.bezier is not None
        assert edge_1.bezier.x1 == 2.5
        assert edge_1.bezier.y1 == 1.0
        assert edge_1.bezier.x2 == 2.5
        assert edge_1.bezier.y2 == -1.0
        assert edge_1.length is not None
        assert edge_1.length > 0

        edge_2 = next(e for e in graph.edges if e.id == "edge_2")
        assert edge_2.source == "node_2"
        assert edge_2.target == "node_3"
        assert edge_2.bezier is None
        assert edge_2.length is not None
        # edge_2 是直线，长度应为 5.0
        assert abs(edge_2.length - 5.0) < 0.01

    def test_adjacency_built_correctly(self, smap_file):
        """测试邻接表构建正确（双向）"""
        graph = import_smap(smap_file)

        # 验证邻接表包含所有节点
        assert set(graph.adjacency.keys()) == {"node_1", "node_2", "node_3"}

        # 验证 node_1 的邻接
        assert len(graph.adjacency["node_1"]) == 1  # 只有 edge_1
        neighbor = graph.adjacency["node_1"][0]
        assert neighbor["to"] == "node_2"
        assert neighbor["edgeId"] == "edge_1"
        assert "cost" in neighbor

        # 验证 node_2 的邻接（双向，所以有 edge_1 和 edge_2）
        assert len(graph.adjacency["node_2"]) == 2
        to_targets = {n["to"] for n in graph.adjacency["node_2"]}
        assert to_targets == {"node_1", "node_3"}

        # 验证 node_3 的邻接
        assert len(graph.adjacency["node_3"]) == 1
        neighbor = graph.adjacency["node_3"][0]
        assert neighbor["to"] == "node_2"

    def test_missing_node_ref_raises(self):
        """测试边引用不存在的节点时抛出 ValueError"""
        invalid_data = {
            "header": {
                "mapType": "2D-Map",
                "mapName": "test_map",
                "minPos": {"x": -5.0, "y": -5.0},
                "maxPos": {"x": 10.0, "y": 10.0},
                "resolution": 0.02,
                "version": "1.0.6"
            },
            "normalPosList": [],
            "advancedPointList": [
                {
                    "instanceName": "node_1",
                    "className": "NormalPoint",
                    "pos": {"x": 0.0, "y": 0.0}
                }
            ],
            "advancedCurveList": [
                {
                    "instanceName": "edge_1",
                    "className": "NormalPath",
                    "startPos": {"instanceName": "node_1"},
                    "endPos": {"instanceName": "node_missing"}  # 不存在的节点
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".smap", delete=False, encoding="utf-8") as f:
            json.dump(invalid_data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                import_smap(temp_path)

            # 验证错误消息包含缺失的节点 ID
            error_msg = str(exc_info.value)
            assert "node_missing" in error_msg
            assert "不存在的节点" in error_msg
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_duplicate_node_id_raises(self):
        """测试重复节点 ID 时抛出 ValueError"""
        invalid_data = {
            "header": {
                "mapType": "2D-Map",
                "mapName": "test_map",
                "minPos": {"x": -5.0, "y": -5.0},
                "maxPos": {"x": 10.0, "y": 10.0},
                "resolution": 0.02,
                "version": "1.0.6"
            },
            "normalPosList": [],
            "advancedPointList": [
                {
                    "instanceName": "node_1",
                    "className": "NormalPoint",
                    "pos": {"x": 0.0, "y": 0.0}
                },
                {
                    "instanceName": "node_1",  # 重复的 ID
                    "className": "NormalPoint",
                    "pos": {"x": 5.0, "y": 5.0}
                }
            ],
            "advancedCurveList": []
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".smap", delete=False, encoding="utf-8") as f:
            json.dump(invalid_data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                import_smap(temp_path)

            # 验证错误消息包含重复的节点 ID
            error_msg = str(exc_info.value)
            assert "node_1" in error_msg
            assert "重复" in error_msg
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_meta_parsing(self, smap_file):
        """测试元数据解析"""
        graph = import_smap(smap_file)

        assert graph.meta.mapName == "test_map"
        assert graph.meta.resolution == 0.02
        assert graph.meta.version == "1.0.6"
        assert graph.meta.minPos == {"x": -5.0, "y": -5.0}
        assert graph.meta.maxPos == {"x": 10.0, "y": 10.0}
