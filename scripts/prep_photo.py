"""Prep a photo for ASCII conversion.

1. remove background (rembg; falls back to GrabCut if the model can't download)
2. crop to a head-and-shoulders square
3. boost local contrast (CLAHE) + lift shadows
4. save grayscale source-prepped.png and a matching mask source-mask.png

Usage: python scripts/prep_photo.py path/to/photo.jpg
"""
import sys
import cv2
import numpy as np
from PIL import Image


def cutout_rembg(img):
    """Segment at reduced size with a small human-segmentation model
    (light on RAM), then scale the mask back up."""
    from rembg import remove, new_session
    session = new_session("u2net_human_seg")
    small = img.convert("RGB")
    scale = 1024 / max(small.size)
    if scale < 1:
        small = small.resize((int(small.width * scale), int(small.height * scale)))
    alpha = np.array(remove(small, session=session))[:, :, 3]
    return cv2.resize(alpha, img.size, interpolation=cv2.INTER_LINEAR)


def cutout_grabcut(img):
    bgr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    rect = (int(w * 0.18), int(h * 0.28), int(w * 0.64), int(h * 0.70))
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, rect, bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    return np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)


def main(path):
    img = Image.open(path)
    img = Image.fromarray(np.array(img.convert("RGB")))
    try:
        alpha = cutout_rembg(img)
        print("background removed with rembg")
    except Exception as e:  # offline / model blocked
        print("rembg failed (%s) -> GrabCut fallback" % e)
        alpha = cutout_grabcut(img)

    # tight head-and-shoulders crop: square, centred on the head
    ys, xs = np.where(alpha > 128)
    x0, x1, y0 = xs.min(), xs.max(), ys.min()
    body_w = x1 - x0
    head_rows = (ys < y0 + body_w * 0.28)
    cx = int(xs[head_rows].mean())
    side = int(body_w * 0.80)
    left = min(max(0, cx - int(side * 0.52)), img.width - side)
    top = max(0, y0 - int(side * 0.05))
    box = (left, top, min(img.width, left + side), min(img.height, top + side))

    rgb = np.array(img.crop(box))
    a = alpha[box[1]:box[3], box[0]:box[2]]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # local contrast + lift shadows so dark hair/blazer keep some structure
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = (255 * (gray / 255.0) ** 0.62).astype(np.uint8)

    a = cv2.GaussianBlur(a, (5, 5), 0)
    out = np.where(a > 110, gray, 255).astype(np.uint8)  # composite on white

    cv2.imwrite("source-prepped.png", out)
    cv2.imwrite("source-mask.png", (a > 110).astype(np.uint8) * 255)
    print("wrote source-prepped.png + source-mask.png", out.shape)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
