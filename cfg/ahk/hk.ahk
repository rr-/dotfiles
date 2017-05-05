;Control key Ctrl- ^
;Alt key Alt- !
;Shift key Shift- +
;Windows key Win- #

#Persistent
#SingleInstance Force
DetectHiddenWindows, On
DetectHiddenText, On
SetTitleMatchMode, RegEx ;match titles and classes using regular expressions
SetTitleMatchMode Slow ;match titles and classes using regular expressions
CoordMode, Mouse, Screen
CoordMode, ToolTip, Screen

;detect cygwin
global CygPath
CygPath = C:\Program Files (x86)\cygwin
IfNotExist %CygPath%
    CygPath = C:\Cygwin
IfNotExist %CygPath%
    CygPath = C:\Cygwin64

;detect browser
global BrowserPath
BrowserPath = C:\Program Files (x86)\Mozilla Firefox\firefox.exe
IfNotExist %BrowserPath%
    BrowserPath = "C:\Users\rr-\AppData\Local\Google\Chrome\Application\chrome.exe"

;disable windows+l
RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Policies\System, DisableLockWorkstation, 1

;activate/run a program
FRun(window, path, folder)
{
    if (!window or !WinExist(window))
    {
        Run, %path%, %folder%
    }
    else
    {
        WinShow
        WinActivate
    }
    return
}

return

;replace stuff in clipboard when it changes
OnClipboardChange:
{
    if (A_EventInfo == 1) and (SubStr(clipboard, 1, 7) == "http://")
    {
        StringReplace, clipboard, clipboard, [, `%5b, All
        StringReplace, clipboard, clipboard, \, `%5c, All
        StringReplace, clipboard, clipboard, ], `%5d, All
    }
    return
}

#If FileExist(CygPath)
    ;cygwin - activate/run
    #Enter::
    {
        Run, %CygPath%\bin\mintty.exe --title "Terminal" --class "mintty_thetty" --exec /bin/zsh -i -l, %CygPath%
        return
    }
    +^![::
    {
        Run, %CygPath%\bin\mintty.exe --title "Terminal" --class "mintty_thetty" --exec /bin/zsh -i -l, %CygPath%
        return
    }
    ^![::
    {
        if (!WinExist("ahk_class mintty_thetty"))
        {
            Run, %CygPath%\bin\mintty.exe --title "Terminal" --class "mintty_thetty" --exec /bin/zsh -i -l, %CygPath%
            WinWait ahk_class mintty_thetty
        }
        else
        {
            WinShow
            WinActivate
        }
        return
    }

    ;ssh to cyclone - activate/run
    +^!]::
    {
        Run, %CygPath%\bin\mintty.exe --title "Remote terminal" --class mintty_ssh --exec /bin/ssh cyclone, %CygPath%/bin
        return
    }
    ^!]::
    {
        if (!WinExist("ahk_class mintty_ssh"))
        {
            Run, %CygPath%\bin\mintty.exe --title "Remote terminal" --class mintty_ssh --exec /bin/ssh cyclone, %CygPath%/bin
            WinWait ahk_class mintty_ssh
        }
        else
        {
            WinShow
            WinActivate
        }
        return
    }

    ;text editor - activate/run
    +^!N::
    {
        IfWinExist, ahk_class Vim
        {
            WinShow
            WinActivate
        }
        else
        {
            Run, %CygPath%\bin\mintty.exe --class "Vim" --exec /bin/zsh -l -i -c /bin/vim, %CygPath%/bin
            WinWait, ahk_class Vim
        }
        return
    }

    ;vifm - activate/run
    #e::
    {
        IfWinExist, ahk_class Vifm
        {
            WinShow
            WinActivate
        }
        else
        {
            Run, %CygPath%\bin\mintty.exe --window max --class "Vifm" --exec /bin/zsh -l -i -c vifm, %CygPath%/bin
            WinWait, ahk_class Vifm
        }
        return
    }

    ;vifm - just run
    +#e::
    {
        Run, %CygPath%\bin\mintty.exe --window max --class "Vifm" --exec /bin/zsh -l -i -c vifm, %CygPath%/bin
        return
    }

;browser
#If FileExist(BrowserPath)
    ;web browser - activate/run
    ^!;::
        if WinExist("Mozilla Firefox")
        {
            WinShow
            WinActivate
            Send, !d
        }
        else if WinExist("Vimperator")
        {
            WinShow
            WinActivate
            Send, !d
        }
        else if WinExist("ahk_class Chrome_WidgetWin_1")
        {
            WinActivate
            ControlFocus, Chrome_OmniboxView1
            SendInput, {Home}+{End}
        }
        else
        {
            IfExist %BrowserPath%
                Run, %BrowserPath%
        }
        return

;adobe products
#IfWinActive ahk_group adobe
    ~LAlt::return
    LAlt UP::Send {Escape}
#IfWinActive
#IfWinActive ahk_class illustrator
+wheelup::
    send {Ctrl Down}{=}{Ctrl Up}
    return
+wheeldown::
    send {Ctrl Down}-{Ctrl Up}
    return
#IfWinActive

;close active window
#q::
    ActiveHwnd := WinExist("A")
    WinClose
    return

;fullscreen
#f::
    WinGet MX, MinMax, A
    if MX
        WinRestore A
    else
        WinMaximize A
    return

;restore active window
#s::
    ActiveHwnd := WinExist("A")
    PostMessage 0x112, 0xf120 ;WM_SYSCOMMAND, SC_RESTORE
    return

;minimize active window
#w::
    if WinActive("WTW$")
    {
        WinHide
    }
    else if WinActive("Buddy List")
    {
        WinHide
    }
    else
    {
        ActiveHwnd := WinExist("A")
        PostMessage 0x112, 0xF020 ;WM_SYSCOMMAND, SC_MINIMIZE
    }
    return

;set active window as always on top
#a::WinSet, AlwaysOnTop, Toggle, A

;transparency
AddTransparency(delta)
{
    WinGet, Transparency, Transparent, A
    if ! Transparency
        Transparency = 255
    Transparency := Transparency + delta
    if Transparency <= 10
    {
        WinSet, Transparent, 10, A
    }
    else if Transparency >= 255
    {
        WinSet, Transparent, 255, A
        WinSet, Transparent, OFF, A
    }
    else
    {
        WinSet, Transparent, %Transparency%, A
    }
    return
}
#WheelUp::AddTransparency(12)
#WheelDown::AddTransparency(-12)
#z::AddTransparency(-12)
+#z::AddTransparency(12)

;music
#x::Send {Volume_Up}
+#x::Volume_Down
#c::Send {Media_Next}
+#c::Media_Prev
#v::Send {Media_Play_Pause}

;screenshots
+#i::Run, %CygPath%\bin\zsh.exe -i -l -c 'shot -w -i --output=Z:/', , Hide
#i::Run, %CygPath%\bin\zsh.exe -i -l -c 'shot -i --output=Z:/', , Hide

;reload autohotkey
!F12::Reload

#j::
{
    SetFormat, Integer, H
    Locale1=0x4150415
    Locale2=0x4110411
    WinGet, WinID,, A
    ThreadID:=DllCall("GetWindowThreadProcessId", "Int", WinID, "Int", "0")
    InputLocaleID:=DllCall("GetKeyboardLayout", "Int", ThreadID)
    if(InputLocaleID=Locale1)
        SendMessage, 0x50,, % Locale2,, A
    else if(InputLocaleID=Locale2)
        SendMessage, 0x50,, % Locale1,, A
    return
}
