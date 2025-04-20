from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

class PhiLLM:
    def __init__(self, model_id="microsoft/phi-2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16).cuda()

    def _load_template(self, template_name):
        path = os.path.join("templates", template_name)
        with open(path) as f:
            return f.read()

    def generate(self, prompt, context="", mode="auto"):
        if mode == "pdf":
            template = self._load_template("pdf_instruction.txt")
            filled = template.format(context=context, question=prompt)
        elif mode == "code":
            template = self._load_template("code_instruction.txt")
            filled = template.format(code=prompt, question="What does this code do?")
        else:
            template = self._load_template("default_instruction.txt")
            filled = template.format(question=prompt)

        inputs = self.tokenizer(filled, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=300)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
