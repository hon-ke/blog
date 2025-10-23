from os import name
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import time
import atexit
import traceback

from colorama import Back
from pydantic_core.core_schema import BoolSchema

# 跨平台颜色支持
try:
    from colorama import init, Fore, Style

    init(autoreset=True)  # 自动重置颜色
except ImportError:

    class ColorDummy:
        def __getattr__(self, name):
            return ""

    Fore = ColorDummy()
    Style = ColorDummy()


class TermianlLogger:
    """带颜色输出的日志工具类"""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.BLUE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Back.RED,
    }

    SYMBLE = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL",
    }

    def __init__(
        self,
        name: Optional[str] = None,
        date_format: Optional[str] = None,
        level: Optional[str] = "DEBUG",
        log_path: Optional[str] = None,
        show_level:Optional[bool] = True,
        show_symble: Optional[dict] = {
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL",
        },
    ):
        """
        初始化日志记录器
        :param name: 日志器名称
        :param level: 日志级别 [DEBUG|INFO|WARNING|SUCCESS|ERROR]
        :param date_format: 日期格式化字符串，None或False时不显示
        :param log_path: 日志文件路径
        """
        self.name = name.upper() + "" if name else ""
        self.level = level.upper()
        self.level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.date_format = date_format
        self.log_path = log_path
        self.show_level = show_level
        self.SYMBLE = show_symble

        # 文件写入相关配置
        self.file_handle = None
        self._buffer = []
        self.buffer_size = 1000  # 缓冲区大小（可调）
        self.flush_interval = 1.0  # 自动刷新间隔（秒）
        self.last_flush_time = time.time()

        # 初始化文件句柄
        if self.log_path is not None and self.log_path != False:
            try:
                self.file_handle = open(
                    self.log_path, "a", encoding="utf-8", buffering=1
                )
                atexit.register(self._force_flush)  # 注册退出时强制刷新
            except Exception as e:
                self._error("Failed to initialize log file", exception=e)

    def _get_color(self, level: str) -> str:
        """获取对应级别的颜色"""
        return self.COLORS.get(level, Fore.WHITE)

    def _set_symble(self,level:str) ->str:
        return self.SYMBLE.get(level,level.upper())

    def _should_log(self, level: str) -> bool:
        """判断是否应该记录该级别日志"""
        return self.level_order.index(level) >= self.level_order.index(self.level)

    def _flush_buffer(self):
        """强制将缓冲区内容写入文件"""
        if not self._buffer or self.file_handle is None:
            return
        try:
            # 批量写入并添加换行符
            self.file_handle.write("\n".join(self._buffer) + "\n")
            self._buffer.clear()
            self.last_flush_time = time.time()
        except Exception as e:
            self._error(f"Buffer flush failed: {e}", exception=e)

    def _force_flush(self):
        """程序退出时强制刷新缓冲区"""
        self._flush_buffer()

    def _log(self, level: str, *args: Any, **kwargs) -> str:
        """通用日志记录方法"""
        if not self._should_log(level):
            return ""

        # 日志需要记录的内容

        # 处理位置参数（自动转为字符串并用空格连接）
        message_parts = []
        for arg in args:
            if isinstance(arg, (dict, list, tuple)):
                # 支持复杂类型显示
                message_parts.append(repr(arg))
            else:
                message_parts.append(str(arg))
        message = " ".join(message_parts)
        # 处理时间戳
        timestamp = datetime.now().strftime(self.date_format or "%Y-%m-%d %H:%M:%S ")
        terminal_timestamp = ""
        if self.date_format not in (None, False):
            terminal_timestamp = (
                f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}{timestamp}{Style.RESET_ALL} "
            )

        color = self._get_color(level)

        symble = self._set_symble(level)
        # 处理日志级别显示
        terminal_level_display = f"{color}{symble}{Style.RESET_ALL} " if self.show_level and symble else ""

        # 分离带颜色和无颜色日志内容
        _log_name = f"[{self.name}] " if self.name else ""
        terminal_log_msg = (
            f"{terminal_timestamp}"
            f"{color}{Style.BRIGHT}{_log_name}{Style.RESET_ALL}"
            f"{terminal_level_display}{message}"
        )

        _log_file_name = f"[{self.name}] " if self.name else ""
        file_level_display = f"{symble} " if self.show_level and symble else ""
        file_log_msg = (
            f"{timestamp}" f"{_log_file_name}" f"{file_level_display}{message}"
        )

        # 输出到控制台
        stream = sys.stderr if level == "ERROR" else sys.stdout
        stream.write(terminal_log_msg + "\n")
        stream.flush()

        # 处理上下文信息并生成纯文本日志
        log_context = self._log_context(kwargs)
        full_log = f"{file_log_msg}{log_context}"

        # 异步写入文件
        if self.log_path is not None and self.log_path != False:
            self._buffer.append(full_log)
            current_time = time.time()

            # 触发缓冲刷新条件
            if (
                len(self._buffer) >= self.buffer_size
                or (current_time - self.last_flush_time) >= self.flush_interval
            ):
                self._flush_buffer()

        return full_log

    def _log_context(self, context: Dict[str, Any]) -> str:
        """记录日志额外上下文信息"""
        if not context:
            return ""

        return_context = ""

        max_key_length = max(len(key) for key in context.keys()) if context else 0
        for key, value in context.items():
            # 重点修改：去除复杂类型的外层单引号
            if isinstance(value, (dict, list, tuple)):
                formatted_value = repr(value)  # 去掉首尾的单引号
            elif isinstance(value, str):
                formatted_value = f"'{value}'"
            else:
                formatted_value = str(value)

            terminal_context = (
                f"{Fore.LIGHTBLACK_EX}│ {key:>{max_key_length}} : {formatted_value}\n"
            )
            file_context = f"\n│ {key:>{max_key_length}} : {formatted_value}"
            return_context += file_context
            sys.stdout.write(terminal_context)

        sys.stdout.flush()

        return return_context

    def _error(self, message: str, exception: Exception = None):
        """内部错误处理"""
        if exception is not None:
            message += f": {exception}\n{traceback.format_exc()}"
        print(f"Logger error: {message}", file=sys.stderr)

    def debug(self, *args, **kwargs):
        return self._log("DEBUG", *args, **kwargs)

    def info(self, *args, **kwargs):
        return self._log("INFO", *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._log("WARNING", *args, **kwargs)

    def error(self, *args, **kwargs):
        return self._log("ERROR", *args, **kwargs)

    def critical(self, *args, **kwargs):
        return self._log("CRITICAL", *args, **kwargs)


log = TermianlLogger()

# 使用示例
if __name__ == "__main__":
    # 测试不同日志级别
    class_methods_dict = {
        "__init__": "构造函数，初始化对象实例",
        "__str__": "返回对象的字符串表示，用于print()",
        "__repr__": "返回对象的官方字符串表示，用于调试",
        "__eq__": "定义对象相等比较行为",
        "__lt__": "定义对象小于比较行为",
        "__gt__": "定义对象大于比较行为",
        "__len__": "返回对象的长度",
        "__getitem__": "定义索引访问行为 obj[key]",
        "__setitem__": "定义索引赋值行为 obj[key] = value",
        "__delitem__": "定义索引删除行为 del obj[key]",
        "__iter__": "返回迭代器对象",
        "__next__": "获取下一个迭代值",
        "__call__": "使实例可以像函数一样调用",
        "__enter__": "上下文管理器进入时调用",
        "__exit__": "上下文管理器退出时调用",
        "__getattr__": "当访问不存在的属性时调用",
        "__setattr__": "当设置属性时调用",
        "__delattr__": "当删除属性时调用",
        "__add__": "定义加法行为 +",
        "__sub__": "定义减法行为 -",
        "__mul__": "定义乘法行为 *",
        "__div__": "定义除法行为 /",
        "__hash__": "返回对象的哈希值",
        "__bool__": "定义对象的布尔值转换",
        "__format__": "定义格式化输出行为",
        "__new__": "创建对象实例，在__init__之前调用",
        "__del__": "析构函数，对象被销毁时调用",
        "__contains__": "定义in操作符行为",
        "__getattribute__": "每次属性访问时都调用",
        "__dir__": "返回对象的属性列表",
        "__sizeof__": "返回对象占用的内存大小",
        "__instancecheck__": "定义isinstance()行为",
        "__subclasscheck__": "定义issubclass()行为",
    }

    log.debug(12138, **class_methods_dict)
    log.info(12138, **class_methods_dict)
    log.warning(12138, **class_methods_dict)
    log.error(12138, **class_methods_dict)
    log.critical(12138, **class_methods_dict)
