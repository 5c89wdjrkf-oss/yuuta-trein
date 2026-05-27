"""
駅ネットワークグラフの構築と最短経路計算モジュール
"""

import heapq
from typing import Dict, List, Optional, Tuple
import networkx as nx
from gtfs_parser import GTFSParser
import config


class GraphBuilder:
    """GTFS データから駅ネットワークのグラフを構築し、最短経路を計算"""
    
    def __init__(self, gtfs_parser: GTFSParser):
        """
        初期化
        
        Args:
            gtfs_parser: GTFSParser インスタンス
        """
        self.gtfs = gtfs_parser
        self.graph = nx.DiGraph()  # 有向グラフ
        self.edge_times = {}  # (from_stop, to_stop) -> min_time（秒）
    
    def build_graph(self) -> None:
        """
        GTFS データからグラフを構築
        
        各 trip について、隣接する停車駅間をエッジで結ぶ
        """
        edges_added = 0
        
        for trip_id, stops_info in self.gtfs.stop_times.items():
            # 各 trip の停車駅を順序通りに処理
            for i in range(len(stops_info) - 1):
                current_stop = stops_info[i]
                next_stop = stops_info[i + 1]
                
                from_stop_id = current_stop['stop_id']
                to_stop_id = next_stop['stop_id']
                
                # 乗車時間を計算（秒）
                departure_time = self.gtfs.time_to_seconds(
                    current_stop['departure_time']
                )
                arrival_time = self.gtfs.time_to_seconds(
                    next_stop['arrival_time']
                )
                
                # 時刻が跨ぐ場合の処理
                if arrival_time < departure_time:
                    arrival_time += 24 * 3600
                
                travel_time = arrival_time - departure_time
                
                # 乗換ペナルティを加算
                if from_stop_id != to_stop_id:
                    travel_time += config.TRANSFER_PENALTY * 60
                
                # 既存のエッジより短い時間があれば更新
                edge_key = (from_stop_id, to_stop_id)
                if edge_key not in self.edge_times or travel_time < self.edge_times[edge_key]:
                    self.edge_times[edge_key] = travel_time
        
        # グラフにエッジを追加
        for (from_stop, to_stop), travel_time in self.edge_times.items():
            self.graph.add_edge(
                from_stop,
                to_stop,
                weight=travel_time
            )
            edges_added += 1
        
        print(f"✓ Graph built with {len(self.graph.nodes)} nodes, {edges_added} edges")
    
    def get_reachable_stations(
        self,
        start_station_id: str,
        max_time_minutes: int
    ) -> Dict[str, Dict]:
        """
        指定駅から指定時間以内で到達可能な全駅を計算
        
        Args:
            start_station_id: 出発駅 ID
            max_time_minutes: 最大乗車時間（分）
        
        Returns:
            到達可能な駅の辞書
            {
                stop_id: {
                    'name': '駅名',
                    'distance': 乗車時間（分）,
                    'path': [stop_id1, stop_id2, ...]
                },
                ...
            }
        """
        max_time_seconds = max_time_minutes * 60
        reachable = {}
        
        # Dijkstra アルゴリズムで最短経路を計算
        try:
            lengths, paths = nx.single_source_dijkstra(
                self.graph,
                start_station_id,
                weight='weight'
            )
            
            for stop_id, distance_seconds in lengths.items():
                distance_minutes = self.gtfs.seconds_to_minutes(distance_seconds)
                
                # 最大時間以内のみを追加
                if distance_minutes <= max_time_minutes:
                    reachable[stop_id] = {
                        'name': self.gtfs.get_stop_name(stop_id),
                        'distance': distance_minutes,
                        'path': paths[stop_id]
                    }
        
        except nx.NetworkXNoPath:
            # 到達不可能な駅
            pass
        except nx.NodeNotFound:
            print(f"✗ 駅が見つかりません: {start_station_id}")
            return {}
        
        return reachable
    
    def get_shortest_path(
        self,
        start_station_id: str,
        end_station_id: str
    ) -> Optional[Tuple[List[str], int]]:
        """
        2 つの駅間の最短経路を取得
        
        Args:
            start_station_id: 出発駅 ID
            end_station_id: 到着駅 ID
        
        Returns:
            (パス, 時間（分）) のタプル、見つからない場合は None
        """
        try:
            path = nx.shortest_path(
                self.graph,
                start_station_id,
                end_station_id,
                weight='weight'
            )
            
            length = nx.shortest_path_length(
                self.graph,
                start_station_id,
                end_station_id,
                weight='weight'
            )
            
            distance_minutes = self.gtfs.seconds_to_minutes(length)
            
            return (path, distance_minutes)
        
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def get_route_details(
        self,
        start_station_id: str,
        end_station_id: str
    ) -> Optional[Dict]:
        """
        2 つの駅間のルート詳細を取得
        
        Args:
            start_station_id: 出発駅 ID
            end_station_id: 到着駅 ID
        
        Returns:
            ルート詳細の辞書
            {
                'path': [stop_id1, stop_id2, ...],
                'stations': [
                    {'stop_id': ..., 'name': ..., 'arrival': ..., 'departure': ...},
                    ...
                ],
                'total_time': 乗車時間（分）,
                'transfers': 乗換回数
            }
        """
        result = self.get_shortest_path(start_station_id, end_station_id)
        if not result:
            return None
        
        path, total_time = result
        
        stations = []
        for stop_id in path:
            stations.append({
                'stop_id': stop_id,
                'name': self.gtfs.get_stop_name(stop_id)
            })
        
        # 乗換回数（路線が変わる回数）
        transfers = max(0, len(path) - 1)
        
        return {
            'path': path,
            'stations': stations,
            'total_time': total_time,
            'transfers': transfers
        }
    
    def get_statistics(self) -> Dict:
        """
        グラフの統計情報を取得
        
        Returns:
            統計情報の辞書
        """
        return {
            'total_nodes': len(self.graph.nodes),
            'total_edges': len(self.graph.edges),
            'is_connected': nx.is_strongly_connected(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes) if len(self.graph.nodes) > 0 else 0
        }
