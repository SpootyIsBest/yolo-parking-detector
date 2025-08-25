# 🚦 YOLO Parking Sign Detector

Detects **Slovakian parking signs** in images using [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics).  
Runs fully inside Docker: provide input images in a folder, get structured JSON + a CSV summary out.  

---

## ✨ Features
- Recursive folder scanning under `/data-in`
- Per-image JSON outputs with bounding boxes & metadata
- Aggregate CSV summary (`detection_summary.csv`)
- Works out-of-the-box with Docker
- Self-contained: ships with trained `best.pt` weights

---

## 🚀 Quick Start

### 1. Build image
```bash
git clone https://github.com/<your-username>/yolo-parking-detector.git
cd yolo-parking-detector
docker build -t yolo-parking .
```

### 2. Prepare folders
```bash
mkdir -p data-in data-out
# put your images in ./data-in (subfolders allowed)
```

### 3. Run detection
```bash
docker run --rm   -v "$(pwd)/data-in:/data-in:ro"   -v "$(pwd)/data-out:/data-out"   yolo-parking
```

Results:
- JSON files in `data-out/` (mirroring the input tree)
- `data-out/detection_summary.json`

---

## 🔎 Example Output

**`detection_summary.json`**
```
{
    "summary": {
        "total_images": 401,
        "confidence_threshold": 0.5,
        "distribution": [
            {
                "signs": 0,
                "image_count": 13
            },
            {
                "signs": 1,
                "image_count": 371
            },
            {
                "signs": 2,
                "image_count": 17
            }
        ]
    },
    "config": {
        "model_path": "best.pt"
    }
}
```

**JSON (per image)**
```json
{
  "predictions": [
    {
      "x": 123.4,
      "y": 234.5,
      "width": 45.6,
      "height": 67.8,
      "confidence": 0.987,
      "class": "slovakian parking sign",
      "class_id": 0,
      "detection_id": "4f832edb-3c7c-4a8a-9e6c-45d236c471fa"
    }
  ]
}
```

---

## ⚙️ Configuration

Environment variables (overridable via `-e` in `docker run`):

| Variable               | Default         | Description                        |
|------------------------|-----------------|------------------------------------|
| `MODEL_PATH`           | `/app/best.pt`  | Path to model weights              |
| `CONFIDENCE_THRESHOLD` | `0.5`           | Minimum confidence for detections  |
| `INPUT_ROOT`           | `/data-in`      | Input folder (mounted from host)   |
| `OUTPUT_ROOT`          | `/data-out`     | Output folder (mounted from host)  |

Example with threshold override:
```bash
docker run --rm   -v "$(pwd)/data-in:/data-in:ro"   -v "$(pwd)/data-out:/data-out"   -e CONFIDENCE_THRESHOLD=0.6   yolo-parking
```

---

## 📂 Project Structure
```
yolo-parking-detector/
├── app/main.py          # main detector script
├── best.pt              # trained YOLO weights
├── Dockerfile           # container build
├── requirements.txt     # Python deps
├── LICENSE              # AGPL-3.0-only
├── NOTICE.md            # 3rd-party attributions
└── README.md            # this file
```

---

## ⚖️ License

Licensed under **AGPL-3.0-only**. See [LICENSE](LICENSE).  
If you run this software as a network service, you must provide full source (including Dockerfile and build instructions) to users of that service.  

Model weights (`best.pt`) are included and were trained by **Krystof Dolecek** with rights for redistribution and commercial use. See [NOTICE.md](NOTICE.md) for third-party components (Ultralytics YOLOv8, PyTorch, OpenCV).  

---

## 🙏 Acknowledgements
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) — detection engine  
- [PyTorch](https://pytorch.org/) — deep learning backend  
- [OpenCV](https://opencv.org/) — image handling  
