import json
import random
import time
import argparse

def generate_sketch_history(
    width=200, 
    height=200, 
    num_events=500, 
    start_time=None, 
    max_interval=10,
    output_file="sketch_history.json"
):
    """
    テスト用のランダムsketch_history.jsonを生成する
    - width, height: キャンバスのサイズ
    - num_events: 履歴の件数
    - start_time: 開始時刻 (Noneなら現在時刻)
    - max_interval: イベント間の最大秒数
    - output_file: 出力ファイル
    """
    if start_time is None:
        start_time = int(time.time())

    history = []
    current_ts = start_time

    for _ in range(num_events):
        current_ts += random.randint(1, max_interval)
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        history.append({"ts": current_ts, "x": x, "y": y, "r": r, "g": g, "b": b})

    data = {
        "range": {"x": width, "y": height},
        "history": history
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"{output_file} を生成しました ({num_events} events)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ランダム sketch_history.json 生成ツール")
    parser.add_argument("--width", type=int, default=200, help="キャンバス幅")
    parser.add_argument("--height", type=int, default=200, help="キャンバス高さ")
    parser.add_argument("--num-events", type=int, default=500, help="生成する履歴の件数")
    parser.add_argument("--start-time", type=int, default=None, help="開始時刻のUnixタイムスタンプ")
    parser.add_argument("--max-interval", type=int, default=10, help="イベント間の最大秒数")
    parser.add_argument("--output", type=str, default="sketch_history.json", help="出力ファイル名")

    args = parser.parse_args()

    generate_sketch_history(
        width=args.width,
        height=args.height,
        num_events=args.num_events,
        start_time=args.start_time,
        max_interval=args.max_interval,
        output_file=args.output
    )
