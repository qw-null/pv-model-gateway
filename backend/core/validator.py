# backend/core/validator.py
import ast

FORBIDDEN_MODULES = {
    "os", "subprocess", "sys", "socket", "shutil",
    "importlib", "ctypes", "multiprocessing", "threading",
    "signal", "resource", "pty", "termios", "fcntl"
}


def validate_meta_code(source_code: str) -> dict:
    """
    校验 meta.py 代码：
    - 只检查 MODEL_META 是否存在且结构完整
    - 不要求包含 run() 函数（run 在 model.py 中）
    """
    errors = []
    warnings = []

    # 1. 语法检查
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"valid": False, "errors": [f"语法错误: {e}"], "warnings": []}

    # 2. 检查 MODEL_META 是否存在
    top_assign_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    top_assign_names.add(target.id)

    if "MODEL_META" not in top_assign_names:
        errors.append("缺少必要定义: MODEL_META")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # 3. 检查 MODEL_META 字段完整性
    meta_errors = _validate_meta_structure(tree)
    errors.extend(meta_errors)

    # 4. 检查危险模块导入
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in FORBIDDEN_MODULES:
                    errors.append(f"禁止导入危险模块: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split(".")[0]
                if mod in FORBIDDEN_MODULES:
                    errors.append(f"禁止导入危险模块: {node.module}")

    # 5. 警告：存在多余的函数定义（meta.py 不应包含函数）
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            warnings.append(
                f"meta.py 中发现函数定义 '{node.name}'，"
                f"建议将执行逻辑放在 model.py 中"
            )

    return {
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings,
    }


def validate_model_code(source_code: str) -> dict:
    """
    校验 model.py 代码：
    - 检查 run() 函数是否存在
    - 检查危险模块导入
    """
    errors = []
    warnings = []

    # 1. 语法检查
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"valid": False, "errors": [f"语法错误: {e}"], "warnings": []}

    # 2. 检查 run 函数是否存在
    func_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_names.add(node.name)

    if "run" not in func_names:
        errors.append("缺少必要函数: run(inputs: dict) -> dict")

    # 3. 检查危险模块导入
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in FORBIDDEN_MODULES:
                    errors.append(f"禁止导入危险模块: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split(".")[0]
                if mod in FORBIDDEN_MODULES:
                    errors.append(f"禁止导入危险模块: {node.module}")

    # 4. 警告：run 函数没有返回类型注解
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            if not node.returns:
                warnings.append("建议为 run() 函数添加返回类型注解: -> dict")

    return {
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings,
    }


def _validate_meta_structure(tree: ast.AST) -> list:
    """检查 MODEL_META 字典的必要字段"""
    errors = []
    required_keys = {"name", "title", "inputs", "outputs"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "MODEL_META":
                    if not isinstance(node.value, ast.Dict):
                        errors.append("MODEL_META 必须是字典类型")
                        return errors

                    present_keys = set()
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant):
                            present_keys.add(key.value)

                    missing = required_keys - present_keys
                    for k in sorted(missing):
                        errors.append(f"MODEL_META 缺少必要字段: '{k}'")
    return errors
