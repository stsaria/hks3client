import json
import cv2
import numpy as np
import argparse

OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080

def create_timelapse(input_file, output_file, duration=10, fps=30):
    # JSON読み込み
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "range" in data and "history" in data:
        width, height = data["range"]["x"], data["range"]["y"]
        history = sorted(data["history"], key=lambda h: h["ts"])
    else:
        history = sorted(data, key=lambda h: h["ts"])
        width, height = 200, 200

    if not history:
        raise ValueError("履歴データが空です")

    t_min, t_max = history[0]["ts"], history[-1]["ts"]
    total_duration = t_max - t_min
    if total_duration <= 0:
        raise ValueError("履歴の時間が不正です")

    frame_count = duration * fps
    ts_per_frame = total_duration / frame_count

    # 元キャンバス
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

    # VideoWriter
    out = cv2.VideoWriter(
        output_file,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (OUTPUT_WIDTH, OUTPUT_HEIGHT)
    )

    hist_index = 0

    # 拡大比率計算（アスペクト比維持）
    scale_w = OUTPUT_WIDTH / width
    scale_h = OUTPUT_HEIGHT / height
    scale = min(scale_w, scale_h)  # キャンバス全体が収まる最大スケール
    new_w = int(width * scale)
    new_h = int(height * scale)
    offset_x = (OUTPUT_WIDTH - new_w) // 2
    offset_y = (OUTPUT_HEIGHT - new_h) // 2

    for frame_idx in range(frame_count):
        virtual_ts = t_min + frame_idx * ts_per_frame
        # このフレームに反映されるピクセルを描画
        while hist_index < len(history) and history[hist_index]["ts"] <= virtual_ts:
            h = history[hist_index]
            x, y = h["x"], h["y"]
            r, g, b = h["r"], h["g"], h["b"]
            if 0 <= x < width and 0 <= y < height:
                canvas[y, x] = (b, g, r)
            hist_index += 1

        # 高解像度キャンバス（黒背景）
        frame_large = np.zeros((OUTPUT_HEIGHT, OUTPUT_WIDTH, 3), dtype=np.uint8)

        # キャンバスを拡大して黒背景に貼る
        canvas_resized = cv2.resize(canvas, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        frame_large[offset_y:offset_y+new_h, offset_x:offset_x+new_w] = canvas_resized

        out.write(frame_large)

    out.release()
    print(f"動画を出力しました: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="入力 JSON ファイル")
    parser.add_argument("output", help="出力 MP4 ファイル")
    parser.add_argument("--duration", type=int, default=10, help="動画に収める秒数")
    parser.add_argument("--fps", type=int, default=30, help="FPS")
    args = parser.parse_args()

    create_timelapse(args.input, args.output, args.duration, args.fps)
