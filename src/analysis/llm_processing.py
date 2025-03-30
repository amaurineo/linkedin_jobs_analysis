from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import re
from tqdm import tqdm

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load Qwen2.5 model (7B version example)
model_name = "Qwen/Qwen2.5-7B"  # Verify exact model name on HuggingFace
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

def extract_requirements_qwen(job_description: str) -> dict:
    """Extract job requirements using Qwen2.5"""
    prompt = f"""<|im_start|>system
    You are an expert HR analyst. Extract the following information from the job description in JSON format:
    {{
        "required_skills": list of technical skills,
        "preferred_skills": list of nice-to-have skills,
        "education_level": string,
        "certifications": list,
        "experience_years": string,
        "technical_requirements": list
    }}<|im_end|>
    <|im_start|>user
    {job_description[:3000]}  # Truncate to save tokens
    <|im_end|>
    <|im_start|>assistant
    """
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    # Generate response
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=500,
        do_sample=True,
        temperature=0.1,
        top_p=0.9
    )
    
    # Decode and parse response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    json_str = response.split("<|im_start|>assistant")[-1].strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback parsing
        return parse_semi_structured_output(json_str)

def parse_semi_structured_output(text: str) -> dict:
    """Fallback parser for malformed JSON"""
    result = {}
    current_key = None
    for line in text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().strip('"').lower()
            value = value.strip().rstrip(',')
            
            if value.startswith('['):
                try:
                    result[key] = json.loads(value)
                except:
                    result[key] = [v.strip() for v in value.strip('[]').split(',')]
            else:
                result[key] = value
    return result

# Usage example:
if __name__ == "__main__":
    sample_desc = """Looking for Python developer with 3+ years experience...
                     Required skills: Django, REST APIs, PostgreSQL..."""
    
    print(extract_requirements_qwen(sample_desc))