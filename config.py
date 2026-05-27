"""
設定ファイル
"""

# GTFS データのデフォルトディレクトリ
GTFS_DIR = './gtfs'

# 乗換ペナルティ（分）
# 駅での乗り換え時に加算される時間
TRANSFER_PENALTY = 3

# 最短経路計算の設定
DEFAULT_TRANSFER_LIMIT = None  # None = 乗換回数制限なし

# 駅間の最大徒歩時間（分）
# これを超える駅間は接続されないとみなす
MAX_WALKING_TIME = 5

# デバッグモード
DEBUG = False

# 出力フォーマット
OUTPUT_FORMATS = ['json', 'csv']

# デフォルト出力フォーマット
DEFAULT_OUTPUT_FORMAT = 'json'
