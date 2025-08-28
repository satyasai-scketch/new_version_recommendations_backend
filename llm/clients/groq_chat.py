from llm.interfaces import LLMClient
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class GroqChat(LLMClient):
    def __init__(self, api_key: str, model: str):
        self._llm = ChatGroq(
            api_key=api_key,
            model=model
        )

    def generate(self, *, prompt: str, **kwargs) -> str:
        """
        Generate a completion from the LLM.

        Kwargs supported:
            - system: str = "You are a helpful assistant."
            - temperature: float (overrides instance default)
            - response_format: dict (e.g., {"type": "json_object"} or JSON schema)
        """
        system_msg = kwargs.get("system", "You are a helpful assistant.")
        response_format = kwargs.get("response_format", None)

        # Create a per-call bound runnable if overrides are provided
        runnable = self._llm
        bind_args = {}
        if response_format is not None:
            bind_args["response_format"] = response_format

        if bind_args:
            runnable = self._llm.bind(**bind_args)

        ai_msg = runnable.invoke(
            [SystemMessage(content=system_msg), HumanMessage(content=prompt)]
        )
        
        return ai_msg.content if hasattr(ai_msg, "content") else str(ai_msg)
