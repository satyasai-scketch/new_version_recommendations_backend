from typing import Any, Optional
from llm.interfaces import LLMClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


class OpenAIChat(LLMClient):
    """
    LangChain-based OpenAI chat client.
    - Uses langchain_openai.ChatOpenAI under the hood.
    - You can override temperature/response_format per call via kwargs.
    - Returns plain string content.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0,
        base_url: Optional[str] = None,
    ):
        """
        Args:
            api_key: OpenAI (or compatible) API key.
            model: Model name (e.g., 'gpt-4o-mini').
            base_url: Custom base URL for compatible providers (optional).
            temperature: Default temperature for the instance.
            timeout: Request timeout in seconds (passed via http client).
            model_kwargs: Extra model kwargs forwarded to the provider
                         (e.g., {"response_format": {"type": "json_object"}} to set a default).
        """
        self._llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
            base_url=base_url
        )
        self._default_temperature = temperature

    def generate(self, *, prompt: str, **kwargs) -> str:
        """
        Generate a completion from the LLM.

        Kwargs supported:
            - system: str = "You are a helpful assistant."
            - temperature: float (overrides instance default)
            - response_format: dict (e.g., {"type": "json_object"} or JSON schema)
        """
        system_msg = kwargs.get("system", "You are a helpful assistant.")
        temperature = kwargs.get("temperature", self._default_temperature)
        response_format = kwargs.get("response_format", None)

        # Create a per-call bound runnable if overrides are provided
        runnable = self._llm
        bind_args = {}
        if temperature is not None:
            bind_args["temperature"] = float(temperature)
        if response_format is not None:
            bind_args["response_format"] = response_format

        if bind_args:
            runnable = self._llm.bind(**bind_args)

        ai_msg = runnable.invoke(
            [SystemMessage(content=system_msg), HumanMessage(content=prompt)]
        )
        
        return ai_msg.content if hasattr(ai_msg, "content") else str(ai_msg)
