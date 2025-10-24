# 文件读取器项目

本项目旨在实现一个能够读取和解析多种文件格式的系统，包括HTML/XML网页文件和Excel文件（.xlsx/.xls）。

## 功能特性

- 读取和解析HTML/XML文件
- 读取和解析Excel文件（.xlsx/.xls格式）
- 数据提取和转换
- 用户友好的界面
- 错误处理和文件格式兼容性检查

## 技术栈

- Python 3.x
- BeautifulSoup4 (HTML/XML解析)
- openpyxl (Excel文件读取)
- xlrd (旧版Excel文件读取)
- tkinter (用户界面)

## 项目结构

```
file_reader_project/
├── src/
│   ├── __init__.py
│   ├── file_reader.py          # 核心文件读取功能
│   ├── html_parser.py          # HTML/XML解析器
│   ├── excel_reader.py         # Excel文件读取器
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口界面
│   │   └── file_selector.py    # 文件选择器
│   └── utils/
│       ├── __init__.py
│       └── data_processor.py   # 数据处理工具
├── tests/
│   ├── __init__.py
│   ├── test_file_reader.py     # 文件读取器测试
│   └── test_parsers.py         # 解析器测试
├── requirements.txt            # 依赖包列表
├── main.py                     # 主程序入口
└── README.md                   # 项目说明文档
```
