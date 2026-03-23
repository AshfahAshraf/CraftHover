from transformers import pipeline

generator = pipeline("text-generation", model="distilgpt2")

def generate_description(name, category):

    prompt = f"""
Write a professional product description for a handmade {category} product named "{name}".

Include:
- A short paragraph introduction
- Then structured details like:

Material:
Craft Type:
Usage:
Care Instructions:
Origin:

Make it suitable for an artisan marketplace.
"""

    result = generator(prompt, max_length=120, num_return_sequences=1)

    return result[0]['generated_text']