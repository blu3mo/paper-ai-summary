import openai
import csv
import json
import bibtexparser
import os
import argparse
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, as_completed

# OpenAI APIキーを設定してください
openai = openai.AzureOpenAI(
    api_key = os.getenv('AZURE_OPENAI_API_KEY'),
    api_version="2024-08-01-preview",
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

# 出力形式のクラス定義
class PaperSummary(BaseModel):
    title_ja: str
    abstract_ja: str
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

    # ChatGPTへのプロンプトを準備
    prompt = f"""
    以下は論文のタイトルとアブストラクトです。日本語に翻訳し、さらに「背景」「目的」「提案」「評価」「結果」の5項目を50字程度ずつに一文で整理してください。
    なお、ぱっと見でわかりやすいように、日本語訳や要約の中の重要なキーワードを強調してください。研究者視点で興味深いところを強調してください。強調する部分は** **で囲ってください。
    
    タイトル:
    {title}
    アブストラクト:
    {abstract}
    
    JSON形式で次のフォーマットで出力してください:
    {{
        "title_ja": "タイトルの日本語訳 (全体を翻訳し、2~3キーワードを** **で強調)",
        "abstract_ja": "アブストラクトの日本語訳(全体を翻訳し、2~3文を** **で強調)",
        "background": "背景 (研究が行われた背景や、対象となる問題や課題の概要、この問題がなぜ重要であるか、なぜ解決が求められているか)",
        "purpose": "目的 (研究が解決しようとしている問題と、その重要性を一言で)",
        "proposal": "提案 (主張する技術/手法/ソフトウェア/現象/仮説の概要)",
        "evaluation": "評価 (仮説検証に用いた実験アプローチや分析手法の概要)",
        "result": "結果 (得られた結論や示唆)"
    }}
    """

    try:
        response = openai.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは翻訳と文章の要約を行うアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            response_format=PaperSummary
        )

        parsed_reply = PaperSummary.parse_raw(response.choices[0].message.content)

        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'title_ja': parsed_reply.title_ja,
            'abstract_ja': parsed_reply.abstract_ja,
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
            'title_ja': '',
            'abstract_ja': '',
            'background': '',
            'purpose': '',
            'proposal': '',
            'evaluation': '',
            'result': '',
            'doi': doi
        }

def translate_and_process_papers(input_bib, output_csv):
    print(f"Loading BibTeX file: {input_bib}")
    with open(input_bib, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    print(f"Loaded {len(bib_database.entries)} entries from the BibTeX file.")

    data_list = [None] * len(bib_database.entries)

    print("Creating thread pool for parallel processing with rate limiting.")
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(process_entry, entry): idx for idx, entry in enumerate(bib_database.entries)}
        print("Submitted tasks for processing entries with rate limiting.")

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            data_list[idx] = future.result()
            print(f"Processed entry {idx + 1}/{len(bib_database.entries)}")

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'authors', 'abstract', 'title_ja', 'abstract_ja', 'background', 'purpose', 'proposal', 'evaluation', 'result', 'doi']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process BibTeX to CSV with OpenAI translation and summarization.")
    parser.add_argument("input_bib", help="Input BibTeX file")
    parser.add_argument("output_csv", help="Output CSV file")

    args = parser.parse_args()

    translate_and_process_papers(args.input_bib, args.output_csv)
