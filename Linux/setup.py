import json
import os
import sys
import termios
from shutil import copytree, rmtree


def get_std_version():
    """获取用户指定的语言标准版本"""
    c_stds = {
        "0": "c11",
        "1": "c17",
        "2": "gnu11",
        "3": "gnu17"
    }
    cpp_stds = {
        "0": "c++11",
        "1": "c++14",
        "2": "c++17",
        "3": "c++20",
        "4": "gnu++11",
        "5": "gnu++14",
        "6": "gnu++17",
        "7": "gnu++20"
    }
    global default_c_std
    global default_cpp_std

    while True:
        print("[0] c11,  [1] c17,  [2] gnu11,  [3] gnu17")
        opt = input("请选择编译器将要使用的C标准版本(默认 c17): ").strip()
        if len(opt) == 0:
            break
        elif opt not in "0123":
            print("错误!!!请输入0或1或2...")
            continue
        default_c_std = c_stds[opt]
        break
    print("")
    while True:
        print("[0] c++11,   [1] c++14,    [2] c++17,    [3] c++20,")
        print("[4] gnu++11, [5] gnu++14,  [6] gnu++17,  [7] gnu++20,")
        opt = input("请选择编译器将要使用的C++标准版本(默认 c++11): ").strip()
        if len(opt) == 0:
            break
        elif opt not in "01234567":
            print("错误!!!请输入0或1或2...")
            continue
        default_cpp_std = cpp_stds[opt]
        break


def read_file(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as fr:
        config = json.loads(fr.read().replace("\'", "\""))
    return config


def write_file(path: str, content: dict) -> None:
    with open(path, 'w', encoding='utf-8') as fw:
        json.dump(content, fw, ensure_ascii=False, indent=4)


def generate_config_file() -> bool:
    Path = os.getenv('PATH').split(':')
    compiler_path = None
    for p in Path:
        try:
            if 'gcc' in os.listdir(p):
                compiler_path = p
                break
        except Exception:
            continue
    if not compiler_path:
        print("警告!!!未找到GCC编译器, 请确保您已经安装GCC编译器, 并已将其添加到'Path'环境变量中!")
        return False

    set_settings_json()
    # set c config files
    set_c_cpp_properties_json(compiler_path, 'c')
    set_tasks_json(compiler_path, 'c')
    set_launch_json(compiler_path, 'c')
    # set cpp config files
    set_c_cpp_properties_json(compiler_path, 'cpp')
    set_tasks_json(compiler_path, 'cpp')
    set_launch_json(compiler_path, 'cpp')
    return True


def set_c_cpp_properties_json(compiler_path: str, language: str):
    """设置c_cpp_properties.json
    Parameter
    ------

    `compiler_path`: str
        编译器路径
    `language`: str
        语言类型, c, c++, ...
    """
    global default_c_std
    global default_cpp_std
    global c_cpp_properties_info
    global c_path
    global cpp_path
    config = c_cpp_properties_info
    config["configurations"][0]['cStandard'] = default_c_std
    config["configurations"][0]['cppStandard'] = default_cpp_std

    if language == "c":
        config['configurations'][0]['compilerPath'] = os.path.join(compiler_path, "gcc")
        write_file(os.path.join(c_path, 'c_cpp_properties.json'), config)
    elif language == "cpp":
        config['configurations'][0]['compilerPath'] = os.path.join(compiler_path, "g++")
        write_file(os.path.join(cpp_path, 'c_cpp_properties.json'), config)


def set_tasks_json(compiler_path: str, language: str):
    """设置tasks.json
    Parameter
    ------

    `compiler_path`: str
        编译器路径
    `language`: str
        语言类型, c, c++, ...
    """
    global tasks_info
    global c_path
    global cpp_path
    config = tasks_info
    compiler = "gcc" if language == "c" else "g++"
    config['tasks'][0]['label'] = f"C/C++: {compiler} 生成活动文件"
    config['tasks'][0]['command'] = os.path.join(compiler_path, compiler)
    config['tasks'][0]['args'] = [
        "-fdiagnostics-color=always",
        "-g",
        "-I",
        "${workspaceFolder}/include",
        "${fileDirname}/" + f"*.{language}",
        "-o",
        "${workspaceFolder}/debug/main"
    ]
    if language == "c":
        write_file(os.path.join(c_path, "tasks.json"), config)
    elif language == "cpp":
        write_file(os.path.join(cpp_path, "tasks.json"), config)


def set_launch_json(compiler_path: str, language: str):
    """设置launch.json
    Parameter
    ------

    `compiler_path`: str
        编译器路径
    `language`: str
        语言类型, c, c++, ...
    """
    global launch_info
    global c_path
    global cpp_path
    config = launch_info
    compiler = "gcc" if language == "c" else "g++"
    config['configurations'][0]['name'] = f"{compiler} - 生成和调试活动文件"
    config['configurations'][0]['miDebuggerPath'] = os.path.join(compiler_path, "gdb")
    config['configurations'][0]['preLaunchTask'] = f"C/C++: {compiler} 生成活动文件"
    if language == "c":
        write_file(os.path.join(c_path, "launch.json"), config)
    elif language == "cpp":
        write_file(os.path.join(cpp_path, "launch.json"), config)


def set_settings_json():
    """设置 Code Runner 的配置参数"""    
    append_command = ' && $workspaceRoot/build/main'
    warning_parameters = ' -Wall -Wpedantic -Wextra'
    global default_c_std
    global default_cpp_std
    global settings_info
    global c_path
    global cpp_path

    settings_info["code-runner.executorMap"]["c"] += f" -std={default_c_std}{warning_parameters}{append_command}"
    settings_info["code-runner.executorMap"]["cpp"] += f" -std={default_cpp_std}{warning_parameters}{append_command}"
    write_file(os.path.join(c_path, 'settings.json'), settings_info)
    write_file(os.path.join(cpp_path, 'settings.json'), settings_info)


def set_shell_config(fpath: str, shell: str="sh"):
    """设置shell配置文件"""
    with open(fpath, 'r', encoding='utf-8') as fr:
        origin_content = fr.readlines()
        start, end = 0, 0
        if origin_content:
            for cnt, line in enumerate(origin_content):
                if line.strip() == '##{{{ C/C++ project initialize':
                    start = cnt
                if start != 0 and line.strip() == '##}}} End C/C++ project initialize':
                    end = cnt + 1
                    break
    global HOME
    if shell == "sh":
        content = '##{{{ C/C++ project initialize\n' \
                + f'source {HOME}/.config/Code/projectTemplate/init_vscode_project.sh\n' \
                + '##}}} End C/C++ project initialize'
    elif shell == "fish":
        content = '##{{{ C/C++ project initialize\n' \
            + f'source {HOME}/.config/Code/projectTemplate/init_vscode_project.fish\n' \
            + '##}}} End C/C++ project initialize'
    with open(fpath, 'w', encoding='utf-8') as fw:
        if not origin_content:
            fw.write(content)
        elif start != 0:
            fw.writelines(origin_content[0:start])
            if len(origin_content[start - 1].strip()) != 0:
                if origin_content[start - 1][-1] != '\n': 
                    fw.write('\n\n')
                else:
                    fw.write('\n')
            fw.write(content)
            if end > start and end < len(origin_content):
                if len(origin_content[end].strip()) != 0:
                    fw.write('\n\n')
                else:
                    fw.write('\n')
                fw.writelines(origin_content[end:])
        else:
            fw.writelines(origin_content)
            fw.write('\n')
            if origin_content[-1][-1] != '\n':
                fw.write('\n')
            fw.write(content)


def generate_template():
    """生成模板目录结构"""
    lang_list = ['c', 'cpp']
    for lang in lang_list:
        build_path = os.path.join('.', 'projectTemplate', lang, 'build')
        debug_path = os.path.join('.', 'projectTemplate', lang, 'debug')
        include_path = os.path.join('.', 'projectTemplate', lang, 'include')
        if os.path.exists(build_path):
            rmtree(build_path)
        if os.path.exists(debug_path):
            rmtree(debug_path)
        if os.path.exists(include_path):
            rmtree(include_path)
        os.mkdir(build_path)
        os.mkdir(debug_path)
        os.mkdir(include_path)


def copy_template():
    """拷贝项目模板到默认模板放置位置"""
    HOME = os.environ['HOME']
    vscode_config_path = f'{HOME}/.config/Code'
    destination = os.path.join(vscode_config_path, 'projectTemplate')
    if not os.path.exists(vscode_config_path):
        os.makedirs(vscode_config_path)
    if os.path.exists(destination):
        rmtree(destination)
    copytree('projectTemplate', destination)


def press_any_key_exit(msg):
    # 获取标准输入的描述符
    fd = sys.stdin.fileno()
    # 获取标准输入(终端)的设置
    old_ttyinfo = termios.tcgetattr(fd)
    # 配置终端
    new_ttyinfo = old_ttyinfo[:]
    # 使用非规范模式(索引3是c_lflag 也就是本地模式)
    new_ttyinfo[3] &= ~termios.ICANON
    # 关闭回显(输入不会被显示)
    new_ttyinfo[3] &= ~termios.ECHO
    # 输出信息
    sys.stdout.write(msg)
    sys.stdout.flush()
    # 使设置生效
    termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
    # 从终端读取
    os.read(fd, 7)
    # 还原终端设置
    termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)


def main():
    print("Visual Studio Code c/c++多文件设置:\n")
    if not os.path.exists(c_path):
        os.mkdir(c_path)
    if not os.path.exists(cpp_path):
        os.mkdir(cpp_path)
    get_std_version()
    if generate_config_file():
        generate_template()
        copy_template()
        global HOME
        bashrc_path = os.path.join(HOME, '.bashrc')
        zshrc_path = os.path.join(HOME, '.zshrc')
        fishconfig_path = os.path.join(HOME, '.config/fish/config.fish')
        if not os.path.exists(bashrc_path):
            fw = open(bashrc_path, 'w', encoding='utf-8')
            fw.close()
        set_shell_config(bashrc_path)

        if os.path.exists(zshrc_path):
            set_shell_config(zshrc_path)

        if os.path.exists(fishconfig_path):
            set_shell_config(fishconfig_path, "fish")
        press_any_key_exit("配置已完成, 请按任意键退出...")
    else:
        press_any_key_exit("\n配置未完成, 请按任意键退出...")


if __name__ == "__main__":
    c_cpp_properties_info = {
        "configurations": [
            {
                "name": "Win32",
                "includePath": [
                    "${workspaceFolder}",
                    "${workspaceFolder}/include"
                ],
                "defines": [
                    "_DEBUG",
                    "UNICODE",
                    "_UNICODE"
                ],
                "compilerPath": "/usr/bin/gcc",
                "cStandard": "gnu11",
                "cppStandard": "gnu++11",
                "intelliSenseMode": "linux-gcc-x64"
            }
        ],
        "version": 4
    }

    launch_info = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "gcc - 生成和调试活动文件",
                "type": "cppdbg",
                "request": "launch",
                "program": "${workspaceFolder}/debug/main",
                "args": [],
                "stopAtEntry": False,
                "cwd": "${workspaceFolder}",
                "environment": [],
                "externalConsole": False,
                "MIMode": "gdb",
                "miDebuggerPath": "/usr/bin/gdb",
                "setupCommands": [
                    {
                        "description": "为 gdb 启用整齐打印",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    }
                ],
                "preLaunchTask": "C/C++: g++ 生成活动文件"
            }
        ]
    }

    tasks_info = {
        "tasks": [
            {
                "type": "cppbuild",
                "label": "C/C++: g++ 生成活动文件",
                "command": "/usr/bin/gcc",
                "args": [
                    "-fdiagnostics-color=always",
                    "-g",
                    "-I",
                    "${workspaceFolder}/include",
                    "${fileDirname}/*.c",
                    "-o",
                    "${workspaceFolder}/debug/main"
                ],
                "options": {
                    "cwd": "${fileDirname}"
                },
                "problemMatcher": [
                    "$gcc"
                ],
                "group": {
                    "kind": "build",
                    "isDefault": True
                },
                "detail": "调试器生成的任务。"
            }
        ],
        "version": "2.0.0"
    }

    settings_info = {
        "explorer.confirmDelete": False,
        "code-runner.runInTerminal": True,
        "files.autoSave": "afterDelay",
        "code-runner.executorMap": {
            
            "c": "cd $workspaceRoot && gcc -I include source/*.c -o $workspaceRoot/build/main",
            "cpp": "cd $workspaceRoot && g++ -I include source/*.cpp -o $workspaceRoot/build/main",
        }
    }

    default_c_std = "c17"  # 默认c标准
    default_cpp_std = "c++11"  # 默认c++标准
    HOME = os.environ['HOME']
    c_path = 'projectTemplate/c/.vscode'
    cpp_path = 'projectTemplate/cpp/.vscode'

    sys.exit(main())
