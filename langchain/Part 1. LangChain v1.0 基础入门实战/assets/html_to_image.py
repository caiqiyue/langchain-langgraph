"""
HTML转图片工具 - 使用Playwright将HTML文件转换为PNG图片
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置文件
ASSETS_DIR = Path(__file__).parent

# 所有需要转换的HTML文件（相对于ASSETS_DIR）
HTML_FILES = [
    # 第一课
    ("第一课_01_LangChain生态概览图.html", "第一课_01_LangChain生态概览图.png"),
    ("第一课_02_LangChain底层架构图.html", "第一课_02_LangChain底层架构图.png"),
    ("第一课_03_Runnable接口与LCEL.html", "第一课_03_Runnable接口与LCEL.png"),
    ("第一课_04_场景选择指南图.html", "第一课_04_场景选择指南图.png"),
    # 第二课
    ("第二课_01_模块依赖关系图.html", "第二课_01_模块依赖关系图.png"),
    ("第二课_02_厂商包vs社区包对比图.html", "第二课_02_厂商包vs社区包对比图.png"),
    # 第三课
    ("第三课_01_LLM与ChatModel区别.html", "第三课_01_LLM与ChatModel区别.png"),
    ("第三课_02_消息类型详解.html", "第三课_02_消息类型详解.png"),
    ("第三课_03_结构化输出解析器.html", "第三课_03_结构化输出解析器.png"),
    ("第三课_04_批处理与流式传输.html", "第三课_04_批处理与流式传输.png"),
    # 第四课
    ("第四课_01_Gradio对话机器人架构.html", "第四课_01_Gradio对话机器人架构.png"),
    ("第四课_02_流式输出与事件监听.html", "第四课_02_流式输出与事件监听.png"),
]

# HTML到PNG的映射（用于替换markdown中的引用）
HTML_TO_PNG = {html_name: png_name for html_name, png_name in HTML_FILES}

# Markdown文件列表
MARKDOWN_FILES = [
    ASSETS_DIR.parent / "第一节课" / "第一阶段、LangChain框架介绍.md",
    ASSETS_DIR.parent / "第二节课" / "第二阶段、LangChain模组化生态的定位与价值.md",
    ASSETS_DIR.parent / "第三节课" / "第三阶段、庖丁解模块.md",
    ASSETS_DIR.parent / "第四节课" / "第四阶段、实战大模型.md",
]

def html_to_image(html_path: Path, png_path: Path, scale: float = 2.0):
    """将HTML文件转换为PNG图片"""
    print(f"正在转换: {html_path.name} -> {png_path.name}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 800, "device_scale_factor": scale})

        # 加载HTML文件
        page.goto(f"file:///{html_path.absolute()}", wait_until="networkidle")

        # 等待内容加载完成
        page.wait_for_timeout(1000)

        # 截图保存
        page.screenshot(path=str(png_path), full_page=True, scale="css")

        browser.close()

    print(f"  完成: {png_path}")

def update_markdown():
    """更新所有Markdown文件中的图片引用"""
    for md_file in MARKDOWN_FILES:
        if not md_file.exists():
            print(f"Markdown文件不存在: {md_file}")
            continue

        content = md_file.read_text(encoding="utf-8")
        original_content = content

        # 替换所有HTML引用为PNG
        for html_name, png_name in HTML_TO_PNG.items():
            content = content.replace(html_name, png_name)

        if content != original_content:
            md_file.write_text(content, encoding="utf-8")
            print(f"已更新: {md_file.name}")
        else:
            print(f"无需更新: {md_file.name}")

def main():
    print("=" * 50)
    print("HTML 转 PNG 图片工具")
    print("=" * 50)

    # 转换HTML文件为PNG
    for html_name, png_name in HTML_FILES:
        html_path = ASSETS_DIR / html_name
        png_path = ASSETS_DIR / png_name

        if html_path.exists():
            html_to_image(html_path, png_path)
        else:
            print(f"  文件不存在: {html_path}")

    # 更新Markdown引用
    print("\n" + "=" * 50)
    print("更新Markdown文件...")
    update_markdown()
    print("=" * 50)
    print("全部完成!")

if __name__ == "__main__":
    main()