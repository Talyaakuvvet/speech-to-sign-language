from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Hazır bir T5 modeli (generic English-to-ASL fine-tune edilmiş model az, ama gösterim için base T5)
model_name = "t5-small"   # demo için (istersen "t5-base" kullan)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def translate_to_gloss(sentence):
    # T5 input genelde "translate English to ASL gloss: <sentence>" şeklinde hazırlanır
    input_text = f"translate English to ASL gloss: {sentence}"
    inputs = tokenizer(input_text, return_tensors="pt")

    outputs = model.generate(**inputs, max_length=50)
    gloss = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return gloss

# Test
eng = "Hello, my name is Talya. I need help at the hospital."
print("English:", eng)
print("Predicted Gloss:", translate_to_gloss(eng))
