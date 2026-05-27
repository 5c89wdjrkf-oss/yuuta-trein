#!/usr/bin/env python3
"""
関東全域 GTFS 最短乗車時間計算ツール

使用例:
  python main.py --gtfs_dir gtfs/your_dataset --from "渋谷" --limit 30
"""

import argparse
import sys
import os
import json
from gtfs_parser import GTFSParser
from graph_builder import GraphBuilder
import config


def main():
    parser = argparse.ArgumentParser(
        description='関東全域の駅→駅最短乗車時間を計算'
    )
    parser.add_argument(
        '--gtfs_dir',
        type=str,
        default=config.GTFS_DIR,
        help='GTFS データディレクトリ (デフォルト: gtfs)'
    )
    parser.add_argument(
        '--from',
        type=str,
        required=True,
        dest='from_station',
        help='出発駅名 (例: "渋谷")'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=60,
        help='最大乗車時間（分）(デフォルト: 60)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='出力ファイル (JSON/CSV) (省略時は標準出力)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'csv'],
        default='json',
        help='出力形式 (デフォルト: json)'
    )
    
    args = parser.parse_args()
    
    # GTFS ディレクトリの存在確認
    if not os.path.isdir(args.gtfs_dir):
        print(f"✗ GTFS ディレクトリが見つかりません: {args.gtfs_dir}", file=sys.stderr)
        print(f"  実行例: python main.py --gtfs_dir ./gtfs --from \"渋谷\" --limit 30", file=sys.stderr)
        sys.exit(1)
    
    print(f"📍 GTFS データを読み込み中: {args.gtfs_dir}")
    
    # GTFS を読み込み
    gtfs_parser = GTFSParser(args.gtfs_dir)
    if not gtfs_parser.load_all():
        sys.exit(1)
    
    print(f"\n🔗 駅グラフを構築中...")
    
    # グラフを構築
    graph_builder = GraphBuilder(gtfs_parser)
    graph_builder.build_graph()
    
    print(f"\n🔍 出発駅を検索中: \"{args.from_station}\"")
    
    # 出発駅を検索
    from_station_id = gtfs_parser.get_stop_by_name(args.from_station)
    if not from_station_id:
        print(f"✗ 駅が見つかりません: {args.from_station}", file=sys.stderr)
        print(f"\n利用可能な駅一覧（最初の 20 駅）:", file=sys.stderr)
        for i, (stop_id, stop_info) in enumerate(gtfs_parser.stops.items()):
            if i >= 20:
                break
            print(f"  - {stop_info['name']}", file=sys.stderr)
        sys.exit(1)
    
    from_station_name = gtfs_parser.get_stop_name(from_station_id)
    print(f"✓ 出発駅: {from_station_name} ({from_station_id})")
    
    print(f"\n⏱️  {args.limit} 分以内で到達可能な駅を検索中...")
    
    # 到達可能な駅を取得
    reachable = graph_builder.get_reachable_stations(from_station_id, args.limit)
    
    # 距離でソート
    sorted_stations = sorted(reachable.items(), key=lambda x: x[1]['distance'])
    
    print(f"\n✓ {len(sorted_stations)} 駅が到達可能です\n")
    print("=" * 60)
    print(f"{'駅名':<30} {'乗車時間（分）':>15}")
    print("=" * 60)
    
    for stop_id, info in sorted_stations:
        print(f"{info['name']:<30} {info['distance']:>15}")
    
    print("=" * 60)
    
    # 出力ファイルに保存（指定された場合）
    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        
        if args.format == 'json':
            output_data = {
                'from_station': from_station_name,
                'from_station_id': from_station_id,
                'limit_minutes': args.limit,
                'reachable_stations': [
                    {
                        'stop_id': stop_id,
                        'name': info['name'],
                        'distance': info['distance']
                    }
                    for stop_id, info in sorted_stations
                ],
                'total_count': len(sorted_stations)
            }
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"\n✓ JSON 出力: {args.output}")
        
        elif args.format == 'csv':
            import csv
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['駅ID', '駅名', '乗車時間（分）'])
                for stop_id, info in sorted_stations:
                    writer.writerow([stop_id, info['name'], info['distance']])
            print(f"\n✓ CSV 出力: {args.output}")


if __name__ == '__main__':
    main()
