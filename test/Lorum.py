import json
import re

def generate_lorem(length):
    base = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ")
    repeated = (base * ((length // len(base)) + 1))[:length]
    return repeated

def replace_html_field(data):
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict) and "html" in entry:
                original_html = entry["html"]
                # Strip HTML tags to estimate text length
                text_only = re.sub(r'<[^>]+>', '', original_html)
                lorem_text = generate_lorem(len(text_only))
                entry["html"] = f"<p>{lorem_text}</p>"
    elif isinstance(data, dict) and "html" in data:
        original_html = data["html"]
        text_only = re.sub(r'<[^>]+>', '', original_html)
        lorem_text = generate_lorem(len(text_only))
        data["html"] = f"<p>{lorem_text}</p>"
    return data

def process_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    updated_data = replace_html_field(data)

    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(updated_data, outfile, indent=2, ensure_ascii=False)

# Example usage
process_json('Diarium.json', 'Lorum.json')