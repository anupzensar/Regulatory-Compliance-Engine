# YOLO Models Directory

This directory contains YOLO model files (.pt format) used for object detection in the regulatory compliance engine.

## Expected Files

- `best.pt` - Main YOLO model file (trained weights)
- `yolov8n.pt` - YOLOv8 nano model (lightweight option)
- `yolov8s.pt` - YOLOv8 small model (balanced option)
- `yolov8m.pt` - YOLOv8 medium model (higher accuracy)

## Usage

The `MultipleSpinService` automatically loads the model from `best.pt` when initialized. Place your trained YOLO model file as `best.pt` in this directory.

## Model Training

If you need to train a custom YOLO model:

1. Prepare your dataset with labeled images
2. Use the ultralytics library to train your model
3. Save the trained weights as `best.pt`
4. Place the file in this directory

## File Format

- Format: PyTorch (.pt)
- Framework: Ultralytics YOLO
- Compatible versions: YOLOv8, YOLOv5
