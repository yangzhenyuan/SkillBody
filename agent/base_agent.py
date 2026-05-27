import re
from typing import Dict, List, Optional

from core.agent import Agent
from core.message import Message
from core.register import ToolExecutor


class BaseAgent(Agent):
    def __init__(
            self, 
            llm, 
            tools: ToolExecutor, 
            prompt = None, 
            config = None,  
            custom_prompt: Optional[str] = None
        ):
        super().__init__(llm, prompt, config)
        self.tools = tools
        self.custom_prompt = custom_prompt
        self.history: List[Message] = []
    
    def run(self, input, **kwargs) -> str:
        """ 
        执行Agent 
        1、拼接系统prompt，说明内容包含初始化所有的内容：系统prompt、可用的工具
        2、如果有历史消息则也需要添加到发送给LLM的消息中
        3、添加用户消息
        4、将组装的消息发送给LLM获取响应，如果需要调用对应的工具则执行工具调用
        5、获取到工具调用的结果，将结果带上再一并发送给LLM获取最终结果
        
        """
        print(f"\n 开始处理问题： {input}")

        messages = []

        # 添加系统消息（包含工具信息）
        system_prompt = self.get_system_prompt()
        print(f"系统prompt为：\n {system_prompt}")
        messages.append({"role": "system", "content": system_prompt})

        # 添加历史消息
        for msg in self.history:
            messages.append({"role": msg.role, "content":msg.content})
        
        # 添加用户信息
        messages.append({"role": "user", "content": input})

        response = self.llm.think(message=messages)
        tool_calls = self._parse_tool_calls(response)
        if tool_calls:
            print(f"🔧 检测到{len(tool_calls)}个工具调用")
            tool_results = []
            tool_call_response = response

            for call in tool_calls:
                tool_result = self._exec_tool_call(tool_name=call['tool_name'], parameters=call['parameters'])
                tool_results.append(tool_result)

                tool_call_response.replace(call['original'], "")

            # 构建包含工具结果的消息
            messages.append({"role": "assistant", "content": tool_call_response})
            tool_results_msg = "\n\n".join(tool_results)
            messages.append({"role": "user", "content": f"工具执行结果：\n{tool_results_msg}\n\n请基于这些结果给出完整的回答"})
        
            final_response = self.llm.think(messages)
        else:
            final_response = response

        self.history.append(Message(input, "user"))
        self.history.append(Message(final_response, "assistant"))
        print("✅ 响应完成")

        return final_response

    def get_system_prompt(self) -> str:
        """
        构建系统提示词：
        基础系统提示词由初始化时传入
        如果还提供了可用的工具列表，则需要将工具的相关信息也加入的系统提示词内
        """
        message = self.prompt or "你是一个有用的AI助手"

        toolDesc = self.tools.list()
        if not toolDesc or toolDesc == "暂无工具可用":
            return message
        
        tools_section = f"""
        ## 可用工具
        你可以使用以下工具来帮助回答问题：
        {toolDesc}

        ## 工具调用格式
        当需要使用工具时，请使用以下格式：
        `[TOOL_CALL:{{tool_name}}:{{parameters}}]`
        当parameters是多个参数时，请使用如下格式：
        `key=value`
        工具调用示例：`[TOOL_CALL:memory:recall=用户信息]`

        工具调用结果会自动插入到对话中，然后你可以基于结果继续回答。

        """

        return message + tools_section

    def _parse_tool_calls(self, response: str) -> List:
        """ 解析文本中的工具调用 """
        pattern = r'\[TOOL_CALL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, response)

        tool_calls = []
        for tool_name, parameters in matches:
            tool_calls.append({
                'tool_name': tool_name.strip(),
                'parameters': parameters.strip(),
                'original': f'[TOOL_CALL:{tool_name}:{parameters}]'
            })

        return tool_calls
    
    def _exec_tool_call(self, tool_name: str, parameters: str) -> str:
        """ 执行工具调用 """
        if not self.tools:
            return f"❌ 错误： 未配置工具注册表"
        
        try:
            tool = self.tools.get_tool(tool_name)
            if not tool:
                return f"❌ 错误：未找到工具 {tool_name}"
            param = self._parse_tool_parameter(parameters)
            result = tool.run(param)
            return f"🔧 工具 {tool_name}执行结果： \n{result}"
        except Exception as e:
            return f"❌ 工具调用失败：{str(e)}"
    
    def _parse_tool_parameter(self, parameters: str) -> Dict:
        """解析工具调用入参"""
        param_dict = {}

        if "=" in parameters:
            if "," in parameters:
                # 多个参数的情况
                params = parameters.split(",")
                for param in params:
                    key, value = param.split('=', 1)
                    param_dict[key.strip()] = value.strip()
            else:
                key, value = parameters.split("=", 1)
                param_dict[key.strip()] = value.strip()
        else:
            print(f"❌ 参数格式有误：{parameters}")

        return param_dict