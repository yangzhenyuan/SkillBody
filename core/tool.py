from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None

class Tool(ABC):
    """工具类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, parameters: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """转换为 OpenAI function calling schema格式
        用于 FunctionCallAgent，使工具能够被OpenAI原生function call 使用

        returns: 符合OpenAI function calling标准的schema
        """

        parameters = self.get_parameters()

        properties: Dict[str, Any] = {}
        required: List[str] = []

        for param in parameters:
            # 基础属性定义
            prop = {
                "type": param.type,
                "description": param.description
            }
            # 如果有默认值，添加到描述中（OpenAI schema 不支持default字段）
            if param.default is not None:
                prop["description"] = f"{param.description}(默认：{param.default})"

            if param.type == "array":
                prop["items"] = {"type": "string"}
            
            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

class ToolRegistry:
    """工具注册表"""
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        """注册Tool对象"""
        if tool.name in self.tools:
            print(f"警告⚠ ： 工具 {tool.name} 已存在，将被覆盖")
        self.tools[tool.name] = tool
        print(f"✅ 工具 {tool.name} 注册成功")

    def get_tools_description(self) -> str:
        """
        获取所有可用工具的格式化描述字符串
        返回的格式为：- {tool_name}: {description}
        """
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions) if descriptions else "暂无可用工具"