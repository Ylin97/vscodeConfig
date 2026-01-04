# VSCode C/C++ 开发模板

一个为 **Visual Studio Code** 打造的 **C/C++ 开发模板项目**，包含编译和调试配置，支持以下两种工作模式：

- **✅ Code Runner 模式**：基于 `C/C++` 插件和 `Code Runner` 插件，适用于**单文件**或**简单多文件**项目。
- **✅ 现代 C++ 模式**：基于 `C/C++` 插件和 `CMake Tools` 插件，适用于**工程化开发**，支持 CMake 构建、第三方库管理（vcpkg）、多平台编译。

------

## 📌 功能亮点

- 自动生成 **标准 C/C++ 项目结构**。
- 支持 **GCC / MSVC / Clang** 工具链。
- 集成 **CMake + Ninja + vcpkg**，现代 C++ 项目管理最佳实践。
- 兼容 **Windows** 和 **Linux** 平台。
- 一键初始化项目，支持 `Init-c` / `Init-cpp` / `new-cpp-project` 命令。

------

## 🚀 快速开始

### 模式一：Code Runner 模式（轻量级）

#### Step 1. 安装插件

通过 VSCode 插件市场安装：

- `C/C++`
- `Code Runner`

#### Step 2. 配置环境

**Windows**

```bash
cd Windows
python setup.py
# 或运行预编译的 setup_win.exe
```

**Linux**

```bash
cd Linux
python setup.py

# 如果需要 Modern Cpp，请执行下面的脚本进行配置
python modern_cpp_setup.py
```

#### Step 3. 初始化项目

在 VSCode 终端（`Ctrl + J`）执行：

| 命令        | 功能                |
| ----------- | ------------------- |
| `Init-c`    | 初始化 **C 项目**   |
| `Init-cpp`  | 初始化 **C++ 项目** |
| `Reset-c`   | 重置 **C 项目**     |
| `Reset-cpp` | 重置 **C++ 项目**   |

初始化后，项目结构如下：

```
.
├── .gitignore       # Git 忽略文件
├── .vscode/         # VSCode 配置文件
├── build/           # Release 构建产物（无调试信息）
├── debug/           # Debug 构建产物（含调试信息）
├── include/         # 自定义头文件
└── source/          # 源文件 (.c / .cpp)
```

> **Tip**：初始化完成后，可以像单文件一样直接使用 **运行/调试按钮** 或 `F5` 进行多文件调试。

------

### 模式二：现代 C++ 模式（工程化）

#### Step 1. 安装插件

- `C/C++`
- `CMake Tools`

#### Step 2. 安装工具链

**Windows**

- `gcc`, `g++`, `gdb`, `cmake`, `ninja`（推荐通过 [MSYS2](https://mirrors.tuna.tsinghua.edu.cn/msys2/distrib/msys2-x86_64-latest.exe) 安装）
- `Microsoft Visual C++ Build Tools`（下载地址：[Visual Studio Build Tools](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/)） 或安装完整的 **Visual Studio C++ 桌面开发**
- `vcpkg`（[GitHub 项目地址](https://github.com/microsoft/vcpkg)）

**Linux**

- `gcc`, `g++`, `gdb`, `cmake`, `ninja`（通过包管理器安装）
- `vcpkg`（同上）

#### Step 3. 配置 CMakePresets.json 和 launch.json

安装程序会尝试自动查找编译器路径，如果没有找到，则请根据提示依次输入 `gcc` 编译器路径和 `cl` 路径。具体配置示例请参考：[modern cpp 配置示例](./Modern Cpp 配置示例.md)。

#### Step 4. 初始化项目

```bash
new-cpp-project
```

> **注意事项**：
>
> 1. 如果使用 MSVC 构建工具，则需要通过开始菜单中的 `Developer PowerShell for VS 2022`、`Developer Command Prompt for VS 2022` 或 ` x64_x86 Cross Tools Command Prompt for VS 2022` 等启动项来启动控制台，然后再在控制台中通过命令`code <项目目录>`来打开项目，否则 vscode 可能无法正确识别 MSVC 开发所需的环境变量。
>
> 2. 如果 git 初次提交没有成功，那很可能是 git 本身没有配置好，请检查 `git config list` 输出结果中是否有 `user.name` 和 `user.email`，如果没有请按下面的命令设置：
>
>    ```shell
>    $ git config --global user.name "John Doe"
>    $ git config --global user.email johndoe@example.com
>    ```

初始化后，项目结构如下：

```
.
├── .clang-format             # Clang 格式化配置
├── .gitignore                # Git 忽略文件
├── .vscode/                  # VSCode 配置
├── CMakeLists.txt            # 顶层 CMake 配置
├── CMakePresets.json         # CMake 预设
├── README.md                 # 项目说明
├── external/                 # 第三方库目录
├── src/                      # 源文件目录
├── vcpkg-configuration.json  # vcpkg 配置
└── vcpkg.json                # vcpkg 包清单
```

当第一次执行构建项目后会产生两个新的目录：

- `build`：CMake 构建信息缓存目录以及 vcpkg 包缓存目录
- `target`：这里面包含两个子目录`lib`和`bin`，前者是存放生成的静态库，后者存放可执行文件及其所需的库文件。

#### Step 5. 引入第三方库

```bash
vcpkg add port <包名>
```

------

## ⚠️ Windows PowerShell 权限问题

首次运行 PowerShell 脚本可能提示**执行策略限制**，解决方法：
 以管理员身份运行 PowerShell，执行：

```powershell
Set-ExecutionPolicy RemoteSigned
```

输入 `Y` 确认。详细参考：[Set-ExecutionPolicy 官方文档](https://learn.microsoft.com/zh-cn/powershell/module/microsoft.powershell.security/set-executionpolicy)。

