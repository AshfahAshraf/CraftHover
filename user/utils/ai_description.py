import re   # For cleaning text

# Lazy loading generator (efficient for Django)
generator = None

def get_generator():
    global generator
    if generator is None:
        from transformers import pipeline
        generator = pipeline("text-generation", model="distilgpt2")  
        # You can upgrade to "gpt2-medium" for better quality
    return generator


#  Remove repeated words (extra safety)
def remove_repetition(text):
    words = text.split()
    result = []

    for word in words:
        if len(result) == 0 or word != result[-1]:
            result.append(word)

    return " ".join(result)


#  Detect material
def detect_material(name, category, product_type):
    text = f"{name} {category} {product_type}".lower()

    if any(word in text for word in ["clay", "ceramic", "pot", "diyas"]):
        return "Clay and ceramic materials"
    
    elif any(word in text for word in ["wood", "wooden"]):
        return "Natural wood"
    
    elif any(word in text for word in ["bamboo", "cane", "jute"]):
        return "Bamboo and natural fibers"
    
    elif any(word in text for word in ["leather"]):
        return "Genuine leather"
    
    elif any(word in text for word in ["silk", "cotton", "fabric", "saree"]):
        return "Cotton, silk, and handwoven fabrics"
    
    elif any(word in text for word in ["gold", "silver", "jewelry", "necklace"]):
        return "Metal and decorative elements"
    
    elif any(word in text for word in ["painting", "canvas", "art"]):
        return "Canvas and natural colors"

    return "High-quality materials"


#  Detect usage
def detect_usage(name, category, product_type):
    text = f"{name} {category} {product_type}".lower()

    if "mug" in text:
        return "Perfect for serving tea and coffee"
    
    elif "toy" in text:
        return "Safe and enjoyable for children"
    
    elif "basket" in text:
        return "Useful for storage and organization"
    
    elif "jewelry" in text or "necklace" in text:
        return "Enhances personal style and fashion"
    
    elif "wall" in text or "painting" in text:
        return "Enhances home décor and wall aesthetics"
    
    elif "bag" in text:
        return "Convenient for carrying daily essentials"
    
    elif "wallet" in text:
        return "Used for carrying money and cards"

    return "Suitable for daily use and decoration"


#  MAIN FUNCTION
def generate_description(name, category, product_type):

    material = detect_material(name, category, product_type)
    usage = detect_usage(name, category, product_type)

    #  Improved prompt
    prompt = f"""
Write a clear and attractive product description in 2-3 sentences.
Avoid repeating words. Keep it simple and professional.

Product Name: {name}
Category: {category}
Type: {product_type}

Description:
"""

    generator = get_generator()

    #  generation  (NO REPETITION)
    result = generator(
        prompt,
        max_length=120,
        do_sample=True,
        temperature=0.7,
        repetition_penalty=1.5,
        no_repeat_ngram_size=2,
        top_k=50,
        top_p=0.9
    )

    text = result[0]['generated_text']

    #  Clean output
    cleaned = text.replace(prompt, "").strip()
    cleaned = re.sub(r'[^a-zA-Z0-9., ]', '', cleaned)

    #  Remove repetition
    cleaned = remove_repetition(cleaned)

    # Limit words
    cleaned = " ".join(cleaned.split()[:40])

    #  Final structured description
    return f"""
{name} is a beautifully handcrafted {product_type} from the {category} collection, created by skilled artisans.

{cleaned}

Material: {material}  
Usage: {usage}  
Origin: India  

This unique piece blends traditional craftsmanship with modern design, making it a perfect addition to your collection.
"""