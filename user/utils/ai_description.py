from transformers import pipeline
import re

generator = pipeline("text-generation", model="distilgpt2")

def generate_description(name, category, product_type):

    prompt = f"{name} is a handmade product. It is"

    result = generator(
        prompt,
        max_length=60,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.5
    )

    text = result[0]['generated_text']

    # remove prompt
    cleaned = text.replace(prompt, "").strip()

    # ❌ remove repeated words
    words = cleaned.split()
    unique_words = []
    for word in words:
        if word.lower() not in [w.lower() for w in unique_words]:
            unique_words.append(word)

    cleaned = " ".join(unique_words[:15])  # limit size

    # ❌ remove unwanted words (like clay, wood etc.)
    cleaned = re.sub(r'\b(clay|wood|plastic|metal)\b', '', cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip()

    # ✅ FINAL CONTROLLED OUTPUT
    return f"""
{name} is a handcrafted {category} {product_type} made by skilled artisans.

Material: High-quality {category}  
Product Type: {product_type}  
Usage: Home décor / daily use  
Care: Keep in dry conditions  
Origin: India  

Designed with a natural and elegant finish, perfect for enhancing your living space.
"""