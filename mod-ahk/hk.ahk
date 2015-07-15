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
OldTicks = 0

;check for cygwin path
global CygPath
CygPath = C:\Program Files (x86)\cygwin
IfNotExist %CygPath%
	CygPath = C:\Cygwin

global BrowserPath
BrowserPath = C:\Program Files (x86)\Mozilla Firefox\firefox.exe
IfNotExist %BrowserPath%
	BrowserPath = "C:\Users\rr-\AppData\Local\Google\Chrome\Application\chrome.exe"

global IMClass
global IMPath

;pidgin
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

global MonitorWorkAreaLeft
global MonitorWorkAreaRight
global MonitorWorkAreaTop
global MonitorWorkAreaBottom
SysGet, MonitorPrimary, MonitorPrimary
SysGet, MonitorWorkArea, MonitorWorkArea, %MonitorPrimary%

;disable windows+l
RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Policies\System, DisableLockWorkstation, 1

TermX := MonitorWorkAreaRight - 920
TermY := 45
RemoteTermX := 45
RemoteTermY := 45

;GroupAdd, adobe, ahk_class OWL.DocumentWindow
;GroupAdd, adobe, ahk_class illustrator
;GroupAdd, adobe, ahk_class PSViewC
;GroupAdd, adobe, ahk_class Photoshop
;GroupAdd, adobe, Photoshop

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

;declare some fun functions...

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

;create random file name
RandomFileName()
{
	FormatTime, fileName,, yyyyMMdd_HHmmss_
	characters := "abcdefghijklmnopqrstuvwxyz"
	Loop 3
	{
		Random, rand, 1, strlen(characters)
		fileName := fileName . substr(characters, rand, 1)
	}
	return fileName
}

;focus window in given direction
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

#If FileExist(CygPath)
	;cygwin - activate/run
	#Enter::
	{
		Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "110`,35" --position "%TermX%`,%TermY%" --class "mintty_thetty" --exec /bin/zsh -l, %CygPath%
		return
	}
	+^![::
	{
		Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "110`,35" --position "%TermX%`,%TermY%" --class "mintty_thetty" --exec /bin/zsh -l, %CygPath%
		return
	}
	^![::
	{
		if (!WinExist("ahk_class mintty_thetty"))
		{
			Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "110`,35" --position "%TermX%`,%TermY%" --class "mintty_thetty" --exec /bin/zsh -c 'while /bin/true`; do /bin/zsh -l`; cygstart "%A_AhkPath%" "%A_ScriptDir%\hide.ahk"`; clear; done', %CygPath%
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


;explorer - activate/run
#E::FRun("ahk_class CabinetWClass", "Z:\", "Z:\")

;foobar - media shortcuts
#X::Send {Volume_Up}
+#X::Volume_Down
#C::Send {Media_Next}
+#C::Media_Prev
#V::Send {Media_Play_Pause}
+#V::FRun("ahk_class {97E27FAA-C0B3-4b8e-A693-ED7881E99FC1}", "C:\program files (x86)\foobar2000\foobar2000.exe", "C:\Program Files (x86)\foobar2000")

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

;windows powershell / cmd functionalities
#IfWinActive ahk_class ConsoleWindowClass
	+Insert::SendInput {Raw}%clipboard% ;paste on shift+insert
	+PgUp::SendInput ! {Up}{Up}{Up}{Right}{Up}{Up}{Enter}{PgUp}{Enter} ;scroll on shift+page up
	+PgDn::SendInput ! {Up}{Up}{Up}{Right}{Up}{Up}{Enter}{PgDn}{Enter} ;scroll on shift+page down
#IfWinActive

;other functionalities

;reload autohotkey
!F12::Reload

;maximize active window
!M::
	ActiveHwnd := WinExist("A")
	PostMessage 0x112, 0xf030 ;WM_SYSCOMMAND, SC_MAXIMIZE
	return

;restore active window
!R::
	ActiveHwnd := WinExist("A")
	PostMessage 0x112, 0xf120 ;WM_SYSCOMMAND, SC_RESTORE
	return

;minimize active window
!W::
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

;always on top
!A::WinSet, AlwaysOnTop, Toggle, A

;transparency
#WheelUp::AddTransparency(16)
#WheelDown::AddTransparency(-16)
#Z::AddTransparency(-12)
+#Z::AddTransparency(12)

;explorer
#IfWinActive ahk_class CabinetWClass
	;new folder
	^n::
		SendInput {Up}{Ctrl Down}{Space}{Ctrl Up}{AppsKey}{Up}{Up}{Right}{Enter}
		return
#IfWinActive

;adobe products
#IfWinActive ahk_group adobe
	~LAlt::return
	LAlt UP::Send {Escape}
#IfWinActive

;shortcuts like in i3
;close active window
#Q::
	ActiveHwnd := WinExist("A")
	WinClose
	return
#D::
	SendInput, {LWin down}r{LWin up}
	return
#F::
	WinGet MX, MinMax, A
	if MX
		WinRestore A
	else
		WinMaximize A
	return
#H::DirectionalFocus("left")
#J::DirectionalFocus("down")
#K::DirectionalFocus("up")
#L::DirectionalFocus("right")
+#H::SendInput, {LWin down}{LShift down}{Left}{LShift up}{LWin up}
+#L::SendInput, {LWin down}{LShift down}{Right}{LShift up}{LWin up}
