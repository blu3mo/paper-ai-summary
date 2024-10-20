import pandas as pd

def generate_markdown_slides(csv_file, output_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # List to hold Markdown strings for slides
    slides = []

    # Process each row to create slides
    for index, row in df.iterrows():
        slide = "" if index == 0 else f"---\n"  # Slide separator
        slide += f"# [__{row['title']}__](https://doi.org/{row['doi']})\n\n"  # Title as a link with underline
        slide += f"###### {row['authors']}\n\n"  # Authors
        slide += f"**Background:** {row['background']}\n\n"  # Background
        slide += f"**Purpose:** {row['purpose']}\n\n"  # Purpose
        slide += f"**System:** {row['proposal']}\n\n"  # Proposal
        slide += f"**Evaluation:** {row['evaluation']}\n\n"  # Evaluation
        slide += f"**Result:** {row['result']}\n"  # Result
        slides.append(slide)

    # Join slides into a single string
    markdown_content = "\n".join(slides)

    # Write to Markdown file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown slides have been saved to {output_file}.")

# Set the base file name
file_name = "uist2024"

# Get the CSV file path and output Markdown file path from file_name
csv_file = f"{file_name}_en.csv"  # CSV file to read
output_file = f"{file_name}_en.md"  # Markdown file to output

# Generate slides
generate_markdown_slides(csv_file, output_file)

import os

# Run the marp command to generate the PDF from the Markdown file
os.system(f"marp --theme customsize_en.css --pdf {file_name}_en.md -o {file_name}_en.pdf")
