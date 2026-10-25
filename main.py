from maix import camera, display, image
import math
import time

# ---------- 参数 ----------
CAM_W = 320
CAM_H = 240

# 黑色目标阈值（形状识别用，现场可调）
THRESH = [(0, 80)]
MIN_PIXELS = 180
MIN_AREA = 180

last_sig = ""

def emit(sig):
    """终端打印信号（变化才打印，避免刷屏）"""
    global last_sig
    if sig != last_sig:
        print(sig)
        last_sig = sig

def classify_shape(blob):
    """
    返回: CIRCLE / RECT / TRI / UNKNOWN
    """
    x, y, w, h = blob.rect()
    area = blob.area()

    if w <= 0 or h <= 0:
        return "UNKNOWN"

    perimeter = 2 * (w + h)
    if perimeter <= 0:
        return "UNKNOWN"

    circularity = 4.0 * math.pi * area / (perimeter * perimeter)  # 圆越接近1
    aspect = w / float(h)
    fill_ratio = area / float(w * h)

    # 圆形
    if circularity > 0.72 and 0.75 <= aspect <= 1.30:
        return "CIRCLE"
    # 矩形
    elif fill_ratio > 0.65:
        return "RECT"
    # 三角形
    elif 0.35 <= fill_ratio <= 0.65:
        return "TRI"
    else:
        return "UNKNOWN"

def run():
    print("app.run() start")
    cam = camera.Camera(CAM_W, CAM_H)
    disp = display.Display()

    while True:
        try:
            img = cam.read()

            # 默认无识别
            sig = "SIG,NONE,0"
            show_type = "NONE"
            show_val = "0"

            # 1) 优先识别二维码
            qrs = img.find_qrcodes()
            if len(qrs) > 0:
                q = qrs[0]  # 简化：取第一个
                img.draw_rect(q.x(), q.y(), q.w(), q.h(), image.COLOR_RED, 2)

                payload = "UNKNOWN"
                try:
                    payload = q.payload()
                except:
                    try:
                        payload = q.data
                    except:
                        pass

                show_type = "QR"
                show_val = str(payload)
                sig = "SIG,QR,{}".format(show_val)
                emit(sig)

            else:
                # 2) 识别形状（矩形/圆形/三角形）
                blobs = img.find_blobs(
                    THRESH,
                    pixels_threshold=MIN_PIXELS,
                    area_threshold=MIN_AREA,
                    merge=True
                )

                if len(blobs) > 0:
                    b = max(blobs, key=lambda t: t.area())
                    shape = classify_shape(b)

                    x, y, w, h = b.rect()
                    img.draw_rect(x, y, w, h, image.COLOR_GREEN, 2)
                    img.draw_cross(b.cx(), b.cy(), image.COLOR_GREEN, 2)

                    show_type = "SHAPE"
                    show_val = shape
                    sig = "SIG,SHAPE,{}".format(shape)
                    emit(sig)
                    print("识别形状:", shape)
                else:
                    emit(sig)

            # 3) 屏幕显示
            img.draw_string(8, 8, "TYPE: {}".format(show_type), image.COLOR_WHITE, 2)
            img.draw_string(8, 36, "VAL : {}".format(show_val[:24]), image.COLOR_WHITE, 1)
            img.draw_string(8, 216, sig[:34], image.COLOR_WHITE, 1)

            disp.show(img)

        except Exception as e:
            print("loop error:", e)
            time.sleep(0.1)