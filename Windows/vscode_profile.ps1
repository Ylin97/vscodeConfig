#region project initialize
function Init-project
{
    param (
        $ProjectType = 'Unknown'
    )
    $TemplatePathRoot = $HOME + "\.vscode\projectTemplate"
    $ResourcePath = switch ( $ProjectType ) 
    {
        'c' {
            $TemplatePathRoot + "\c\*"
        }
        'cpp' {
            $TemplatePathRoot + "\cpp\*"
        }
        default {
            "Unknown"
        }
    }
    Copy-Item -Path $ResourcePath -Destination "." -Recurse 
    if ( $? ) {
        if ( Get-Command "git" -errorAction SilentlyContinue ) {
            git init
            git add .
            git commit -m "Initialized a project."
        } else {
            Write-Host "WARN: 'git' command not found."
        }
        # open main file in vscode
        $MainFile = ".\source\main." + $ProjectType
        Code $MainFile
    }
}

function Reset-Vscode-Config
{
    param (
        $ProjectType = "Unknown"
    )
    
    $CurrentConfigPath = ".\.vscode"
    $TemplatePathRoot = $HOME + "\.vscode\projectTemplate"
    
    # remove the old configuration files
    $TRUE_FALSE = ( Test-Path $CurrentConfigPath )
    if ( $TRUE_FALSE -eq "True" ) {
        remove-Item -Recurse -Force $CurrentConfigPath
    }
    
    $ResourcePath = switch ( $ProjectType ) 
    {
        'c' {
            $TemplatePathRoot + "\c\.vscode"
        }
        'cpp' {
            $TemplatePathRoot + "\cpp\.vscode"
        }
        default {
            "Unknown"
        }
    }
    # reset configuration
    if ( $ResourcePath -ne 'Unknown') {
        Copy-Item -Path $ResourcePath -Destination "." -Recurse
        if ( $? ) {
            $msg = "Reset workspace's configuration for a " + $ProjectType +  " project seccussfully!"
            Write-Host $msg
        } else {
            Write-Host "Error: can't reset workspace configuration, please try again!"
        }
    }
}

function Init-c
{
    Init-project 'c'
}

function Init-cpp
{
    Init-project 'cpp'
}

function Reset-c
{
    Reset-Vscode-Config 'c'
}

function Reset-cpp
{
    Reset-Vscode-Config 'cpp'
}
#endregion