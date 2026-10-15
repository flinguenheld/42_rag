from __future__ import annotations

from typing import ClassVar, cast

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BatchEncoding,
    PreTrainedModel,
)


# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█░░░█░░░█▄█░░░█░█░█▀▄░█▀█░█▀█░█▀█░█▀▀░█▀▄░░
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█░░░█░░░█░█░░░█▄█░█▀▄░█▀█░█▀▀░█▀▀░█▀▀░█▀▄░░
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▀▀▀░▀▀▀░▀░▀░░░▀░▀░▀░▀░▀░▀░▀░░░▀░░░▀▀▀░▀░▀░░
class LLMWrapper:
    NAME: ClassVar[str] = "Qwen/Qwen3-0.6B"

    # ########################################################################
    # ############################################################## INIT ####
    def __init__(self) -> None:

        tokenizer = AutoTokenizer.from_pretrained(self.NAME)
        if tokenizer is None:
            raise RuntimeError(f"Cannot load the tokenizer of {self.NAME}")
        self.tokenizer = tokenizer

        self.model: PreTrainedModel = cast(
            PreTrainedModel,
            AutoModelForCausalLM.from_pretrained(
                self.NAME,
                dtype=torch.bfloat16,
                device_map="auto",
            ),
        )

    # ########################################################################
    # ##################################################### ENCODE PROMPT ####
    def _encode_prompt(self, prompt: str) -> BatchEncoding:
        """Encode prompt into tokens"""

        tokens = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )

        prompt_dict = self.tokenizer([tokens], return_tensors="pt").to(
            self.model.device
        )
        return prompt_dict

    # ########################################################################
    # ############################################################### ASK ####
    def ask(self, prompt: str, max_new_tokens: int) -> str:
        """Generate an answer from the given prompt"""

        tokens = self._encode_prompt(prompt)
        generated_tk_ids = self.model.generate(
            inputs=tokens["input_ids"],
            attention_mask=tokens["attention_mask"],
            max_new_tokens=max_new_tokens,
            do_sample=False,  # greedy: always the most likely token
            repetition_penalty=1.1,  # discourage loops
            temperature=None,  # cancel the sampling values
            top_p=None,  # from generation_config.json
            top_k=None,
        )  # type: ignore[operator] # ty: ignore[call-non-callable]

        # Get rid of prompt and return the answer
        input_length = tokens["input_ids"].shape[1]
        answer_ids = generated_tk_ids[0][input_length:]

        answer = self.tokenizer.decode(answer_ids, skip_special_tokens=True)
        if isinstance(answer, str):
            return answer.strip()

        return ""
