;Control key Ctrl- ^
;Alt key Alt- !
;Shift key Shift- +
;Windows key Win- #

#Persistent
#SingleInstance Force

A_DetectHiddenWindows := true
A_DetectHiddenText := true
A_TitleMatchMode := "RegEx" ;match titles and classes using regular expressions
A_TitleMatchModeSpeed := "Slow" ;match titles and classes using regular expressions
A_CoordModeMouse := "Screen"
A_CoordModeToolTip := "Screen"


;detect cygwin
CygPath := "C:\Program Files (x86)\cygwin"
if !FileExist(CygPath) {
    CygPath := "C:\Cygwin"
}
If !FileExist(CygPath) {
    CygPath := "C:\Cygwin64"
}


;detect browser
BrowserPath := "C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
if !FileExist(BrowserPath) {
    BrowserPath := "C:\Program Files\Mozilla Firefox\firefox.exe"
}
if !FileExist(BrowserPath) {
    BrowserPath := "C:\Users\rr-\AppData\Local\Google\Chrome\Application\chrome.exe"
}


;activate/run a program
FRun(window, path, folder)
{
    if !window || !WinExist(window) {
        Run(path, folder)
    } else {
        WinShow
        WinActivate
    }
    return
}


;fix URLs copied by some browsers so they're clickable in popular programs
ClipboardChanged(type)
{
    if (SubStr(clipboard, 1, 7) == "http://") || SubStr(clipboard, 1, 8) == "https://" {
        clipboard := StrReplace(clipboard, "[", "%5b", All)
        clipboard := StrReplace(clipboard, "\", "%5c", All)
        clipboard := StrReplace(clipboard, "]", "%5d", All)
    }
    return
}
OnClipboardChange("ClipboardChanged")


;enforce same keyboard layout across all programs
global Locale1 := 0x4150415
global Locale2 := 0x4110411
global CurrentLocale := Locale1

GetActiveLocale()
{
    win_id := WinGetID("A")
    thread_id := DllCall("GetWindowThreadProcessId", "Int", win_id, "Int", "0")
    return DllCall("GetKeyboardLayout", "Int", thread_id)
}

ApplyLocale(locale)
{
    global CurrentLocale := locale
    SendMessage(0x50, 0, locale, "", "A")
}

CycleLocale()
{
    if CurrentLocale == Locale1 {
        ApplyLocale(locale2)
    } else if CurrentLocale == Locale2 {
        ApplyLocale(Locale1)
    }
}

ShellMessage(wparam, lparam)
{
    title := WinGetTitle(lparam)
    if wParam == 4 { ;HSHELL_WINDOWACTIVATED
        ApplyLocale(CurrentLocale)
    }
}

gui := GuiCreate("", "")
gui.Opt("+LastFound")
hwnd := WinExist()
DllCall("RegisterShellHookWindow", uint, hwnd)
msgnum := DllCall("RegisterWindowMessage", str, "SHELLHOOK")
OnMessage(msgnum, "ShellMessage")


return


#If FileExist(CygPath)
    ;cygwin - activate/run
    #Enter::
    {
        Run(CygPath . "\\bin\\mintty.exe --title Terminal --class mintty_thetty --exec /bin/zsh -i -l", CygPath)
        return
    }
    +^![::
    {
        Run(CygPath . "\\bin\\mintty.exe --title Terminal --class mintty_thetty --exec /bin/zsh -i -l", CygPath)
        return
    }
    ^![::
    {
        if !WinExist("ahk_class mintty_thetty") {
            Run(CygPath . "\\bin\\mintty.exe --title Terminal --class mintty_thetty --exec /bin/zsh -i -l", CygPath)
            WinWait("ahk_class mintty_thetty")
        } else {
            WinShow
            WinActivate
        }
        return
    }

    ;ssh to cyclone - activate/run
    +^!]::
    {
        Run(CygPath . "\\bin\\mintty.exe --title 'Remote terminal' --class mintty_ssh --exec /bin/ssh cyclone", CygPath . "/bin")
        return
    }
    ^!]::
    {
        if !WinExist("ahk_class mintty_ssh") {
            Run(CygPath . "\\bin\\mintty.exe --title 'Remote terminal' --class mintty_ssh --exec /bin/ssh cyclone", CygPath . "/bin")
            WinWait("ahk_class mintty_ssh")
        } else {
            WinShow
            WinActivate
        }
        return
    }

    ;vifm - activate/run
    #e::
    {
        If WinExist("ahk_class Vifm") {
            WinShow
            WinActivate
        } else {
            Run(CygPath . "\\bin\\mintty.exe --window max --class Vifm --exec /bin/zsh -l -i -c vifm", CygPath . "/bin")
            WinWait("ahk_class Vifm")
        }
        return
    }

    ;vifm - just run
    +#e::
    {
        Run(CygPath . "\\bin\\mintty.exe --window max --class Vifm --exec /bin/zsh -l -i -c vifm", CygPath . "/bin")
        return
    }
#If

;browser
#If FileExist(BrowserPath)
    ;web browser - activate/run
    ^!;::
        if WinExist("Mozilla Firefox") {
            WinShow
            WinActivate
            ;Send("!d")
        } else if WinExist("Vimperator") {
            WinShow
            WinActivate
            ;Send("!d")
        } else if WinExist("ahk_class Chrome_WidgetWin_1") {
            WinActivate
            ControlFocus("Chrome_OmniboxView1")
            ;SendInput("{Home}+{End}")
        } else {
            if FileExist(BrowserPath) {
                Run(BrowserPath)
            }
        }
        return
#If

;adobe products
#IfWinActive ahk_group adobe
    ~LAlt::return
    LAlt UP::Send("{Escape}")
#IfWinActive
#IfWinActive ahk_class illustrator
+wheelup::
    Send("{Ctrl Down}{=}{Ctrl Up}")
    return
+wheeldown::
    Send("{Ctrl Down}-{Ctrl Up}")
    return
#IfWinActive

;close active window
#q::
{
    active_hwnd := WinExist("A")
    WinClose
    return
}

;fullscreen
#f::
{
    if WinGetMinMax("A") {
        WinRestore("A")
    } else {
        WinMaximize("A")
    }
    return
}

;restore active window
#s::
{
    active_hwnd := WinExist("A")
    PostMessage(0x112, 0xf120) ;WM_SYSCOMMAND, SC_RESTORE
    return
}

;minimize active window
#w::
{
    if WinActive("WTW$") {
        WinHide
    } else if WinActive("Buddy List") {
        WinHide
    } else {
        active_hwnd := WinExist("A")
        PostMessage(0x112, 0xF020) ;WM_SYSCOMMAND, SC_MINIMIZE
    }
    return
}

;set active window as always on top
#a::WinSetAlwaysOnTop("Toggle", "A")

;transparency
AddTransparency(delta)
{
    transparency := WinGetTransparent("A")
    if !transparency {
        transparency := 255
    }
    transparency := transparency + delta
    if transparency <= 10 {
        WinSetTransparent(10, "A")
    } else if Transparency >= 255 {
        WinSetTransparent(255, "A")
        WinSetTransparent("OFF", "A")
    } else {
        WinSetTransparent(transparency, "A")
    }
}
#WheelUp::AddTransparency(12)
#WheelDown::AddTransparency(-12)
#z::AddTransparency(-12)
+#z::AddTransparency(12)

;music
#x::Volume_Up
+#x::Volume_Down
#c::Media_Next
+#c::Media_Prev
#v::Media_Play_Pause

;screenshots
+#i::Run(CygPath . "\\bin\\zsh.exe -i -l -c 'shot -w -i --output=Z:/'", , Hide)
#i::Run(CygPath . "\\bin\\zsh.exe -i -l -c 'shot -i --output=Z:/'", , Hide)

;reload autohotkey
!F12::Reload

;linux-compatible useful keys
RAlt & -::Send(GetKeyState("Shift") ? "{U+2014}" : "{U+2013}")
RAlt & k::Send("{U+2026}")

;hepburn macrons
RAlt & =::
{
    key := Input("L1", "{delete}{esc}{home}{end}") ; pressing any of these will terminate the input
    if key == "A" {
        Send("{U+0100}")
    } else if key == "I" {
        Send("{U+012A}")
    } else if key == "U" {
        Send("{U+016A}")
    } else if key == "E" {
        Send("{U+0112}")
    } else if key == "O" {
        Send("{U+014C}")
    } else if key == "a" {
        Send("{U+0101}")
    } else if key == "i" {
        Send("{U+012B}")
    } else if key == "u" {
        Send("{U+016B}")
    } else if key == "e" {
        Send("{U+0113}")
    } else if key == "o" {
        Send("{U+014D}")
    }
     return
}


#n::
{
    CycleLocale()
}
