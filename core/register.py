from typing import Any, Dict


class ToolExecutor:
    """
    工具箱
    agent使用的工具统一从工具箱中获取，需要给agent新增加要用的工具需先添加到工具箱内
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, tool_name: str, description: str, func: callable):
        """
        向工具箱注册新工具
        """
        if tool_name in self.tools:
            print(f"警告：{tool_name}将被覆盖")
        self.tools[tool_name] = {"description": description, "func": func}

    def list(self) -> str:
        """
        获取所有可用工具的格式化描述字符
        """
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])

    def get_tool(self, tool_name: str) -> callable:
        """
        根据名称获取工具的执行函数
        """
        return self.tools.get(tool_name, {}).get("func")