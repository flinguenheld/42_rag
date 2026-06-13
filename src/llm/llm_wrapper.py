from __future__ import annotations

import torch
from typing import ClassVar, TypedDict, cast
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    PreTrainedModel,
)


class LLMWrapper:
    NAME: ClassVar[str] = "Qwen/Qwen3-0.6B"

    class PromptDict(TypedDict):
        input_ids: torch.Tensor
        attention_mask: torch.Tensor

    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(self.NAME)
        self.model: PreTrainedModel = cast(
            PreTrainedModel,
            AutoModelForCausalLM.from_pretrained(
                self.NAME,
                torch_dtype=torch.bfloat16,
                device_map="auto",
            ),
        )

    def _encode(self, prompt: str) -> PromptDict | None:
        """Encode prompt into tokens"""

        if self.model and self.tokenizer:
            tokens = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True,
            )

            prompt_dict = self.tokenizer([tokens], return_tensors="pt").to(
                self.model.device
            )
            if isinstance(prompt_dict, dict):
                return prompt_dict  # type: ignore[return-value]
        return None

    def ask(self, prompt: str, max_new_tokens: int) -> str:
        """Generate an answer from the given prompt"""

        tokens = self._encode(prompt)
        if tokens and self.tokenizer:
            generated_tk_ids = self.model.generate(  # type: ignore[operator]
                inputs=tokens["input_ids"],
                attention_mask=tokens["attention_mask"],
                max_new_tokens=max_new_tokens,
            )

            # Get rid of prompt and return the answer
            input_length = tokens["input_ids"].shape[1]
            answer_ids = generated_tk_ids[0][input_length:]
            answer = self.tokenizer.decode(
                answer_ids, skip_special_tokens=True
            )
            if isinstance(answer, str):
                return answer

        return ""
