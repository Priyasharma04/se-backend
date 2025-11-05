from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch, gc

model_path = "C:/Users/saxen/Desktop/se-project-final/models"

print("🔄 Loading model on GPU (4-bit)...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(model_path)

# load model to GPU automatically
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    device_map="auto"  # automatically uses GPU if available
)

model.eval()

def generate_review(paper_text: str) -> str:
    print("🧠 Generating review on GPU...")
    mode = "full" if len(paper_text) < 20000 else "chunked"

    if mode == "full":
        prompt = f"""
You are an expert reviewer for a top-tier research conference.
Provide a structured and academic review for the paper below.

Paper:
{paper_text}

Follow this structure:
### Domain Classification
### Summary
### Strengths
### Weaknesses
### Novelty
### Review Decision Memo
### Additional Comments
"""
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to("cuda")

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=1600,
                temperature=0.6,
                top_p=0.9,
                eos_token_id=tokenizer.eos_token_id,
            )

        review_text = tokenizer.decode(output[0], skip_special_tokens=True)
        torch.cuda.empty_cache(); gc.collect()
        return review_text