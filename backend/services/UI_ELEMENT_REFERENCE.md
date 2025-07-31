# UI Element Class IDs Reference

This document provides a reference for the UI element class IDs used in the test flows.

## Class ID Mapping

Based on the classes.json file, here are the available UI element classes:

| Class ID | Class Name | Description |
|----------|------------|-------------|
| 0 | FeatureDisplay | Feature information display |
| 1 | SpinButton | Main spin button |
| 2 | AutoPlayButton | AutoPlay toggle button |
| 3 | QuickSpin | Quick spin feature button |
| 4 | QuickSpinOff | Quick spin off button |
| 5 | TurboSpin | Turbo spin feature button |
| 6 | PurchaseButton | Purchase/buy feature button |
| 7 | BetSettingsButton | Bet configuration button |
| 8 | Slider | Bet amount slider |
| 9 | SettingsButton | General settings button |
| 10 | PaytableButton | Paytable information button |
| 11 | CloseButton | Close/dismiss button |
| 12 | Scrollbar | Scrollable content bar |
| 13 | StartAutoPlayBtn | Start AutoPlay button |
| 14 | StudioLogo | Game studio logo |
| 15 | HamburgerButton | Menu/hamburger button |
| 16 | QuickBets | Quick bet selection buttons |

## Current Test Flows

### Multiple Spin Test
**Flow:** `[9, 7, 1, 1, 1, 1, 1]`
**Description:** Settings -> Bet Settings -> Spin Button (5 times)

### Banking Test
**Flow:** `[9, 7, 6]`
**Description:** Settings -> Bet Settings -> Purchase Button

### Playcheck Test
**Flow:** `[9, 10, 1]`
**Description:** Settings -> Paytable -> Spin Button

### Max Bet Limit Test
**Flow:** `[7, 8, 1]`
**Description:** Bet Settings -> Slider -> Spin Button

### Session Reminder Test
**Flow:** `[9, 11, 1, 1, 1]`
**Description:** Settings -> Close Button -> Spin Button (3 times)

### Practice Play Test
**Flow:** `[9, 2, 13, 1]`
**Description:** Settings -> AutoPlay Button -> Start AutoPlay -> Spin Button

## Usage

1. **Test Services** return a `test_flow` array containing class IDs in execution order
2. **Frontend** uses this array to call the **DetectService**
3. **DetectService** processes the image and returns click coordinates for each class ID
4. **Frontend** executes the clicks in the specified order

## DetectService API

### Request Format
```json
{
  "test_type": "UI Element Detection",
  "game_url": "http://example.com",
  "image_data": "base64_encoded_image",
  "additional_params": {
    "class_ids": [1, 2, 3]
  }
}
```

### Response Format
```json
{
  "status": "success",
  "results": {
    "click_targets": [
      {
        "class_id": 1,
        "class_name": "SpinButton",
        "click_x": 400.5,
        "click_y": 300.2,
        "bounding_box": {
          "x1": 350.0,
          "y1": 275.0,
          "x2": 450.0,
          "y2": 325.0
        },
        "confidence": 0.95,
        "width": 100.0,
        "height": 50.0
      }
    ]
  }
}
```
