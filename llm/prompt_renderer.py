from typing import Mapping

class PromptRenderer:
    def render(self, template: str, variables: Mapping[str, str]) -> str:
        return template.format(**variables)
