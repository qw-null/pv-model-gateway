"""
沙箱执行封装：通过 RestrictedPython 提供额外的代码安全层（可选增强）
当前主要依赖进程隔离作为安全手段，此模块提供辅助白名单控制。
"""

ALLOWED_BUILTINS = {
    "abs", "all", "any", "bin", "bool", "bytes", "callable",
    "chr", "dict", "dir", "divmod", "enumerate", "filter",
    "float", "format", "frozenset", "getattr", "hasattr",
    "hash", "hex", "int", "isinstance", "issubclass", "iter",
    "len", "list", "map", "max", "min", "next", "oct", "ord",
    "pow", "print", "range", "repr", "reversed", "round",
    "set", "setattr", "slice", "sorted", "str", "sum",
    "tuple", "type", "vars", "zip",
    # 数学
    "__import__",  # 允许 import，但在 validator 层面限制危险模块
}

def get_safe_globals() -> dict:
    """返回受限的全局命名空间，供沙箱执行使用"""
    import builtins
    safe_builtins = {k: getattr(builtins, k) for k in ALLOWED_BUILTINS if hasattr(builtins, k)}
    return {"__builtins__": safe_builtins}
