import requests
from dotenv import load_dotenv
import os

load_dotenv()


class GeminiAPIClient:
    def __init__(self):
        self.api_url = os.getenv('GEMINI_URL')
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.headers = {'Content-Type': 'application/json'}

    def generate_book_recommendations(self, reading_lists, genres=None, themes=None, writing_style=None, specific_elements=None):
        books_data = []
        for reading_list in reading_lists:
            for item in reading_list.items.all():
                book = item.book
                books_data.append({
                    "title": book.title,
                    "authors": book.authors,
                    "genre": book.genre,
                    "publication_date": book.publication_date.strftime("%Y-%m-%d"),
                    "description": book.description or "",
                })

        if not books_data:
            return {"error": "No books in the reading lists to base recommendations on"}

        max_books = 10
        books_data = books_data[:max_books]

        content_text = "Based on the following books:\n"
        for book in books_data:
            content_text += (
                f"- Title: {book['title']}, Author(s): {book['authors']}, Genre: {book['genre']}, "
                f"Published on: {book['publication_date']}, Description: {book['description']}\n"
            )
        content_text += "Recommend books similar to these."

        if genres:
            content_text += f" Preferred genres: {', '.join(genres)}."
        if themes:
            content_text += f" Themes: {', '.join(themes)}."
        if writing_style:
            content_text += f" Writing style: {writing_style}."
        if specific_elements:
            content_text += f" Specific elements: {', '.join(specific_elements)}."

        payload = {"contents": [{"parts": [{"text": content_text}]}]}
        url = f"{self.api_url}?key={self.api_key}"
        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            return self.parse_response(response.json())
        else:
            return {"error": f"Failed to generate recommendations. Status code: {response.status_code}, Response: {response.text}"}

    def parse_response(self, response_data):
        recommendations = []
        candidates = response_data.get("candidates", [])
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
                recommendations.append(part.get("text", "").strip())
        return recommendations if recommendations else {"error": "No recommendations found in the response."}


    def generate_book_description(self, book_title, book_author):
        content_text = f"Please generate a description for the book titled '{book_title}' by {book_author}."

        payload = {
            "contents": [{
                "parts": [{"text": content_text}]
            }]
        }

        url = f"{self.api_url}?key={self.api_key}"
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            generated_description = result['candidates'][0]['content']['parts'][0]['text']
            return generated_description
        else:
            return {"error": "Failed to generate book description"}
        

    def ask_book_query(self, query):
        content_text = f"Answer the following question: {query}"

        payload = {
            "contents": [{
                "parts": [{"text": content_text}]
            }]
        }

        url = f"{self.api_url}?key={self.api_key}"
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            answer = result['candidates'][0]['content']['parts'][0]['text']
            return answer
        else:
            return {"error": "Failed to get book query response"}