"""
.smap 地图导入 CLI 工具

用法:
    python scripts/import_smap.py --in ./assets/default_1.smap --out ./out/map.json
"""
import argparse
import json
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.smap_importer import import_smap


def main():
    parser = argparse.ArgumentParser(description=".smap 地图导入工具")
    parser.add_argument("--in", dest="input", required=True, help="输入的 .smap 文件路径")
    parser.add_argument("--out", dest="output", required=True, help="输出的 JSON 文件路径")

    args = parser.parse_args()

    print(f"导入 .smap 文件: {args.input}")

    try:
        # 导入地图
        map_graph = import_smap(args.input)

        print(f"成功导入地图:")
        print(f"  - 地图名称: {map_graph.meta.mapName}")
        print(f"  - 版本: {map_graph.meta.version}")
        print(f"  - 分辨率: {map_graph.meta.resolution}")
        print(f"  - 节点数量: {len(map_graph.nodes)}")
        print(f"  - 边数量: {len(map_graph.edges)}")

        # 确保输出目录存在
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 输出为 JSON
        output_data = map_graph.to_dict()
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"已输出到: {args.output}")

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"数据错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
