# Someta Math Helper Chrome Extension

A Chrome extension that provides a floating, draggable math helper widget on any webpage.

## Features

- **Floating Chat Widget**: A movable widget that can be positioned anywhere on the page
- **Screenshot Integration**: Take screenshots of math problems for instant AI analysis
- **Simple Interface**: Minimalist design focused on quick math help
- **Customization Options**: Dark mode and minimized state settings
- **Secure API Integration**: Uses Socrato's backend for math assistance

## Installation (Development Mode)

1. Download or clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right corner
4. Click "Load unpacked" and select the `chrome-extension` folder
5. The extension is now installed and ready to use

## Usage

1. Click the Someta Math Helper icon in your Chrome toolbar
2. Click "Activate Widget" in the popup
3. The widget will appear on the current webpage
4. To get help with a math problem:
   - Click the screenshot button (📷) to capture the problem, or
   - Type your question directly in the text input
5. Drag the header to reposition the widget
6. Use the minimize button (−) to collapse the widget
7. Use the close button (×) to remove the widget from the page

## Configuration

Click the extension icon and use the options panel to:
- Enter your API key (if required)
- Set the widget to start minimized
- Enable dark mode

## Connecting to Backend

The extension connects to the Socrato API for math assistance. The API endpoint is configurable in the `background.js` file.

## Development

### Project Structure

```
chrome-extension/
├── manifest.json       # Extension configuration
├── popup.html          # Extension popup interface
├── css/
│   ├── popup.css       # Styles for the popup
│   └── widget.css      # Styles for the floating widget
├── js/
│   ├── background.js   # Background service worker
│   ├── contentScript.js # Content script for injecting the widget
│   └── popup.js        # JavaScript for the popup
└── images/             # Extension icons
```

### Customization

- Edit `widget.css` to change the appearance of the chat widget
- Modify `contentScript.js` to change widget behavior
- Update `background.js` to adjust API communication 