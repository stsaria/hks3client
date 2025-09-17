import json
import cv2
import numpy as np
import argparse

def create_timelapse(input_file, output_file, duration=10, fps=30, out_w=1920, out_h=1080, resize=False):
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
        (out_w, out_h)
    )

    hist_index = 0

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

        if resize:
            # 出力サイズに強制リサイズ
            frame_large = cv2.resize(canvas, (out_w, out_h), interpolation=cv2.INTER_NEAREST)
        else:
            # アスペクト比維持で黒背景に収める
            frame_large = np.zeros((out_h, out_w, 3), dtype=np.uint8)
            scale_w = out_w / width
            scale_h = out_h / height
            scale = min(scale_w, scale_h)
            new_w = int(width * scale)
            new_h = int(height * scale)
            offset_x = (out_w - new_w) // 2
            offset_y = (out_h - new_h) // 2
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
    parser.add_argument("--width", type=int, default=1920, help="出力解像度の横幅")
    parser.add_argument("--height", type=int, default=1080, help="出力解像度の縦幅")
    parser.add_argument("--resize", action="store_true", help="強制リサイズ（黒帯なし）")
    args = parser.parse_args()

    create_timelapse(args.input, args.output, args.duration, args.fps, args.width, args.height, args.resize)

