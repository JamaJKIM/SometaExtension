# Someta Math Helper

Someta Math Helper is a Chrome extension that provides on-demand math assistance for students. The system consists of two parts:

1. **Chrome Extension**: A floating widget that can be activated on any webpage to take screenshots of math problems or ask questions directly.
2. **Backend API (Socrato)**: Processes math questions and screenshots to provide helpful explanations and solutions.

## Project Structure

```
/
├── chrome-extension/     # Chrome extension source code
│   ├── manifest.json     # Extension configuration
│   ├── popup.html        # Extension popup interface
│   ├── css/              # Styles for the extension
│   ├── js/               # JavaScript for the extension
│   └── images/           # Extension icons and assets
│
└── backend/              # Backend API source (Socrato)
    ├── main.py           # Main Flask application
    ├── processors/       # Content processing modules
    ├── models/           # Data models
    ├── services/         # External service connectors
    ├── routes/           # API route definitions
    └── tests/            # Test cases
```

## Getting Started

### Chrome Extension

Follow the instructions in the [Chrome Extension README](./chrome-extension/README.md) to install and use the extension.

### Backend API

The backend API is built with Flask and handles processing math problems, screenshots, and serving AI-powered responses.

#### Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add necessary API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

4. Run the development server:
   ```bash
   python backend/main.py
   ```

## Development

### Chrome Extension Development

Edit the files in the `chrome-extension` directory to modify the extension's functionality and appearance.

### Backend Development

The backend uses Flask for the API and leverages OpenAI for processing math problems.

## Deployment

### Chrome Extension

The Chrome extension can be published to the Chrome Web Store following the [official guidelines](https://developer.chrome.com/docs/webstore/publish/).

### Backend API

The backend API can be deployed to platforms like Heroku, Render, or Vercel. Environment variables should be set accordingly in the deployment environment.
