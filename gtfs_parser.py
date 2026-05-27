"""
GTFS ファイルの読み込み・解析モジュール
"""

import os
import csv
from typing import Dict, List, Optional, Tuple


class GTFSParser:
    """GTFS（General Transit Feed Specification）ファイルを解析"""
    
    def __init__(self, gtfs_dir: str):
        """
        初期化
        
        Args:
            gtfs_dir: GTFS ファイルが格納されているディレクトリ
        """
        self.gtfs_dir = gtfs_dir
        self.stops = {}  # stop_id -> {name, lat, lon}
        self.routes = {}  # route_id -> {short_name, long_name}
        self.trips = {}  # trip_id -> {route_id, service_id}
        self.stop_times = {}  # trip_id -> [(stop_id, arrival_time, departure_time), ...]
        self.transfers = {}  # (from_stop_id, to_stop_id) -> min_transfer_time
        self.stop_id_by_name = {}  # 駅名 -> stop_id のマッピング
    
    def load_all(self) -> bool:
        """
        全ての GTFS ファイルを読み込む
        
        Returns:
            成功時 True、失敗時 False
        """
        try:
            if not self._load_stops():
                return False
            if not self._load_routes():
                return False
            if not self._load_trips():
                return False
            if not self._load_stop_times():
                return False
            self._load_transfers()  # Optional ファイル
            return True
        except Exception as e:
            print(f"✗ GTFS 読み込みエラー: {e}")
            return False
    
    def _load_stops(self) -> bool:
        """stops.txt を読み込む"""
        stops_file = os.path.join(self.gtfs_dir, 'stops.txt')
        
        if not os.path.exists(stops_file):
            print(f"✗ ファイルが見つかりません: {stops_file}")
            return False
        
        try:
            with open(stops_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stop_id = row['stop_id']
                    stop_name = row.get('stop_name', '')
                    
                    self.stops[stop_id] = {
                        'name': stop_name,
                        'lat': float(row.get('stop_lat', 0)),
                        'lon': float(row.get('stop_lon', 0))
                    }
                    
                    # 駅名からの検索用マッピング
                    if stop_name:
                        if stop_name not in self.stop_id_by_name:
                            self.stop_id_by_name[stop_name] = []
                        self.stop_id_by_name[stop_name].append(stop_id)
            
            print(f"✓ Loaded {len(self.stops)} stops")
            return True
        except Exception as e:
            print(f"✗ stops.txt 読み込みエラー: {e}")
            return False
    
    def _load_routes(self) -> bool:
        """routes.txt を読み込む"""
        routes_file = os.path.join(self.gtfs_dir, 'routes.txt')
        
        if not os.path.exists(routes_file):
            print(f"✗ ファイルが見つかりません: {routes_file}")
            return False
        
        try:
            with open(routes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    route_id = row['route_id']
                    self.routes[route_id] = {
                        'short_name': row.get('route_short_name', ''),
                        'long_name': row.get('route_long_name', '')
                    }
            
            print(f"✓ Loaded {len(self.routes)} routes")
            return True
        except Exception as e:
            print(f"✗ routes.txt 読み込みエラー: {e}")
            return False
    
    def _load_trips(self) -> bool:
        """trips.txt を読み込む"""
        trips_file = os.path.join(self.gtfs_dir, 'trips.txt')
        
        if not os.path.exists(trips_file):
            print(f"✗ ファイルが見つかりません: {trips_file}")
            return False
        
        try:
            with open(trips_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trip_id = row['trip_id']
                    self.trips[trip_id] = {
                        'route_id': row['route_id'],
                        'service_id': row.get('service_id', '')
                    }
            
            print(f"✓ Loaded {len(self.trips)} trips")
            return True
        except Exception as e:
            print(f"✗ trips.txt 読み込みエラー: {e}")
            return False
    
    def _load_stop_times(self) -> bool:
        """stop_times.txt を読み込む"""
        stop_times_file = os.path.join(self.gtfs_dir, 'stop_times.txt')
        
        if not os.path.exists(stop_times_file):
            print(f"✗ ファイルが見つかりません: {stop_times_file}")
            return False
        
        try:
            with open(stop_times_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trip_id = row['trip_id']
                    stop_id = row['stop_id']
                    arrival_time = row.get('arrival_time', '')
                    departure_time = row.get('departure_time', '')
                    
                    if trip_id not in self.stop_times:
                        self.stop_times[trip_id] = []
                    
                    self.stop_times[trip_id].append({
                        'stop_id': stop_id,
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'stop_sequence': int(row.get('stop_sequence', 0))
                    })
            
            # 各 trip の stop_times を stop_sequence でソート
            for trip_id in self.stop_times:
                self.stop_times[trip_id].sort(
                    key=lambda x: x['stop_sequence']
                )
            
            print(f"✓ Loaded stop_times for {len(self.stop_times)} trips")
            return True
        except Exception as e:
            print(f"✗ stop_times.txt 読み込みエラー: {e}")
            return False
    
    def _load_transfers(self) -> None:
        """transfers.txt を読み込む（オプション）"""
        transfers_file = os.path.join(self.gtfs_dir, 'transfers.txt')
        
        if not os.path.exists(transfers_file):
            return
        
        try:
            with open(transfers_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    from_stop = row['from_stop_id']
                    to_stop = row['to_stop_id']
                    transfer_time = int(row.get('min_transfer_time', 0))
                    
                    key = (from_stop, to_stop)
                    if key not in self.transfers:
                        self.transfers[key] = transfer_time
                    else:
                        self.transfers[key] = min(self.transfers[key], transfer_time)
            
            print(f"✓ Loaded {len(self.transfers)} transfers")
        except Exception as e:
            print(f"⚠ transfers.txt 読み込みエラー（無視）: {e}")
    
    def get_stop_by_name(self, name: str) -> Optional[str]:
        """
        駅名から stop_id を取得
        
        Args:
            name: 駅名
        
        Returns:
            stop_id（見つからない場合は None）
        """
        if name in self.stop_id_by_name:
            return self.stop_id_by_name[name][0]
        
        # 部分一致で検索
        for stop_name, stop_ids in self.stop_id_by_name.items():
            if name in stop_name or stop_name in name:
                return stop_ids[0]
        
        return None
    
    def get_stop_name(self, stop_id: str) -> str:
        """
        stop_id から駅名を取得
        
        Args:
            stop_id: 駅 ID
        
        Returns:
            駅名（見つからない場合は stop_id をそのまま返す）
        """
        if stop_id in self.stops:
            return self.stops[stop_id]['name']
        return stop_id
    
    def get_all_stop_names(self) -> List[str]:
        """
        全駅名のリストを取得
        
        Returns:
            駅名のリスト
        """
        return list(self.stop_id_by_name.keys())
    
    def time_to_seconds(self, time_str: str) -> int:
        """
        GTFS 形式の時刻文字列を秒に変換
        
        Args:
            time_str: HH:MM:SS 形式の時刻文字列
        
        Returns:
            秒単位の時刻（24時間を超える場合もあり）
        """
        if not time_str:
            return 0
        
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        
        return hours * 3600 + minutes * 60 + seconds
    
    def seconds_to_minutes(self, seconds: int) -> int:
        """秒を分に変換（四捨五入）"""
        return round(seconds / 60)
