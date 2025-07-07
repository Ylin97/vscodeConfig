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


def prompt_vcpkg_root():
    while True:
        path = input("请输入 vcpkg 可执行文件所在目录（例如 ~/.local/opt/vcpkg/）: ").strip()
        expanded = os.path.expanduser(path)
        if Path(expanded).joinpath("vcpkg").exists():
            return expanded
        print("❌ 无法在指定目录找到 vcpkg 可执行文件。请重试。")


def update_shell_configs(vcpkg_root: str):
    for shell, config in SHELL_CONFIGS.items():
        shell_block = config[1].format(vcpkg_root=vcpkg_root)
        file_path = Path(os.path.expanduser(config[0]))
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
    if not os.path.exists(vscode_config_template_path):
        os.makedirs(vscode_config_template_path)
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(Path('./projectTemplate/ModernCpp'), destination)
        
    
def main():
    check_toolchain()
    vcpkg_root = prompt_vcpkg_root()
    print("\n🔧 正在更新用户 shell 配置...")
    update_shell_configs(vcpkg_root)
    if is_installed("fish"):
        force_symlink(Path(vcpkg_root) / "scripts/vcpkg_completion.fish", 
                     os.path.expanduser("~/.config/fish/completions/vcpkg.fish"))

    cmake_file_path = Path("./projectTemplate/ModernCpp/CMakeLists.txt")
    if cmake_file_path.exists():
        std = get_cxx_std()
        update_cmakelists(cmake_file_path, std)
        
    copy_template()
    print("\n✅ 恭喜，VSCode 配置已完成！")

if __name__ == "__main__":
    main()
