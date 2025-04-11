# Medical Analysis Assistant

A web application that uses AI models to analyze patient medical data, suggest potential diagnoses, and recommend appropriate medications.

## Disclaimer

**IMPORTANT**: This tool is for educational and demonstration purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## Features

- Upload patient medical data in PDF, DOCX, or TXT format
- Analyze data using Anthropic Claude to identify potential medical conditions
- Receive medication recommendations based on identified conditions
- View detailed reasoning for each diagnosis
- Print-friendly results page

## API Key Setup

This application requires an Anthropic API key. Set it up using one of the following methods:

### Method 1: Environment Variable (Recommended)

Set the `ANTHROPIC_API_KEY` environment variable:

```bash
# Linux/Mac
export ANTHROPIC_API_KEY=your_api_key_here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_api_key_here"
```

### Method 2: Direct Edit (Not recommended for production)

Edit the API key in the file `app/analyzer.py`:

```python
# Replace "your_api_key_here" with your actual API key
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your_api_key_here")
```

> **Note**: Without a valid API key, the application will run in "mock mode" and provide simulated responses for testing.

## Requirements

- Python 3.8+

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/medical-gpt-assistant.git
   cd medical-gpt-assistant
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```
   python run.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

3. Upload a patient medical file

4. View the analysis results

## File Format Support

- PDF (.pdf)
- Microsoft Word (.docx)
- Plain text (.txt)

## Privacy and Security

- Patient data is processed locally and is not stored after analysis
- No data is sent to any third-party services other than OpenAI's API

## License

This project is licensed under the MIT License - see the LICENSE file for details.