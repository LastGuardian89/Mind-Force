import os
import asyncio
import torch
import re
from typing import Optional, Tuple
from sentence_transformers import SentenceTransformer, util
from llm.phi_wrapper import PhiLLM
from utils.exceptions import QualityThresholdReached

class SocietyMind:
    def __init__(
        self,
        model: PhiLLM,
        max_rounds: int = 3,
        similarity_threshold: float = 0.85,
        quality_threshold: float = 0.7
    ):
        self.model = model
        self.max_rounds = max_rounds
        self.similarity_threshold = similarity_threshold
        self.quality_threshold = quality_threshold
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.templates = {
            'generator': self._load_template("generator_instruction.txt"),
            'critic': self._load_template("critic_instruction.txt"),
            'finalizer': self._load_template("finalizer_instruction.txt")
        }

    async def refine_response(
        self,
        query: str,
        context: str,
        initial_response: str
    ) -> str:
        current_response = initial_response
        previous_response = ""
        iteration = 0
        
        while iteration < self.max_rounds:
            # 1. Generate critique with context
            critique = await self._generate_critique(query, current_response, context)
            
            # 2. Check stopping conditions
            stop_reason = self._check_stopping_conditions(
                current_response,
                previous_response,
                context
            )
            if stop_reason:
                print(f"Stopping iteration: {stop_reason}")
                break
                
            # 3. Generate improved response
            previous_response = current_response
            current_response = await self._generate_improved(
                query,
                context,
                critique
            )
            
            iteration += 1
            
        return await self._finalize_response(current_response, context)

    def _check_stopping_conditions(
        self,
        current: str,
        previous: str,
        context: str
    ) -> Optional[str]:
        # 1. Check similarity between iterations
        iteration_similarity = self._calculate_similarity(current, previous)
        if iteration_similarity > self.similarity_threshold:
            return f"Iteration similarity {iteration_similarity:.2f}"
            
        # 2. Check quality score
        quality_score = self._calculate_quality_score(current, context)
        if quality_score >= self.quality_threshold:
            return f"Quality threshold {quality_score:.2f}"
            
        return None

    def _calculate_quality_score(self, response: str, context: str) -> float:

        context_sim = self._calculate_similarity(response, context)
        
        key_terms = self._extract_key_terms(context)
        coverage = sum(1 for term in key_terms if term in response) / len(key_terms)
        
        
        length_factor = min(max(len(response)/500, 0.5), 1.0)
        
        
        return 0.6*context_sim + 0.3*coverage + 0.1*length_factor

    def _extract_key_terms(self, text: str, top_n: int = 10) -> list:
        words = re.findall(r'\w+', text.lower())
        freq = {}
        for word in words:
            if word in freq:
                freq[word] += 1
            else:
                freq[word] = 1
        return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

    async def _generate_critique(
        self,
        query: str,
        response: str,
        context: str
    ) -> str:
        prompt = self.templates['critic'].format(
            query=query,
            response=response,
            context=context
        )
        return await self._safe_generate(prompt)

    async def _generate_improved(
        self,
        query: str,
        context: str,
        critique: str
    ) -> str:
        prompt = self.templates['generator'].format(
            query=query,
            context=context,
            feedback=critique
        )
        return await self._safe_generate(prompt)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        embeddings = self.similarity_model.encode([text1, text2])
        return util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

    async def _safe_generate(self, prompt: str) -> str:
        try:
            inputs = self.model.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=1024,
                truncation=True
            ).to(self.model.device)

            outputs = await asyncio.to_thread(
                self.model.model.generate,
                **inputs,
                max_new_tokens=500,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            return self.model.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            ).strip()
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")

    def _load_template(self, filename: str) -> str:
        template_path = os.path.join("templates", filename)
        with open(template_path, "r") as f:
            return f.read()

    async def _finalize_response(self, response: str, context: str) -> str:
        prompt = self.templates['finalizer'].format(
            response=response,
            context=context
        )
        return await self._safe_generate(prompt)