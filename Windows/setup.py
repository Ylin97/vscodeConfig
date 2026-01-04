import os
import sys
import json
import msvcrt
from shutil import copytree, rmtree
from pathlib import Path


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


def read_file(path: Path | str) -> dict:
    with open(path, 'r', encoding='utf-8') as fr:
        config = json.loads(fr.read().replace("\'", "\""))
    return config


def write_file(path: Path | str, content: dict) -> None:
    with open(path, 'w', encoding='utf-8') as fw:
        json.dump(content, fw, ensure_ascii=False, indent=4)


def generate_config_file() -> bool:
    """生成配置文件"""
    # request tools path
    ucrt64_bin_path = request_exec_path('gcc', 'D:\\msys64\\ucrt64\\bin')
    msvc_path = request_exec_path('cl', 'C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.35.32215\\bin\\Hostx64\\x64')
    
    # set c/cpp settings.json
    set_settings_json()

    # set c config files
    set_c_cpp_properties_json(ucrt64_bin_path, 'c')
    set_tasks_json(ucrt64_bin_path, 'c')
    set_launch_json(ucrt64_bin_path, 'c')

    # set cpp config files
    set_c_cpp_properties_json(ucrt64_bin_path, 'cpp')
    set_tasks_json(ucrt64_bin_path, 'cpp')
    set_launch_json(ucrt64_bin_path, 'cpp')

    # set modern_cpp config files
    set_modern_cpp_settings_json()
    set_modern_cpp_tasks_json()
    set_modern_cpp_launch_json(ucrt64_bin_path)
    set_modern_cpp_cmake_presets_json(msvc_path, ucrt64_bin_path)

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
        config['configurations'][0]['compilerPath'] = os.path.join(compiler_path, "gcc.exe")
        write_file(os.path.join(c_path, 'c_cpp_properties.json'), config)
    elif language == "cpp":
        config['configurations'][0]['compilerPath'] = os.path.join(compiler_path, "g++.exe")
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
    compiler = "gcc.exe" if language == "c" else "g++.exe"
    config['tasks'][0]['label'] = f"C/C++: {compiler} 生成活动文件"
    config['tasks'][0]['command'] = os.path.join(compiler_path, compiler)
    config['tasks'][0]['args'] = [
        "-fdiagnostics-color=always",
        "-g",
        "-I",
        "${workspaceFolder}\\include",
        "${fileDirname}\\" + f"*.{language}",
        "-o",
        "${workspaceFolder}\\debug\\main.exe"
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
    compiler = "gcc.exe" if language == "c" else "g++.exe"
    config['configurations'][0]['name'] = f"{compiler} - 生成和调试活动文件"
    config['configurations'][0]['miDebuggerPath'] = os.path.join(compiler_path, "gdb.exe")
    config['configurations'][0]['preLaunchTask'] = f"C/C++: {compiler} 生成活动文件"
    if language == "c":
        write_file(os.path.join(c_path, "launch.json"), config)
    elif language == "cpp":
        write_file(os.path.join(cpp_path, "launch.json"), config)


def set_settings_json():
    """设置 Code Runner 的配置参数"""    
    append_command = ' && $workspaceRoot\\build\\main.exe'
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


def set_profile():
    """ 设置 profile.ps1 文件"""
    HOME = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    profile_paths = [os.path.join(HOME, 'Documents', 'PowerShell'), 
                        os.path.join(HOME, 'Documents', 'WindowsPowerShell')]
    
    with open('vscode_profile.ps1', 'r', encoding='utf-8') as fr:
        content = fr.read()     
    for profile_path in profile_paths:
        destination = os.path.join(profile_path, 'profile.ps1')
        # destination = 'profile.ps1'
        origin_content = None
        start, end = 0, 0
        if os.path.exists(destination):
            with open(destination, 'r', encoding='utf-8') as fr:
                origin_content = fr.readlines()
                for cnt, line in enumerate(origin_content):
                    if line.strip() == '#region project initialize':
                        start = cnt
                    if start != 0 and line.strip() == '#endregion':
                        end = cnt + 1
                        break
        else:
            os.makedirs(profile_path)
            
        with open(destination, 'w', encoding='utf-8') as fw:
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


def check_vcpkg_environment_variable() -> bool:
    """检查 vcpkg 环境变量是否存在"""
    vcpkg_root = os.getenv('VCPKG_ROOT', None)
    if not vcpkg_root or not os.path.exists(vcpkg_root):
        print("错误!!! 请先设置 vcpkg 的环境变量 VCPKG_ROOT 指向 vcpkg 安装目录...")
        return False
    else:
        print(f"VCPKG_ROOT = {vcpkg_root}")
    return True


def set_modern_cpp_settings_json():
    """设置 modern_cpp 下的 settings.json"""
    global modern_cpp_settings_info
    global modern_cpp_path
    write_file(os.path.join(modern_cpp_path, 'settings.json'), modern_cpp_settings_info)


def set_modern_cpp_tasks_json():
    """设置 modern_cpp 下的 tasks.json"""
    global modern_cpp__tasks_info
    global modern_cpp_path
    write_file(os.path.join(modern_cpp_path, 'tasks.json'), modern_cpp__tasks_info)


def set_modern_cpp_launch_json(ucrt64_bin_path: str):
    """设置 modern_cpp 下的 launch.json"""
    global modern_cpp_launch_info
    global modern_cpp_path

    # add gcc path to environment PATH
    base_path_env = modern_cpp_launch_info['configurations'][1]['environment'][0]['value']
    modern_cpp_launch_info['configurations'][1]['environment'][0]['value'] = f"{ucrt64_bin_path};${base_path_env}"
    # set miDebuggerPath for GDB config
    modern_cpp_launch_info['configurations'][1]['miDebuggerPath'] = os.path.join(ucrt64_bin_path, "gdb.exe")

    write_file(os.path.join(modern_cpp_path, 'launch.json'), modern_cpp_launch_info)

def set_modern_cpp_cmake_presets_json(cl_path: str, ucrt64_bin_path: str):
    """设置 modern_cpp 下的 CMakePresets.json"""
    global modern_cpp_cmake_presets
    global modern_cpp_path

    # set msvc configurations
    pos = cl_path.find("Community")
    community_path = cl_path[0:pos + len("Community")]

    msvc_ninja_path = os.path.join(community_path, "Common7", "IDE", "CommonExtensions", "Microsoft", "CMake", "Ninja")
    modern_cpp_cmake_presets['configurePresets'][0]['cacheVariables']['CMAKE_MAKE_PROGRAM'] = os.path.join(msvc_ninja_path, "ninja.exe")

    # set ucrt64 configurations
    ninja_path = ucrt64_bin_path
    if "ninja.exe" not in os.listdir(ucrt64_bin_path):
        ninja_path = request_exec_path('ninja', 'D:\\msys64\\ucrt64\\bin')

    modern_cpp_cmake_presets['configurePresets'][1]['environment']['PATH'] = f"{ucrt64_bin_path};$penv{{PATH}}"
    modern_cpp_cmake_presets['configurePresets'][1]['cacheVariables']['CMAKE_MAKE_PROGRAM'] = os.path.join(ninja_path, "ninja.exe")
    modern_cpp_cmake_presets['configurePresets'][1]['cacheVariables']['CMAKE_C_COMPILER'] = os.path.join(ucrt64_bin_path, "gcc.exe")
    modern_cpp_cmake_presets['configurePresets'][1]['cacheVariables']['CMAKE_CXX_COMPILER'] = os.path.join(ucrt64_bin_path, "g++.exe")

    write_file(Path(modern_cpp_path).parent / 'CMakePresets.json', modern_cpp_cmake_presets)


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
    """移动项目模板到默认模板放置位置"""
    HOME = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    vscode_config_path = os.path.join(HOME, '.vscode')
    destination = os.path.join(vscode_config_path, 'projectTemplate')
    if not os.path.exists(vscode_config_path):
        os.makedirs(vscode_config_path)
    if os.path.exists(destination):
        rmtree(destination)
    copytree('projectTemplate', destination)


def main():
    print("Visual Studio Code c/c++多文件设置:\n")
    global c_path
    global cpp_path

    if not check_vcpkg_environment_variable():
        print("\n配置未完成, 请按任意键退出...")
        ord(msvcrt.getch())
        return -1
    else:
        print("vcpkg 环境变量检查通过...\n")

    if not os.path.exists(c_path):
        os.mkdir(c_path)
    if not os.path.exists(cpp_path):
        os.mkdir(cpp_path)
    if not os.path.exists(modern_cpp_path):
        os.mkdir(modern_cpp_path)

    get_std_version()
    if generate_config_file():
        generate_template()
        copy_template()
        set_profile()
        print("配置已完成, 请按任意键退出...")
    else:
        print("\n配置未完成, 请按任意键退出...")

    ord(msvcrt.getch())


def get_input(prompt: str) -> str:
    """获取用户输入"""
    return input(prompt).strip()


def request_exec_path(name: str, example: str) -> str:
    """请求用户输入编译器路径"""
    exec_name = f'{name.lower()}.exe'
    Path = os.getenv('Path', '').split(';')
    exec_path = None
    for p in Path:
        try:
            if exec_name in os.listdir(p):
                exec_path = p
                break
        except Exception:
            continue

    if not exec_path:
        while True:
            path = get_input(f"请输入 {name} 可执行文件所在路径(例如 {example}): ")
            if os.path.exists(path) and exec_name in os.listdir(path):
                exec_path = path
                break
            print(f"错误!!!请输入正确 {name} 可执行文件的路径...\n")
    return exec_path


if __name__ == '__main__':
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
                "compilerPath": "D:\\Tools\\mingw64\\bin\\gcc.exe",
                "cStandard": "gnu11",
                "cppStandard": "gnu++11",
                "intelliSenseMode": "windows-gcc-x64"
            }
        ],
        "version": 4
    }

    launch_info = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "gcc.exe - 生成和调试活动文件",
                "type": "cppdbg",
                "request": "launch",
                "program": "${workspaceFolder}\\debug\\main.exe",
                "args": [],
                "stopAtEntry": False,
                "cwd": "${workspaceFolder}",
                "environment": [],
                "externalConsole": False,
                "MIMode": "gdb",
                "miDebuggerPath": "D:\\Tools\\mingw64\\bin\\gdb.exe",
                "setupCommands": [
                    {
                        "description": "为 gdb 启用整齐打印",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    }
                ],
                "preLaunchTask": "C/C++: g++.exe 生成活动文件"
            }
        ]
    }

    tasks_info = {
        "tasks": [
            {
                "type": "cppbuild",
                "label": "C/C++: g++.exe 生成活动文件",
                "command": "D:\\Tools\\mingw64\\bin\\gcc.exe",
                "args": [
                    "-fdiagnostics-color=always",
                    "-g",
                    "-I",
                    "${workspaceFolder}\\include",
                    "${fileDirname}\\*.c",
                    "-o",
                    "${workspaceFolder}\\debug\\main.exe"
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
            
            "c": "cd $workspaceRoot && gcc -I include source\\*.c -o $workspaceRoot\\build\\main.exe",
            "cpp": "cd $workspaceRoot && g++ -I include source\\*.cpp -o $workspaceRoot\\build\\main.exe",
        }
    }

    #=======================================================
    #         Modern Cpp Project Configurations
    #=======================================================

    modern_cpp_settings_info = {
        "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools"
    }

    modern_cpp__tasks_info = {
        "version": "2.0.0",
        "tasks": [
            {
            "label": "build-msvc-debug",
            "type": "shell",
            "command": "cmake",
            "args": [
                "--build",
                "${workspaceFolder}/build/msvc-vs-debug",
                "--target",
                "example"
            ],
            "problemMatcher": [],
            "group": {
                "kind": "build",
                "isDefault": True
            }
            },
            {
            "label": "build-ucrt64-debug",
            "type": "shell",
            "command": "cmake",
            "args": [
                "--build",
                "${workspaceFolder}/build/ucrt64-debug",
                "--target",
                "example"
            ],
            "problemMatcher": [],
            "group": "build"
            }
        ]
    }

    modern_cpp_launch_info = {
    "version": "0.2.0",
    "configurations": [
            {
            # MSVC 原生调试器，无需配置 GDB/MI
            "name": "Debug with MSVC",
            "type": "cppvsdbg",
            "request": "launch",
            # CMake Tools 会解析为当前 launch target 的输出全路径
            "program": "${command:cmake.launchTargetPath}",
            "args": [],
            "stopAtEntry": False,
            # 把工作目录设置为可执行文件所在目录，方便 DLL 加载等
            "cwd": "${command:cmake.getLaunchTargetDirectory}",
            "environment": [
                {
                "name": "PATH",
                "value": "${command:cmake.getLaunchTargetDirectory};${env:PATH}"
                }
            ],
            # 使用 VSCode 的集成终端
            "console": "integratedTerminal",
            # 若你希望使用外部终端，可以改为:
            # "console": "externalTerminal",
            "preLaunchTask": "build-msvc-debug"
            },
            {
            # GDB (MinGW-w64 / MSYS2 UCRT64) 使用 MI 协议，需要指定调试器
            "name": "Debug with GDB",
            "type": "cppdbg",
            "request": "launch",
            "program": "${command:cmake.launchTargetPath}",
            "args": [],
            "stopAtEntry": False,
            "cwd": "${command:cmake.getLaunchTargetDirectory}",
            "environment": [
                {
                "name": "PATH",
                "value": "${command:cmake.getLaunchTargetDirectory};${env:PATH}"
                }
            ],
            "externalConsole": False, # 使用系统终端可避免字符集或输入问题
            "MIMode": "gdb", # 指定 MI 模式为 gdb
            "miDebuggerPath": "D:/msys64/ucrt64/bin/gdb.exe", # GDB 可执行路径
            "setupCommands": [ # GDB 启动时的初始化命令
                {
                "description": "Enable pretty-printing for gdb",
                "text": "-enable-pretty-printing",
                "ignoreFailures": True
                }
            ], 
            "preLaunchTask": "build-ucrt64-debug"
            }
        ]
    }

    modern_cpp_cmake_presets = {
        "version": 8,
        "cmakeMinimumRequired": {
            "major": 3,
            "minor": 23,
            "patch": 0
        },
        "configurePresets": [
            {
            "name": "msvc-vs",
            "displayName": "MSVC + VS Ninja (base)",
            "generator": "Ninja",
            "binaryDir": "${sourceDir}/build/${presetName}",
            "installDir": "${sourceDir}/install/${presetName}",
            "cacheVariables": {
                "CMAKE_MAKE_PROGRAM": "D:/Program Files/Microsoft Visual Studio/2022/Community/Common7/IDE/CommonExtensions/Microsoft/CMake/Ninja/ninja.exe",
                "CMAKE_TOOLCHAIN_FILE": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake",
                "VCPKG_TARGET_TRIPLET": "x64-windows",
                "VCPKG_MANIFEST_MODE": "ON"
            }
            },
            {
            "name": "ucrt64",
            "displayName": "MinGW-w64 UCRT64 + MSYS2 Ninja (base)",
            "generator": "Ninja",
            "binaryDir": "${sourceDir}/build/${presetName}",
            "installDir": "${sourceDir}/install/${presetName}",
            "environment": {
                "PATH": "D:\\msys64\\ucrt64\\bin;$penv{PATH}"
            },
            "cacheVariables": {
                "CMAKE_MAKE_PROGRAM": "D:/msys64/ucrt64/bin/ninja.exe",
                "CMAKE_C_COMPILER": "D:/msys64/ucrt64/bin/gcc.exe",
                "CMAKE_CXX_COMPILER": "D:/msys64/ucrt64/bin/g++.exe",
                "CMAKE_TOOLCHAIN_FILE": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake",
                "VCPKG_TARGET_TRIPLET": "x64-mingw-dynamic",
                "VCPKG_MANIFEST_MODE": "ON"
            }
            },

            {
            "name": "msvc-vs-debug",
            "inherits": "msvc-vs",
            "displayName": "MSVC Debug",
            "cacheVariables": { "CMAKE_BUILD_TYPE": "Debug" }
            },
            {
            "name": "msvc-vs-release",
            "inherits": "msvc-vs",
            "displayName": "MSVC Release",
            "cacheVariables": { "CMAKE_BUILD_TYPE": "Release" }
            },
            {
            "name": "msvc-vs-minsizerel",
            "inherits": "msvc-vs",
            "displayName": "MSVC MinSizeRel",
            "cacheVariables": { "CMAKE_BUILD_TYPE": "MinSizeRel" }
            },

            {
            "name": "ucrt64-debug",
            "inherits": "ucrt64",
            "displayName": "UCRT64 Debug",
            "cacheVariables": { "CMAKE_BUILD_TYPE": "Debug" }
            },
            {
            "name": "ucrt64-release",
            "inherits": "ucrt64",
            "displayName": "UCRT64 Release",
            "cacheVariables": { "CMAKE_BUILD_TYPE": "Release" }
            },
            {
            "name": "ucrt64-minsizerel",
            "inherits": "ucrt64",
            "displayName": "UCRT64 MinSizeRel",
            "cacheVariables": { "CMAKE_BUILD_TYPE": "MinSizeRel" }
            }
        ],

        "buildPresets": [
            { "name": "build-msvc-debug",        "configurePreset": "msvc-vs-debug" },
            { "name": "build-msvc-release",      "configurePreset": "msvc-vs-release" },
            { "name": "build-msvc-minsizerel",   "configurePreset": "msvc-vs-minsizerel" },

            { "name": "build-ucrt64-debug",      "configurePreset": "ucrt64-debug" },
            { "name": "build-ucrt64-release",    "configurePreset": "ucrt64-release" },
            { "name": "build-ucrt64-minsizerel", "configurePreset": "ucrt64-minsizerel" }
        ]
    }

    default_c_std = "c17"  # 默认c标准
    default_cpp_std = "c++11"  # 默认c++标准
    c_path = 'projectTemplate\\c\\.vscode'
    cpp_path = 'projectTemplate\\cpp\\.vscode'
    modern_cpp_path = 'projectTemplate\\ModernCpp\\.vscode'

    sys.exit(main())