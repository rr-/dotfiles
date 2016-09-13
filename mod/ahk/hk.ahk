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

;detect im
global IMClass
global IMPath
IMClass := "Buddy List"
IMPath := "C:\Program Files (x86)\pidgin\pidgin.exe"
If !FileExist(IMPath) {
    ;wtw
    IMClass := "ahk_class {B993D471-D465-43f2-BBA5-DEEA18A1789E}"
    IMPath := "C:\Program Files\WTW\WTW.exe"
    If !FileExist(IMPath) {
        IMPath := "C:\Program Files\K2T\WTW\WTW.exe"
    }
}

;disable windows+l
RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Policies\System, DisableLockWorkstation, 1

;detect screen resolution
global MonitorWorkAreaLeft
global MonitorWorkAreaRight
global MonitorWorkAreaTop
global MonitorWorkAreaBottom
SysGet, MonitorPrimary, MonitorPrimary
SysGet, MonitorWorkArea, MonitorWorkArea, %MonitorPrimary%
;...and set terminal position basing on this
TermX := MonitorWorkAreaRight - 920
TermY := 45
RemoteTermX := 45
RemoteTermY := 45

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
        Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "110`,35" --position "%TermX%`,%TermY%" --class "mintty_thetty" --exec /bin/zsh -i -l, %CygPath%
        return
    }
    +^![::
    {
        Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "110`,35" --position "%TermX%`,%TermY%" --class "mintty_thetty" --exec /bin/zsh -i -l, %CygPath%
        return
    }
    ^![::
    {
        if (!WinExist("ahk_class mintty_thetty"))
        {
            Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "110`,35" --position "%TermX%`,%TermY%" --class "mintty_thetty" --exec /bin/zsh -i -l, %CygPath%
            WinWait ahk_class mintty_thetty
        }
        else
        {
            WinShow
            WinActivate
        }
        return
    }

    ;ssh to burza - activate/run
    +^!]::
    {
        Run, %CygPath%\bin\mintty.exe --title "Remote terminal" --size "190`,65" --position "%RemoteTermX%`,%RemoteTermY%" --class mintty_ssh --exec /bin/ssh burza, %CygPath%/bin
        return
    }
    ^!]::
    {
        if (!WinExist("ahk_class mintty_ssh"))
        {
            Run, %CygPath%\bin\mintty.exe --title "Remote terminal" --size "190`,65" --position "%RemoteTermX%`,%RemoteTermY%" --class mintty_ssh --exec /bin/ssh burza, %CygPath%/bin
            WinWait ahk_class mintty_ssh
        }
        else
        {
            WinShow
            WinActivate
        }
        return
    }

    ;text editor - activate/run + fix screen position
    +^!N::
    {
        IfWinExist, ahk_class Vim
        {
            WinShow
            WinActivate
        }
        else
        {
            Run, %CygPath%\bin\mintty.exe --size "180`,60" --position "100`,100" --class "Vim" --exec /bin/zsh -l -i -c /bin/vim, %CygPath%/bin
            WinWait, ahk_class Vim
        }
        return
    }

    ;vifm - activate/run
    #E::
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
    +#E::
    {
        Run, %CygPath%\bin\mintty.exe --window max --class "Vifm" --exec /bin/zsh -l -i -c vifm, %CygPath%/bin
        return
    }

;im
#If FileExist(IMPath)
    ;im - activate/run
    +^!M::
        if (!WinExist(IMClass))
        {
            Run, %IMPath% -x
        }
        else
        {
            WinShow
            WinActivate
        }
        return

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
#Q::
    ActiveHwnd := WinExist("A")
    WinClose
    return

;fullscreen
#F::
    WinGet MX, MinMax, A
    if MX
        WinRestore A
    else
        WinMaximize A
    return

;restore active window
#S::
    ActiveHwnd := WinExist("A")
    PostMessage 0x112, 0xf120 ;WM_SYSCOMMAND, SC_RESTORE
    return

;minimize active window
#W::
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
#A::WinSet, AlwaysOnTop, Toggle, A

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
#Z::AddTransparency(-12)
+#Z::AddTransparency(12)

;directional focus
DirectionalFocus(direction)
{
    DetectHiddenWindows, Off
    ActiveHwnd := WinExist("A")
    WinGetPos bx, by, _, _, ahk_id %ActiveHwnd%
    WinGet windows, List
    Loop %windows%
    {
        id := windows%A_Index%
        WinGetPos wx, wy, _, _, ahk_id %id%
        if (direction == "left")
            condition := wx < bx
        else if (direction == "right")
            condition := wx > bx
        else if (direction == "up")
            condition := wy < by
        else if (direction == "down")
            condition := wy > by
        else
        {
            MsgBox % "Bad direction"
            return
        }
        if (condition)
        {
            WinGetTitle, wtitle, ahk_id %id%
            if (wtitle != "")
            {
                WinActivate, ahk_id %id%
                break
            }
        }
    }
    DetectHiddenWindows, On
    return
}
#H::DirectionalFocus("left")
#J::DirectionalFocus("down")
#K::DirectionalFocus("up")
#L::DirectionalFocus("right")
+#H::SendInput, {LWin down}{LShift down}{Left}{LShift up}{LWin up}
+#L::SendInput, {LWin down}{LShift down}{Right}{LShift up}{LWin up}

;music
#X::Send {Volume_Up}
+#X::Volume_Down
#C::Send {Media_Next}
+#C::Media_Prev
#V::Send {Media_Play_Pause}

;screenshots
+#I::Run, %CygPath%\bin\zsh.exe -i -l -c 'shot -w -i --output=Z:/', , Hide
#I::Run, %CygPath%\bin\zsh.exe -i -l -c 'shot -i --output=Z:/', , Hide

;reload autohotkey
!F12::Reload

;toggle arrows
~ScrollLock::
    Sleep, 300
    if GetKeyState("ScrollLock", "T")
       Run, %CygPath%\bin\zsh.exe -i -l -c 'arrows 1', , Hide
    else
        Run, %CygPath%\bin\zsh.exe -i -l -c 'arrows 0', , Hide
