import pandas as pd
import argparse
import os

def generate_markdown_slides(csv_file, output_file):
    df = pd.read_csv(csv_file)
    slides = []

    for index, row in df.iterrows():
        slide = "" if index == 0 else f"---\n"
        slide += f"# {row['title_ja']}\n\n"
        slide += f"##### [__{row['title']}__](https://doi.org/{row['doi']})\n\n"
        slide += f"###### {row['authors']}\n\n"
        slide += f"**背景** {row['background']}\n\n"
        slide += f"**目的** {row['purpose']}\n\n"
        slide += f"**提案** {row['proposal']}\n\n"
        slide += f"**評価** {row['evaluation']}\n\n"
        slide += f"**結果** {row['result']}\n"

        slides.append(slide)

    markdown_content = "\n".join(slides)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdownスライドが{output_file}に保存されました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Markdown slides from CSV.")
    parser.add_argument("csv_file", help="Input CSV file")
    parser.add_argument("output_md", help="Output Markdown file")

    args = parser.parse_args()

    generate_markdown_slides(args.csv_file, args.output_md)

    # PDFを生成するためのコマンド
    os.system(f"marp --theme customsize.css --pdf {args.output_md} -o {args.output_md.replace('.md', '.pdf')}")
