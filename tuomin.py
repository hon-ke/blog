#!/usr/bin/env python3
"""
简单的脱敏处理，用模板的示例文件替换掉原先的敏感文件
"""
import os
import shutil

# 文件对列表: (敏感文件, 替换的模板文件)
PROCESS_FILE = [
    ("back/.env", "back/.env.temp"),
    ("back/core/db.py", "back/core/db.temp.py")
]

for target, template in PROCESS_FILE:
    if os.path.exists(template):
        if os.path.exists(target):
            os.remove(target)
        shutil.copy2(template, target)
        print(f"[+] {target} 处理成功")

    else:
        print(f"[!] {template} 不存在，{target} 处理失败")

print("[+] 脱敏处理完成")
