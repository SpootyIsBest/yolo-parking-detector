import os
import json
import uuid
import shutil
from pathlib import Path
from collections import Counter
from ultralytics import YOLO

# ==============================
# CONFIG (env-aware)
# ==============================
MODEL_PATH = os.getenv("MODEL_PATH", "/app/best.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))
SUMMARY_JSON = "detection_summary.json"
USE_GPU = os.getenv("USE_GPU", "false").lower() in ("1", "true", "yes")
SAVE_SUMMARY = os.getenv("SAVE_SUMMARY", "false").lower() in ("1", "true", "yes")

DEVICE = "cuda" if USE_GPU else "cpu"


# ==============================
# HELPERS
# ==============================
def find_images_recursive(root: str):
    root_path = Path(root)
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
    files = [str(p) for p in root_path.rglob("*") if p.suffix.lower() in exts]
    files.sort()
    return files


def clear_dir_contents(dirpath: str):
    """Delete only contents of dirpath (safe for bind mounts)."""
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath, exist_ok=True)
        return
    for entry in os.scandir(dirpath):
        try:
            if entry.is_dir(follow_symlinks=False):
                shutil.rmtree(entry.path)
            else:
                os.unlink(entry.path)
        except Exception as e:
            print(f"Warning: couldn’t remove {entry.path}: {e}")


# ==============================
# FUNCTION TO PROCESS ONE IMAGE
# ==============================
def process_image(model, image_path, counts, output_dir):
    results = model.predict(image_path, conf=CONFIDENCE_THRESHOLD, device=DEVICE)
    boxes = results[0].boxes

    predictions = []
    for box in boxes:
        xywh = box.xywh[0].tolist()
        confidence = float(box.conf[0].item())
        cls_id = int(box.cls[0].item())

        predictions.append({
            "x": xywh[0],
            "y": xywh[1],
            "width": xywh[2],
            "height": xywh[3],
            "confidence": round(confidence, 3),
            "class": "slovakian parking sign",
            "class_id": cls_id,
            "detection_id": str(uuid.uuid4())
        })

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, base_name + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"predictions": predictions}, f, indent=4, ensure_ascii=False)

    counts[len(predictions)] += 1
    print(f"Processed {image_path} → {json_path} (found {len(predictions)} signs)")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Detect Slovakian parking signs.")
    parser.add_argument("--image", help="Path to image file")
    parser.add_argument("--folder", default=os.getenv("INPUT_ROOT"),
                        help="Path to folder of images (recursively searched). Defaults to $INPUT_ROOT if set.")
    parser.add_argument("--out", default=os.getenv("OUTPUT_ROOT", "results"),
                        help="Output folder for JSON results (defaults to $OUTPUT_ROOT or ./results)")
    parser.add_argument("--save-summary", action="store_true",
                        help="Enable saving detection_summary.json (can also use SAVE_SUMMARY env)")
    args = parser.parse_args()

    # final toggle (CLI overrides env)
    save_summary = args.save_summary or SAVE_SUMMARY

    print(f"Loading model from {MODEL_PATH} on {DEVICE} (USE_GPU={USE_GPU})")
    model = YOLO(MODEL_PATH)

    clear_dir_contents(args.out)

    counts = Counter()
    total_images = 0

    if args.image:
        process_image(model, args.image, counts, args.out)
        total_images = 1
    elif args.folder:
        image_files = find_images_recursive(args.folder)
        if not image_files:
            print(f"No images found in {args.folder} (including subfolders).")
            raise SystemExit(0)
        for img_path in image_files:
            process_image(model, img_path, counts, args.out)
        total_images = len(image_files)
    else:
        print("Please specify either --image or --folder (or set INPUT_ROOT).")
        raise SystemExit(2)

    # only save summary if enabled
    if counts and save_summary:
        max_signs = max(counts.keys())
        distribution = [{"signs": i, "image_count": counts[i]} for i in range(max_signs + 1)]
        summary_payload = {
            "summary": {
                "total_images": total_images,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
                "device": DEVICE,
                "distribution": distribution
            },
            "config": {"model_path": MODEL_PATH}
        }
        summary_path = os.path.join(args.out, SUMMARY_JSON)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=4, ensure_ascii=False)

        print("\n=== Detection Summary ===")
        for bucket in distribution:
            print(f"{bucket['signs']} sign(s): {bucket['image_count']} image(s)")
        print(f"\nSummary saved to {summary_path}")
    else:
        print("\nSummary not saved (SAVE_SUMMARY=false)")