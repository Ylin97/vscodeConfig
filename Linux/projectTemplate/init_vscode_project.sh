## 初始化 vscode 项目
function Init-c {
    local template_path="$HOME/.config/Code/projectTemplate/c"
    # 复制所有模板文件到当前目录
    local cmd="cp -r $template_path/. . >/dev/null 2>&1"
    if eval $cmd; then
        # 检查 git 命令是否存在，如果存在则初始化一个仓库
        if which "git" >/dev/null 2>&1; then
            git init
            git add .
            git commit -m "Initialized a project."
        else
            echo "WARN: 'git' command not found!"
            return 2
        fi
        # 尝试用 vscode 打开 main.c 文件
        if which "code" >/dev/null 2>&1; then
            code source/main.c
        fi
    else
        echo -e "\033[33mError: can't initialize a project here, please check if the path '$template_path' exists.\033[0m"
        return 1
    fi
    return 0
}

function Init-cpp {
    local template_path="$HOME/.config/Code/projectTemplate/cpp"
    # 复制所有模板文件到当前目录
    local cmd="cp -r $template_path/. . >/dev/null 2>&1"
    if eval $cmd; then
        # 检查 git 命令是否存在，如果存在则初始化一个仓库
        if which "git" >/dev/null 2>&1; then
            git init
            git add .
            git commit -m "Initialized a project."
        else
            echo "WARN: 'git' command not found!"
            return 2
        fi
        # 尝试用 vscode 打开 main.cpp 文件
        if which "code" >/dev/null 2>&1; then
            code source/main.cpp
        fi
    else
        echo -e "\033[33mError: can't initialize a project here, please check if the path '$template_path' exists.\033[0m"
        return 1
    fi
    return 0
}

function Reset-c {
    local template_path="$HOME/.config/Code/projectTemplate/c"
    # 复制所有模板文件到当前目录
    local cmd="cp -r $template_path/. . >/dev/null 2>&1"
    if eval $cmd; then
        echo "Reset workspace's configuration for a C project seccussfully!"
    else
        echo "Error: can't reset workspace configuration, please try again!"
}

function Reset-cpp {
    local template_path="$HOME/.config/Code/projectTemplate/cpp"
    # 复制所有模板文件到当前目录
    local cmd="cp -r $template_path/. . >/dev/null 2>&1"
    if eval $cmd; then
        echo "Reset workspace's configuration for a C++ project seccussfully!"
    else
        echo "Error: can't reset workspace configuration, please try again!"
    fi
}
