import requests
from bs4 import BeautifulSoup
from arxiv import Search
import re


def prompt_user():
    return input("Enter a search query: ")


def display_progress(progress):
    print(f"Downloading papers... {progress}%")


def display_results(results):
    for result in results:
        print(result)


def display_error(error):
    print(f"Error: {error}")


def display_completion():
    print("Download completed.")


def search_google_scholar(query):
    url = f"https://scholar.google.com/scholar?q={query}&hl=en"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    results = []
    for result in soup.find_all("div", class_="gs_r gs_or gs_scl"):
        try:
            title = result.find("h3", class_="gs_rt").text
            url = result.find("a")["href"]
            results.append({"title": title, "url": url})
        except:
            continue
    return results


def search_arxiv(query):
    results = Search(query=query, max_results=10).results()
    formatted_results = []
    for result in results:
        title = result.title
        url = result.pdf_url
        formatted_results.append({"title": title, "url": url})
    return formatted_results


def combine_metadata(google_scholar_metadata, arxiv_metadata):
    return google_scholar_metadata + arxiv_metadata


def sanitize_filename(filename):
    # Remove special characters and replace spaces with underscores
    filename = re.sub(r"[^\w\s-]", "", filename)
    filename = re.sub(r"\s+", "_", filename)
    return filename


def download_paper(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        sanitized_filename = sanitize_filename(filename)
        with open(f"./papers/{sanitized_filename}.pdf", "wb") as file:
            file.write(response.content)


def download_papers(metadata):
    total_papers = len(metadata)
    for i, paper in enumerate(metadata, 1):
        title = paper["title"]
        url = paper["url"]
        filename = f"{title}.pdf"
        download_paper(url, filename)
        progress = (i / total_papers) * 100
        display_progress(progress)
