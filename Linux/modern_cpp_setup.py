import os
import re
import shutil
from pathlib import Path


SUPPORTED_DISTROS = {
    "arch": "sudo pacman -S --needed --noconfirm",
    "ubuntu": "sudo apt install -y",
    "debian": "sudo apt install -y",
    "fedora": "sudo dnf install -y",
    "opensuse": "sudo zypper install -y",
}

REQUIRED_TOOLS = {
    "git": "git",
    "cmake": "cmake",
    "ninja": "ninja",
    "vscode": "code",
    "g++": "g++",
    "gdb": "gdb",
}

BASH_INSERT_TEMPLATE = """# >>> modern cpp initialize >>>
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH=\"$HOME/.local/bin:$PATH\"
fi

# vcpkg
export VCPKG_ROOT=\"{vcpkg_root}\"
source $VCPKG_ROOT/scripts/vcpkg_completion.bash
# <<< modern cpp initialize <<<
"""

ZSH_INSERT_TEMPLATE = """# >>> modern cpp initialize >>>
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH=\"$HOME/.local/bin:$PATH\"
fi

# vcpkg
export VCPKG_ROOT=\"{vcpkg_root}\"
autoload bashcompinit
bashcompinit
source $VCPKG_ROOT/scripts/vcpkg_completion.zsh
# <<< modern cpp initialize <<<
"""

FISH_INSERT_TEMPLATE = """# >>> modern cpp initialize >>>
if not contains "$HOME/.local/bin" $PATH
    set -gx PATH $HOME/.local/bin $PATH
end

# vcpkg
set -gx VCPKG_ROOT \"{vcpkg_root}\"
# <<< modern cpp initialize <<<
"""

SHELL_CONFIGS = {
    "bash": ("~/.bashrc", BASH_INSERT_TEMPLATE),
    "zsh": ("~/.zshrc", ZSH_INSERT_TEMPLATE),
    "fish": ("~/.config/fish/config.fish", FISH_INSERT_TEMPLATE)
}

NEW_CPP_PROJECT_CMD = """#!/usr/bin/env bash

#────────────────────────────
# 初始化 CMake + vcpkg + VSCode 项目（Linux版）
# 默认模板：$HOME/.config/Code/projectTemplate/ModernCpp
#────────────────────────────

set -e

# 默认值
PROJECT_NAME_RAW=$(basename "$PWD")
TEMPLATE_PATH="$HOME/.config/Code/projectTemplate/ModernCpp"

# 显示帮助信息
show_help() {
    cat <<EOF
用法: new-cpp-project [选项]

选项:
  -n, --name <项目名>       指定项目名称（默认使用当前目录名）
  -t, --template <路径>     指定模板路径（默认：$HOME/.config/Code/projectTemplate/ModernCpp）
  -h, --help                显示此帮助信息

说明:
  本工具将初始化一个基于 CMake + vcpkg + VS Code 的 C++ 项目：
    - 复制模板文件
    - 替换 "example" 为你的项目名
    - 初始化 Git 和 vcpkg
    - 打开 VS Code（如果已安装）

示例:
  new-cpp-project
  new-cpp-project -n MyApp
  new-cpp-project -n Engine -t ~/Templates/ModernCpp
EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--name)
            PROJECT_NAME_RAW="$2"
            shift 2
            ;;
        -t|--template)
            TEMPLATE_PATH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "❌ 未知参数: $1"
            echo "请使用 --help 查看用法。"
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

#──────────────── 规范化项目名 ────────────────
PROJECT_NAME=$(echo "$PROJECT_NAME_RAW" | tr '[:upper:]' '[:lower:]' | sed 's/[ _]/-/g; s/[^a-z0-9\\-]//g')

if [[ "$PROJECT_NAME" != "$PROJECT_NAME_RAW" ]]; then
    echo "⚠️ 项目名 [$PROJECT_NAME_RAW] 已规范化为 [$PROJECT_NAME] 以符合 vcpkg 要求。"
fi

#──────────────── 工具检查 ───────────────────
check_tool() {
    if ! command -v "$1" &>/dev/null; then
        echo "⚠️ 未找到 $1，相关步骤将跳过。"
        return 1
    fi
    return 0
}

HAS_GIT=0; check_tool git && HAS_GIT=1
HAS_VCPKG=0; check_tool vcpkg && HAS_VCPKG=1
HAS_CODE=0; check_tool code && HAS_CODE=1

#──────────────── 复制模板 ───────────────────
if [[ ! -d "$TEMPLATE_PATH" ]]; then
    echo "❌ 模板路径 [$TEMPLATE_PATH] 不存在。"
    exit 1
fi

shopt -s dotglob nullglob
cp -r "$TEMPLATE_PATH/"* .
shopt -u dotglob nullglob

#──────────────── 替换占位符 ────────────────
find . -type f \\( -name "*.cpp" -o -name "*.h" -o -name "*.txt" -o -name "*.cmake" -o -name "CMakeLists.txt" -o -name "vcpkg.json" -o -name "launch.json" -o -name "tasks.json" \\) | while read -r file; do
    sed -i "s/\\bexample\\b/$PROJECT_NAME/g" "$file"
done

#──────────────── 重命名头文件 ──────────────
OLD_HEADER="src/include/example.h"
if [[ -f "$OLD_HEADER" ]]; then
    NEW_LEAF="$PROJECT_NAME.h"
    mv "$OLD_HEADER" "src/include/$NEW_LEAF"
    sed -i "s/\\"example.h\\"/\\"$NEW_LEAF\\"/" src/source/main.cpp
fi

#──────────────── vcpkg new ──────────────────
if [[ "$HAS_VCPKG" -eq 1 ]]; then
    if [[ -f vcpkg.json ]]; then
        echo "⚠️ 已存在 vcpkg.json，跳过 vcpkg new。"
    else
        echo "▶ 运行: vcpkg new --name=$PROJECT_NAME --version=0.1.0"
        vcpkg new --name="$PROJECT_NAME" --version=0.1.0
    fi
fi

#──────────────── Git 初始化 ────────────────
if [[ "$HAS_GIT" -eq 1 ]]; then
    if [[ ! -d .git ]]; then
        git init
    fi
    git add . || true
    git commit -m "Initialized $PROJECT_NAME project." || true
fi

#──────────────── 打开 VS Code ───────────────
if [[ "$HAS_CODE" -eq 1 ]]; then
    code src/source/main.cpp
fi

echo "✅ [$PROJECT_NAME] 初始化完成！"
"""


def detect_distro():
    try:
        with open("/etc/os-release") as f:
            data = f.read().lower()
            for key in SUPPORTED_DISTROS:
                if key in data:
                    return key
    except FileNotFoundError:
        pass
    return None


def is_installed(tool):
    return shutil.which(tool) is not None


def check_toolchain():
    print("\n🔍 正在检查工具链...")
    missing = []
    for name, binary in REQUIRED_TOOLS.items():
        if not is_installed(binary):
            missing.append(name)
        else:
            print(f"✅ {name} 已安装。")

    if missing:
        print("\n❌ 以下工具未安装:", ", ".join(missing))
        distro = detect_distro()
        if distro in SUPPORTED_DISTROS:
            install_cmd = SUPPORTED_DISTROS[distro]
            packages = " ".join([REQUIRED_TOOLS[t] for t in missing])
            print(f"\n🔧 请运行以下命令安装缺失工具：\n{install_cmd} {packages}")
        else:
            print("⚠️ 无法识别您的系统，请手动安装缺失的工具。")
        exit(1)


def prompt_vcpkg_root() -> Path:
    while True:
        path = input("请输入 vcpkg 可执行文件所在目录（例如 ~/.local/opt/vcpkg）: ").strip()
        expanded = Path(path).expanduser()
        if expanded.joinpath("vcpkg").exists():
            return expanded
        print("❌ 无法在指定目录找到 vcpkg 可执行文件。请重试。")


def update_shell_configs(vcpkg_root: Path):
    for shell, config in SHELL_CONFIGS.items():
        shell_block = config[1].format(vcpkg_root=vcpkg_root)
        file_path = Path(config[0]).expanduser()
        if not file_path.exists():
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start_tag = "# >>> modern cpp initialize >>>"
        end_tag = "# <<< modern cpp initialize <<<"
        in_block = False
        new_lines = []
        replaced = False

        for line in lines:
            if start_tag in line:
                in_block = True
                new_lines.append(shell_block)
                replaced = True
                continue
            if end_tag in line and in_block:
                in_block = False
                continue
            if not in_block:
                new_lines.append(line)

        if not replaced:
            new_lines.append("\n\n" + shell_block + "\n")

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ 已更新 {file_path.name} 配置。")


def get_cxx_std() -> str:
    cpp_stds = {
        "0": "11", "1": "14", "2": "17", "3": "20",
        "4": "11", "5": "14", "6": "17", "7": "20"
    }
    while True:
        print("[0] c++11,   [1] c++14,    [2] c++17,    [3] c++20,")
        print("[4] gnu++11, [5] gnu++14,  [6] gnu++17,  [7] gnu++20")
        opt = input("请选择编译器将要使用的C++标准版本(默认 c++20): ").strip()
        if len(opt) == 0:
            return "20"
        elif opt in cpp_stds:
            return cpp_stds[opt]
        print("错误!!!请输入 0~7 内的数字。")


def update_cmakelists(file_path: Path, new_std: str):
    if not file_path.exists():
        print("未找到 CMakeLists.txt")
        return
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    pattern = r'(set\s*\(\s*CMAKE_CXX_STANDARD\s+)(\d+)(\s*\))'
    new_content, count = re.subn(pattern, rf'\g<1>{new_std}\g<3>', content)
    if count == 0:
        print("未找到 CMAKE_CXX_STANDARD 设置项。")
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"✅ CMAKE_CXX_STANDARD 已设置为 {new_std}")


def force_symlink(src, dst):
    # 如果目标路径已存在（无论是文件、目录还是链接），先删除
    if os.path.lexists(dst):  # 注意：lexists 不会跟踪符号链接
        os.remove(dst)
    os.symlink(src, dst)


def copy_template():
    """拷贝项目模板到默认模板放置位置"""
    HOME = os.environ['HOME']
    vscode_config_template_path = Path(f'{HOME}/.config/Code/projectTemplate')
    destination = vscode_config_template_path / 'ModernCpp'
    if not vscode_config_template_path.exists():
        vscode_config_template_path.mkdir(parents=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(Path('./projectTemplate/ModernCpp'), destination)


def generate_init_script():
    """生成项目初始化脚本 (命令)"""
    user_bin_path = Path("~/.local/bin").expanduser()
    if not user_bin_path.exists():
        user_bin_path.mkdir(parents=True)
    
    cmd_path = user_bin_path / "new-cpp-project"
    with open(cmd_path, "w", encoding="utf-8") as f:
        f.write(NEW_CPP_PROJECT_CMD)
    cmd_path.chmod(0o755)
        
    
def config_modern_cpp():
    check_toolchain()
    vcpkg_root = prompt_vcpkg_root()
    print("\n🔧 配置 vcpkg...")
    vcpkg_cmd = vcpkg_root / "vcpkg"
    dst_path = Path("~/.local/bin/vcpkg").expanduser()
    if not dst_path.exists():
        dst_path.mkdir(parents=True)
    force_symlink(vcpkg_cmd, dst_path)

    print("\n🔧 正在更新用户 shell 配置...")
    update_shell_configs(vcpkg_root)
    if is_installed("fish"):
        force_symlink(vcpkg_root / "scripts/vcpkg_completion.fish", 
                     Path("~/.config/fish/completions/vcpkg.fish").expanduser())

    cmake_file_path = Path("./projectTemplate/ModernCpp/CMakeLists.txt")
    if cmake_file_path.exists():
        std = get_cxx_std()
        update_cmakelists(cmake_file_path, std)
        
    copy_template()
    generate_init_script()
    print("\n✅ 恭喜，VSCode 配置已完成！")


if __name__ == "__main__":
    config_modern_cpp()
