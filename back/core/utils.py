import json
from pathlib import Path
from typing import Union, Any, Optional

# 明确定义类型别名
JsonData = Union[dict, list]
FilePath = Union[str, Path]

def read_json(file_path: str, encoding: str = 'utf-8') -> Union[dict, list, None]:
    """读取 JSON 文件，成功返回解析后的对象，失败返回 None"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        raise

def read_txt(file_path: FilePath, encoding: str = 'utf-8') -> str:
    """读取文本文件，成功返回内容，失败返回空字符串"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        raise
    

def to_json(data: JsonData, file_path: FilePath, encoding: str = 'utf-8') -> bool:
    """将 JSON 数据写入文件，成功返回 True"""
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, TypeError):
        return False

def to_txt(content: str, file_path: FilePath, encoding: str = 'utf-8') -> bool:
    """将文本写入文件，成功返回 True"""
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except (IOError, TypeError):
        return False