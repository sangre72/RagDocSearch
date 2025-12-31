"""HuggingFace Transformers LLM Provider"""

from typing import AsyncIterator

from app.providers.base import LLMConfig, LLMMessage, LLMResponse
from .base import BaseLLMProvider


class HuggingFaceLLMProvider(BaseLLMProvider):
    """HuggingFace Transformers LLM Provider - 로컬 모델 실행"""

    provider_name = "huggingface"

    AVAILABLE_MODELS = [
        "microsoft/phi-2",
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "Qwen/Qwen2-1.5B-Instruct",
        "google/gemma-2b-it",
        "meta-llama/Llama-2-7b-chat-hf",
    ]

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._pipeline = None
        self._model_loaded = False

    def _load_model(self):
        """모델 지연 로딩"""
        if self._model_loaded:
            return

        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            import torch

            # 디바이스 설정
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"

            # 모델 로드
            self._pipeline = pipeline(
                "text-generation",
                model=self.config.model_name,
                device=device,
                torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            )
            self._model_loaded = True
        except ImportError:
            raise RuntimeError(
                "transformers not installed. "
                "Run: pip install transformers accelerate torch"
            )

    async def generate(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """동기 응답 생성"""
        self._load_model()

        # 메시지를 프롬프트로 변환
        prompt = self._format_messages(messages)

        # 생성
        outputs = self._pipeline(
            prompt,
            max_new_tokens=self.config.max_tokens or 512,
            temperature=self.config.temperature,
            do_sample=True,
            return_full_text=False,
        )

        return LLMResponse(
            content=outputs[0]["generated_text"],
            model=self.config.model_name,
        )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """스트리밍 응답 생성 (HuggingFace는 기본적으로 스트리밍 미지원)"""
        response = await self.generate(messages, **kwargs)
        yield response.content

    def _format_messages(self, messages: list[LLMMessage]) -> str:
        """메시지를 프롬프트 문자열로 변환"""
        formatted = []
        for msg in messages:
            if msg.role == "system":
                formatted.append(f"System: {msg.content}")
            elif msg.role == "user":
                formatted.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                formatted.append(f"Assistant: {msg.content}")
        formatted.append("Assistant:")
        return "\n\n".join(formatted)

    def get_available_models(self) -> list[str]:
        """사용 가능한 모델 목록 반환"""
        return self.AVAILABLE_MODELS

    async def health_check(self) -> bool:
        """Provider 상태 확인"""
        try:
            import transformers
            return True
        except ImportError:
            return False
