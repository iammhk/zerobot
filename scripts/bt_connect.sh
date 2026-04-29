#!/bin/bash
# bt_connect.sh - Connect ZEB-CLIPPER and switch to HFP (mic-enabled) mode.
# Run this script each time before using the voice agent.

# Detect the first connected bluetooth card
BT_CARD=$(pactl list cards short | grep bluez_card | head -n 1 | awk '{print $2}')

if [ -z "$BT_CARD" ]; then
    echo "⚠️ No connected Bluetooth audio device found."
    exit 1
fi

# Extract MAC from card name (bluez_card.XX_XX_XX_XX_XX_XX)
BT_MAC_UNDERSCORES=${BT_CARD#bluez_card.}
BT_MAC=${BT_MAC_UNDERSCORES//_/:}
BT_SOURCE="bluez_source.${BT_MAC_UNDERSCORES}.handsfree_head_unit"

echo "🔵 Detected Bluetooth device: $BT_MAC"
echo "🎤 Switching to HFP profile (enables microphone)..."
pactl set-card-profile "$BT_CARD" handsfree_head_unit
sleep 1

echo "🔊 Setting as default audio source..."
pactl set-default-source "$BT_SOURCE"

echo "✅ Done! Run 'uv run zerobot voice' to start."
