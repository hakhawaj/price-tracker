import os
import json
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

def clean_html(raw_html):
    """
    Strips code noise (scripts, CSS, structural svgs) to shrink payload size by ~80%
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Remove script and style elements completely
    for element in soup(["script", "style", "svg", "noscript", "header", "footer", "nav"]):
        element.extract()
        
    # Get text and eliminate extra whitespace gaps
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:400])  # Cap rows to keep target contextual frame concise

def extract_price_with_ai(raw_html, asset_name):
    """
    Feeds processed text layouts to Gemma and extracts structured price information
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY missing from environment configurations.")

    # Initialize client to target Gemma 2 models natively
    client = genai.Client(api_key=api_key)
    
    # Clean the code layout
    cleaned_text = clean_html(raw_html)
    
    prompt = f"""
    You are an expert e-commerce data extraction engine tracking inventory for {asset_name}.
    Analyze the following extracted web page text and locate the primary, current purchase price for this item.
    Ignore crossed-out original prices (MSRP) and monthly financing breakdowns.

    Web Page Content:
    \"\"\"
    {cleaned_text}
    \"\"\"

    Return ONLY a raw JSON object matching this exact schema:
    {{
        "price": float or null
    }}
    Do not include markdown code blocks, backticks, or text explanations.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # Targets the Gemini 2.5 flash model for fast execution
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", # Forces deterministic JSON structures
                temperature=0.1 # Forces predictable, non-creative accuracy
            )
        )
        
        # Parse output safely
        result = json.loads(response.text.strip())
        return result.get("price")
    except Exception as e:
        # Fallback tracking if API caps or parsing issues arise
        return None