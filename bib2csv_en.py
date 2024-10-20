import openai
import csv
import json
import bibtexparser
import os
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Define the output format class
class PaperSummary(BaseModel):
    background: str
    purpose: str
    proposal: str
    evaluation: str
    result: str

def process_entry(entry):
    title = entry.get('title', '')
    authors = entry.get('author', '')
    abstract = entry.get('abstract', '')
    doi = entry.get('doi', '')

    # Prepare the prompt for ChatGPT
    prompt = f"""
    Below is the title and abstract of a paper. Please summarize it into five sections: "Background", "Purpose", "Proposal", "Evaluation", and "Result", each in a single sentence of max 100 characters. Highlight interesting words in a sentence from a researcher's perspective by enclosing them in ** **.
    
    Title:
    {title}
    Abstract:
    {abstract}
    
    Output in JSON format as follows:
    {{
        "background": "Background (overview of the context, the problem or issue being addressed, why it is important, and why a solution is needed)",
        "purpose": "Purpose (the problem the research aims to solve and its significance in one sentence)",
        "proposal": "Proposal (summary of the proposed technology/method/software/phenomenon/hypothesis)",
        "evaluation": "Evaluation (overview of the experimental approach or analysis methods used to test the hypothesis)",
        "result": "Result (conclusions or insights obtained)"
    }}
    """

    # Use OpenAI API for summarization and information extraction
    try:
        response = openai.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are an assistant that performs translation and summarization of texts."},
                {"role": "user", "content": prompt}
            ],
            response_format=PaperSummary
        )

        # Retrieve the API result and handle it as a class instance
        parsed_reply = PaperSummary.parse_raw(response.choices[0].message.content)

        # Return data in dictionary format
        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'background': parsed_reply.background,
            'purpose': parsed_reply.purpose,
            'proposal': parsed_reply.proposal,
            'evaluation': parsed_reply.evaluation,
            'result': parsed_reply.result,
            'doi': doi
        }

    except Exception as e:
        print(f"Error processing abstract for '{title}': {e}")
        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'background': '',
            'purpose': '',
            'proposal': '',
            'evaluation': '',
            'result': '',
            'doi': doi
        }

def translate_and_process_papers(input_bib, output_csv):
    # Load the BibTeX file
    with open(input_bib, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    # Create an empty list based on the number of entries to maintain input order
    data_list = [None] * len(bib_database.entries)

    # Create a thread pool for parallel processing
    with ThreadPoolExecutor() as executor:
        # Create asynchronous tasks for each entry and save them with their index
        future_to_index = {executor.submit(process_entry, entry): idx for idx, entry in enumerate(bib_database.entries)}

        # Add results when tasks are completed
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            data_list[idx] = future.result()

    # Output to CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'authors', 'abstract', 'background', 'purpose', 'proposal', 'evaluation', 'result', 'doi']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

# Example execution
file_name = 'uist2024'
translate_and_process_papers(file_name + ".bib", file_name + "_en.csv")
