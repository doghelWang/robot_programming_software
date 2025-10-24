import json
import os

# 检查输出目录
if os.path.exists('output'):
    print("输出目录内容:")
    files = os.listdir('output')
    for file in files:
        print(f"  {file}")
    
    # 读取并显示第一个JSON文件
    for file in files:
        if file.endswith('.json'):
            filepath = os.path.join('output', file)
            print(f"\n文件 {file} 的内容:")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
            except Exception as e:
                print(f"读取文件时出错: {e}")
else:
    print("输出目录不存在")
