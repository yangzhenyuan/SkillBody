from core.register import ToolExecutor


if __name__ == "__main__":
    tool_cool = ToolExecutor()

    from tools.cal import add

    tool_cool.register(tool_name="add", description="加法计算，可以计算两个数字的和", func=add)

    print("---可用的工具---")
    print(tool_cool.list())

    print("\n --- 执行工具调用 ---")
    name = "add"
    func = tool_cool.get_tool(tool_name=name)
    if func:
        sum = func(12, 13)
        print("--- 计算结果 ---")
        print(sum)
    else:
        print(f"错误：未找到名为{name}的工具")