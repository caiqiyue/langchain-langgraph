from IPython.display import Image, display

# 生成可视化图像结构
display(Image(graph.get_graph().draw_mermaid_png()))