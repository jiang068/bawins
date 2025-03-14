import os
import json
from itertools import cycle, product
from typing import Optional
from PIL import Image, ImageDraw
import cv2
from tqdm import tqdm
import numpy as np


# 定义 frame_to_boxes 函数
def frame_to_boxes(im: Image, name):
    w, h = im.size
    ratio = w / h

    # greyscale
    im = im.convert("L")
    # resize
    im = im.resize((max_width, int(max_width / ratio)))
    # threshold
    im = im.point(lambda p: 255 if p > threshold else 0)
    # mono
    im = im.convert("1")

    # find largest region via brute force
    # tqdm.write(f'{im.width=} {im.height=}')
    pixels = im.load()
    visited = np.zeros(im.size, dtype=bool)

    # visualisation
    boxes = []
    work = im.copy().convert("RGB")
    draw = ImageDraw.Draw(work)
    fills = cycle(
        [
            "red",
            "green",
            "blue",
            "orange",
            "yellow",
            "purple",
            "pink",
            "cyan",
            "gray",
            "brown",
            "maroon",
            "hotpink",
            "gold",
            "chocolate",
            "green",
        ]
    )

    while False in visited:
        largest: Optional[tuple[int, int, int, int]] = None  # x, y, width, height

        for x, y in product(range(im.width), range(im.height)):
            if visited[x, y] or pixels[x, y] == 0:
                visited[x, y] = True
                continue

            sublargest: Optional[tuple[int, int]] = None
            widest = im.width - x  # optimise

            if widest == 0:
                continue

            # row by row
            for h in range(im.height - y):
                # search until black pixel
                for w in range(widest + 1):
                    if (
                        (w == widest)
                        or visited[x + w, y + h]
                        or pixels[x + w, y + h] == 0
                    ):
                        break

                # tqdm.write(f'tapped out {x} {y} {w} {h} {widest}')

                widest = min(widest, w)
                if sublargest is None or (sublargest[0] * sublargest[1]) < (
                    (w) * (h + 1)
                ):
                    sublargest = [w, h + 1]

            if largest is None or (largest[2] * largest[3]) < (
                sublargest[0] * sublargest[1]
            ):
                largest = [x, y, *sublargest]

            # break # debug

        # tqdm.write(f'{largest=}')

        # Generally only occurs when the entire frame is black
        if largest is None:
            break

        visited[
            largest[0] : largest[0] + largest[2], largest[1] : largest[1] + largest[3]
        ] = True

        boxes.append(largest)

        # [(x0, y0), (x1, y1)] from [x0, y0, w, h], where the bounding box is inclusive
        box = [
            (largest[0], largest[1]),
            (largest[0] + largest[2] - 1, largest[1] + largest[3] - 1),
        ]
        draw.rectangle(box, fill=next(fills))

        # work.show() # debug
        # exit()

        # break # debug

    tqdm.write(f"{len(boxes)=}")

    # im.show()
    # work.show()

    # 检查 frames 目录是否存在，如果不存在则创建
    if not os.path.exists(out):
        os.makedirs(out)

    work.save(os.path.join(out, f"{name}.png"))

    return boxes


# 检查 assets 文件夹是否存在，如果不存在则创建
if not os.path.exists('assets'):
    os.makedirs('assets')

# 初始化变量
inp = "1.mp4"
out = "frames"
max_width = 64
threshold = 255 * 0.4

# 检查 boxes.json 文件是否存在
if os.path.exists('assets/boxes.json'):
    # 如果 boxes.json 文件存在，直接使用
    try:
        with open('assets/boxes.json') as f:
            all_boxes = json.load(f)
        print("boxes.json already exists. Skipping video processing.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in assets/boxes.json.")
        exit(1)
else:
    all_boxes = []
    # 打开视频文件
    cap = cv2.VideoCapture(inp)

    # 检查视频文件是否成功打开
    if not cap.isOpened():
        print(f"Error opening video file: {inp}")
        exit(1)

    # 获取视频的总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prog = tqdm(total=total_frames)

    try:
        image_counter = 0
        while cap.isOpened():
            ret, cv2_im = cap.read()
            if ret:
                # 将 OpenCV 图像转换为 Pillow 图像
                converted = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
                pil_im = Image.fromarray(converted)

                # 处理当前帧，生成矩形框数据
                boxes = frame_to_boxes(pil_im, f"{image_counter}")

                all_boxes.append(boxes)

                image_counter += 1
                prog.update()
            else:
                break

    except Exception as e:
        print(f"Error processing video: {e}")

    finally:
        # 释放视频资源
        cap.release()
        # 删除frames目录
        if os.path.exists(out):
            for file in os.listdir(out):
                os.remove(os.path.join(out, file))
            os.rmdir(out)

        # 保存 boxes.json
        try:
            with open("assets/boxes.json", "w") as f:
                json.dump(all_boxes, f)
            print("\nSuccessfully saved boxes.json")
        except Exception as e:
            print(f"\nError writing to boxes.json: {e}")
            # 将所有帧的矩形框数据保存到 boxes.json 文件中

# 将 boxes.json 转换为 boxes.bin
try:
    print("\nSerialising box-o'-bytes to boxes.bin")
    with open("assets/boxes.bin", "wb") as f:
        for frame in all_boxes:
            for window in frame:
                f.write(bytes(window))
                # null window signifies new frame
            f.write(bytes([0, 0, 0, 0]))
except Exception as e:
    print(f"\nError writing to boxes.bin: {e}")
