# Content-generator-Consty-AI


### Project Overview

The **Robust Content Generator** is an end-to-end Python system designed to automate content creation by generating well-structured **summaries** and creative **stories** from a simple user prompt. [cite\_start]It leverages advanced **transformer models** (BART and GPT-2), integrates **real-time web scraping** for data, and outputs the final content into a professionally formatted **PDF report**[cite: 5, 6, 78, 81].

[cite\_start]The system is built with a focus on **resilience** and **robustness**, incorporating multiple fallback mechanisms to ensure a valid output is always provided, even if external services (like Wikipedia or Unsplash) or the core AI models fail[cite: 7, 12, 64].

-----

### Key Features and Technology Stack

| Component | Function | Technology | Details |
| :--- | :--- | :--- | :--- |
| **Content Generation** | [cite\_start]Produces summaries and stories from a prompt[cite: 5]. | **Hugging Face Transformers** | [cite\_start]Uses `facebook/bart-large-cnn` for summarization and `gpt2-medium` for story generation[cite: 11]. |
| **Data Retrieval** | Fetches source content for summarization. | **Wikipedia API & Requests/BeautifulSoup** | [cite\_start]Scrapes content from Wikipedia for reliable, structured data[cite: 10, 49, 79]. |
| **Image Integration** | Fetches a relevant image for the content. | **Unsplash Source API** | [cite\_start]Retrieves high-quality, relevant images for visualization[cite: 79]. |
| **Output Formatting** | Converts generated text and images into a document. | **ReportLab** | [cite\_start]Exports the final result as a paginated, well-designed PDF[cite: 6, 14, 40]. |
| **API & Web Interface**| Serves the generator logic via a web endpoint. | **FastAPI & Jinja2** | [cite\_start]Provides a modern, asynchronous web service and UI rendering[cite: 86]. |

-----

### Resilience and Robustness

[cite\_start]A core design principle of this project is its resilience, which addresses common challenges like unreliable external services and potential model failures[cite: 17, 64].

  * **Model Fallbacks (AI Resilience):** If the BART or GPT-2 models fail to load or generate content (e.g., due to memory constraints), the system defaults to a structured, hardcoded fallback summary or a well-written fallback story ("The Jungle Monarch").
  * **Web Scraping Fallbacks:** If the Wikipedia API request fails, the summarization model is provided with a generic prompt to generate a summary based on its general knowledge, preventing a failure.
  * [cite\_start]**Structured Output:** The code includes logic to structure the raw AI output into clean, readable paragraphs, tackling the challenge of incoherent or unstructured AI text[cite: 20, 53].

-----

### How to Run the Project

The project is packaged as a FastAPI application with a simple web interface.

#### 1\. Prerequisites

You need **Python 3.8+** installed.

#### 2\. Setup Environment

Clone the repository and install the dependencies:

```bash
# Clone the repository (assuming a standard git setup)
git clone <your_repo_url>
cd robust-content-generator-project

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3\. Run the Application

Start the FastAPI server:

```bash
python main.py
```

*The application will be running at `http://127.0.0.1:8000`.*

#### 4\. Usage

1.  Open your browser and navigate to `http://127.0.0.1:8000`.
2.  Enter a **Prompt** (e.g., "Quantum Computing" for a summary, or "A lone pirate's last voyage" for a story).
3.  Select the **Content Type** (`summary` or `story`).
4.  Click the "Generate Content" button.
5.  The system will process the request and provide a link to download the final PDF, which will be saved in the local `output/` directory.

-----

### Code Structure

```
robust-content-generator-project/
├── app/
│   ├── static/           # CSS, JS, etc.
│   ├── templates/
│   │   └── index.html    # Jinja2 template for the UI
│   └── schemas.py        # Pydantic models for data validation (optional, but good practice)
├── output/               # Generated PDFs are saved here
├── temp/                 # Fetched images are temporarily saved here
├── generator.py          # The core RobustContentGenerator class (all generation logic)
├── main.py               # FastAPI entry point, API routes, and setup
└── requirements.txt      # Project dependencies
```

The core logic resides in the `RobustContentGenerator` class within `generator.py`, which handles:

  * `_fetch_web_content`: Scrapes Wikipedia content.
  * `_fetch_image`: Gets an image from Unsplash.
  * `_summarize_with_paragraphs`: Uses BART for summarization and formats the output.
  * `_generate_story_with_paragraphs`: Uses GPT-2 for structured story generation.
  * `_save_pdf`: Uses ReportLab to compile and save the final PDF.

-----

### Model Performance (Estimated)

| Model | Evaluation Metric | Estimated Accuracy |
| :--- | :--- | :--- |
| **BART** | ROUGE-1 | [cite\_start]$0.62 - 0.68$ (High word-level overlap) [cite: 43] |
| **BART** | ROUGE-L | [cite\_start]$0.58 - 0.63$ (Good sequence accuracy) [cite: 44] |
| **GPT-2** | BLEU | [cite\_start]$0.28 - 0.33$ (Acceptable for creative generation) [cite: 45] |
| **GPT-2** | User Rating (est) | [cite\_start]$4.0 - 4.5 / 5$ (Strong user satisfaction) [cite: 46] |
