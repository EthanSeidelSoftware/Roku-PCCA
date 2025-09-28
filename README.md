# Roku PC Control App (PCCA)

The **Roku PC Control App (PCCA)** lets you control your Roku device from your Windows PC using your keyboard.  
It includes features like keyboard-to-remote mapping, HDMI input selection, auto wake on activity, and a simple GUI built with Tkinter.

---

## ✨ Features
- 🎮 **Keyboard Remote** – Map your keyboard keys to Roku remote commands.  
- 📺 **HDMI Input Selection** – Optionally switch to a specific HDMI input when waking the TV.  
- 🔄 **Device Discovery** – Automatically scan for Roku devices on your local network.  
- 💤 **Idle Detection** – Wakes your Roku when the PC returns from idle.  
- 🖥️ **GUI Application** – Built with Tkinter for an easy-to-use interface.  
- 📋 **App List** – Print installed Roku apps and IDs to the console.  

---

## ⌨️ Keyboard Controls
| Key          | Roku Command   |
|--------------|----------------|
| ↑ / ↓ / ← / → | Up/Down/Left/Right |
| Enter / Space | Select |
| Backspace    | Back |
| Home         | Home |
| P            | Play/Pause |
| S            | Stop |
| R            | Rewind |
| F            | Fast Forward |
| M            | Mute |
| End          | Stop capturing |

---

## 🛠️ Requirements
- Python 3.8+  
- Windows (for idle detection via `ctypes`)  
- Roku device connected to the same local network  

### Python dependencies
Install with pip:
```bash
pip install roku pynput
