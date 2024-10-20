import requests
import bibtexparser

# Semantic Scholar APIの設定
API_BASE_URL = "https://api.semanticscholar.org/graph/v1"
from dotenv import load_dotenv
import os

load_dotenv()  # .envファイルから環境変数をロード

API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")  # .envファイルにAPIキーを設定

def get_paper_id_from_doi(doi):
    url = f"{API_BASE_URL}/paper/DOI:{doi}"
    headers = {"x-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('paperId')
    else:
        print("DOIから論文IDを取得できませんでした。エラー:", response.status_code)
        return None

def get_citations(paper_id):
    url = f"{API_BASE_URL}/paper/{paper_id}/citations"
    headers = {"x-api-key": API_KEY}
    params = {
        "fields": "title,authors,year,venue,abstract",
        "offset": 0,
        "limit": 100
    }
    all_citations = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get('data', [])
            if not data:
                print("No more citations found.")
                break
            all_citations.extend(data)
            params["offset"] += params["limit"]
        else:
            print("引用論文を取得できませんでした。エラー:", response.status_code)
            break
    
    return all_citations

def citation_to_bibtex_entry(citation):
    authors = " and ".join([author['name'] for author in citation['citingPaper']['authors']])
    bibtex_entry = {
        'ENTRYTYPE': 'article',
        'ID': citation['citingPaper']['paperId'],
        'title': citation['citingPaper']['title'],
        'author': authors,
        'year': str(citation['citingPaper']['year']),
        'journal': citation['citingPaper'].get('venue', 'Unknown'),
        'abstract': citation['citingPaper']['abstract'] if citation['citingPaper'].get('abstract') is not None else 'Abstract not available'
    }
    return bibtex_entry

def generate_bibtex_file(citations, filename="citations.bib"):
    bibtex_database = bibtexparser.bibdatabase.BibDatabase()
    bibtex_database.entries = [citation_to_bibtex_entry(citation) for citation in citations]
    
    with open(filename, "w") as bibtex_file:
        bibtexparser.dump(bibtex_database, bibtex_file)
    print(f"{filename}として保存されました。")

# メイン処理
doi = "10.1145/3586183.3606763"  # ここに対象のDOIを入力
paper_id = get_paper_id_from_doi(doi)
if paper_id:
    citations = get_citations(paper_id)
    generate_bibtex_file(citations, "citations.bib")
