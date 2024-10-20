
# BibTeX to CSV and Markdown Slides Conversion

This project consists of two Python scripts: 
- `bib2csv.py`: Converts a BibTeX file into a CSV format by translating and summarizing the entries using the OpenAI API.
- `csv2md.py`: Converts the CSV file generated from `bib2csv.py` into a series of Markdown slides and generates a PDF.

## Prerequisites

Before you begin, ensure you have the following software and libraries installed:

1. **Python 3.7+** - You can download it from [here](https://www.python.org/downloads/).
2. **Required Python libraries**:
   - `openai`
   - `bibtexparser`
   - `pydantic`
   - `pandas`
   - `argparse`
   - `concurrent.futures` (part of the Python standard library)
3. **Marp CLI** (for generating PDFs from Markdown) - Install it using npm:
   ```bash
   npm install -g @marp-team/marp-cli
   ```
4. **Custom Marp theme**: If using a custom size or theme for your slides, ensure you have a `customsize.css` file ready for use with Marp.

## Installation

1. Clone the repository (or copy the scripts) to your local machine.

2. Install the required Python libraries:
   ```bash
   pip install openai bibtexparser pydantic pandas
   ```

3. Set up the OpenAI API key and endpoint in your environment variables. 
If you are using Azure OpenAI, add the following lines to your shell profile (e.g., `.bashrc`, `.zshrc`, or `.bash_profile`):
   ```bash
   export AZURE_OPENAI_API_KEY='your_azure_openai_api_key_here'
   export AZURE_OPENAI_ENDPOINT='your_azure_openai_endpoint_here'
   ```
   If you are using the regular OpenAI API, uncomment the relevant lines in the code and set your API key as follows:
   ```bash
   export OPENAI_API_KEY='your_openai_api_key_here'
   ```

## Usage

### 1. Converting BibTeX to CSV

Use the `bib2csv.py` script to translate and summarize your BibTeX file into a CSV format. The script will translate the title and abstract into Japanese and break down the abstract into "background," "purpose," "proposal," "evaluation," and "result" fields.

```bash
python bib2csv.py input_file.bib output_file.csv
```

- **input_file.bib**: The input BibTeX file containing the research papers.
- **output_file.csv**: The output CSV file that will contain the translated and summarized data.

### 2. Converting CSV to Markdown and Generating PDF

Once the CSV is generated, you can use the `csv2md.py` script to convert the CSV data into a Markdown file. It will also generate a PDF using Marp CLI.

```bash
python csv2md.py output_file.csv output_file.md
```

- **output_file.csv**: The CSV file generated from the previous step.
- **output_file.md**: The output Markdown file that will be used to generate the PDF.

To generate a PDF, the script automatically runs the following Marp command (make sure you have Marp installed):
```bash
marp --theme customsize.css --pdf output_file.md -o output_file.pdf
```

### Example

1. Convert `sample.bib` to `sample.csv`:
   ```bash
   python bib2csv.py sample.bib sample.csv
   ```

2. Convert `sample.csv` to `sample.md` and generate `sample.pdf`:
   ```bash
   python csv2md.py sample.csv sample.md
   ```

After running the above commands, you should have a `sample.pdf` file that contains the summarized research papers as a series of slides.