# 🚇 yuuta-trein - 関東全域 GTFS 最短乗車時間計算ツール

物件探しの「○○駅から何分圏内」という曖昧な条件を、**駅→駅（乗車時間ベース）**の考え方に分解し、比較しやすい条件に整えるツールです。

## 📖 概要

このツールは、関東地方の複数の鉄道事業者（東京メトロ、JR東日本、小田急、京王など）のGTFS（General Transit Feed Specification）データを統合し、指定した駅から一定時間以内に到達可能な全駅を計算します。

## ✨ 特徴

- ✅ **複数事業者対応**: 関東全域の主要鉄道事業者に対応
- ✅ **正確な最短経路計算**: Dijkstra アルゴリズムで確実に最短乗車時間を計算
- ✅ **乗換ペナルティ対応**: 乗換時間を考慮した現実的な計算
- ✅ **複数出力形式**: JSON/CSV での出力に対応
- ✅ **シンプルな CLI**: 引数で指定するだけで簡単に利用可能

## 🚀 インストール

### 前提条件

- Python 3.9 以上
- pip

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/5c89wdjrkf-oss/yuuta-trein.git
cd yuuta-trein

# 依存パッケージをインストール
pip install -r requirements.txt

# GTFS データディレクトリを作成
mkdir -p gtfs
```

## 📥 GTFS データの準備

### 1. GTFS データの取得

関東の主要鉄道事業者から GTFS データを取得します：

#### 東京メトロ
```bash
wget https://api.odpt.org/api/v4/gtfs/Tokyo-Metro.zip -O gtfs/tokyo-metro.zip
unzip gtfs/tokyo-metro.zip -d gtfs/tokyo-metro/
```

#### 都営地下鉄
```bash
wget https://api.odpt.org/api/v4/gtfs/Toei.zip -O gtfs/toei.zip
unzip gtfs/toei.zip -d gtfs/toei/
```

#### JR 東日本
```bash
wget https://api.odpt.org/api/v4/gtfs/JR-East.zip -O gtfs/jr-east.zip
unzip gtfs/jr-east.zip -d gtfs/jr-east/
```

#### 小田急電鉄
```bash
wget https://api.odpt.org/api/v4/gtfs/Odakyu.zip -O gtfs/odakyu.zip
unzip gtfs/odakyu.zip -d gtfs/odakyu/
```

#### 京王電鉄
```bash
wget https://api.odpt.org/api/v4/gtfs/Keio.zip -O gtfs/keio.zip
unzip gtfs/keio.zip -d gtfs/keio/
```

### 2. データの統合（オプション）

複数事業者のデータを 1 つのディレクトリに統合する場合：

```bash
# gtfs/merged/ に全データをコピー
mkdir -p gtfs/merged
cp gtfs/tokyo-metro/*.txt gtfs/merged/
cp gtfs/toei/*.txt gtfs/merged/
# ... 他の事業者も同様
```

## 💻 使用方法

### 基本的な使用例

```bash
python main.py --gtfs_dir gtfs/tokyo-metro --from "渋谷" --limit 30
```

### パラメータ

- `--gtfs_dir` (必須): GTFS データのディレクトリパス
- `--from` (必須): 出発駅名（例: "渋谷"、"東京"）
- `--limit` (オプション): 最大乗車時間（分）。デフォルト: 60
- `--output` (オプション): 出力ファイルパス（指定時に JSON/CSV で保存）
- `--format` (オプション): 出力形式（json または csv）。デフォルト: json

### 実行例

#### 例 1: 渋谷から 30 分以内で到達可能な駅を表示

```bash
python main.py --gtfs_dir gtfs/tokyo-metro --from "渋谷" --limit 30
```

**出力例：**
```
📍 GTFS データを読み込み中: gtfs/tokyo-metro
✓ Loaded 163 stops
✓ Loaded 9 routes
...

🔍 出発駅を検索中: "渋谷"
✓ 出発駅: 渋谷 (1000001)

⏱️  30 分以内で到達可能な駅を検索中...

✓ 45 駅が到達可能です

============================================================
駅名                           乗車時間（分）
============================================================
原宿                                       3
明治神宮前                                 5
表参道                                     7
...
```

#### 例 2: 結果を JSON ファイルに保存

```bash
python main.py --gtfs_dir gtfs/merged --from "東京" --limit 60 --output result.json --format json
```

#### 例 3: 結果を CSV ファイルに保存

```bash
python main.py --gtfs_dir gtfs/merged --from "新宿" --limit 45 --output stations.csv --format csv
```

## 📊 出力形式

### JSON 形式

```json
{
  "from_station": "渋谷",
  "from_station_id": "1000001",
  "limit_minutes": 30,
  "reachable_stations": [
    {
      "stop_id": "1000002",
      "name": "原宿",
      "distance": 3
    },
    {
      "stop_id": "1000003",
      "name": "明治神宮前",
      "distance": 5
    }
  ],
  "total_count": 45
}
```

### CSV 形式

```
駅ID,駅名,乗車時間（分）
1000002,原宿,3
1000003,明治神宮前,5
...
```

## 🔧 プロジェクト構成

```
yuuta-trein/
├── main.py              # CLI エントリーポイント
├── gtfs_parser.py       # GTFS ファイル読み込み・解析
├── graph_builder.py     # 駅ネットワークグラフ構築
├── config.py            # 設定ファイル
├── requirements.txt     # Python 依存パッケージ
├── README.md            # このファイル
└── gtfs/                # GTFS データディレクトリ
    ├── tokyo-metro/     # 東京メトロ
    ├── toei/            # 都営地下鉄
    ├── jr-east/         # JR 東日本
    ├── odakyu/          # 小田急電鉄
    └── keio/            # 京王電鉄
```

## 🔌 モジュール説明

### `gtfs_parser.py`

GTFS テキストファイルを読み込み、駅・路線・乗車時間などの情報を Python オブジェクトとして保持します。

**主なクラス:**
- `GTFSParser`: GTFS ファイルを解析

**主なメソッド:**
- `load_all()`: 全 GTFS ファイルを読み込み
- `get_stop_by_name(name)`: 駅名から stop_id を取得
- `get_stop_name(stop_id)`: stop_id から駅名を取得

### `graph_builder.py`

GTFS データから駅ネットワークのグラフを構築します。

**主なクラス:**
- `GraphBuilder`: GTFS データからネットワークグラフを構築

**主なメソッド:**
- `build_graph()`: グラフを構築
- `get_reachable_stations(start, max_time)`: 到達可能な駅を計算

## ⚙️ 設定（config.py）

```python
# 乗換ペナルティ（分）
TRANSFER_PENALTY = 3

# 最短経路計算の設定
DEFAULT_TRANSFER_LIMIT = None  # None = 無制限
MAX_WALKING_TIME = 5  # 駅間の徒歩時間（分）
```

## 📈 アルゴリズム

このツールは以下のアルゴリズムを使用しています：

1. **グラフ構築**: GTFS データを有向グラフに変換
   - ノード: 駅（stop）
   - エッジ: 路線（乗車時間をウェイトとして保持）

2. **最短経路計算**: Dijkstra アルゴリズム
   - NetworkX の `single_source_dijkstra_path_length` を使用
   - 時間計算量: O((V + E) log V)

3. **乗換処理**: transfers.txt から乗換時間を取得
   - 同じ stop_id への複数エッジで最小値を採用

## 🚨 注意事項

- GTFS データは定期的に更新されます。最新のデータを使用してください
- 乗換ペナルティは固定値（デフォルト: 3分）ですが、実際の乗換時間は駅によって異なります
- このツールは乗車時間のみを考慮します。待ち時間は含まれません
- 複数の GTFS ソースを使用する場合、駅 ID の重複に注意が必要です

## 📝 ライセンス

MIT License

## 🤝 貢献

バグ報告や機能提案は Issue として報告してください。

## 📞 サポート

問題が発生した場合は、以下をご確認ください：

1. GTFS ディレクトリが正しく指定されているか
2. GTFS ファイル（stops.txt, routes.txt など）が全て揃っているか
3. Python 3.9 以上がインストールされているか
4. 依存パッケージが全てインストールされているか（`pip install -r requirements.txt`）

---

**Made with ❤️ for 物件探し**
