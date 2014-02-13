;Control key Ctrl- ^
;Alt key Alt- !
;Shift key Shift- +
;Windows key Win- #

#Persistent
;#NoTrayIcon
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

global WTWPath
WTWPath = C:\Program Files\WTW\WTW.exe
IfNotExist %WTWPath%
	WTWPath = C:\Program Files\K2T\WTW\WTW.exe

global MonitorWorkAreaLeft
global MonitorWorkAreaRight
global MonitorWorkAreaTop
global MonitorWorkAreaBottom
SysGet, MonitorPrimary, MonitorPrimary
SysGet, MonitorWorkArea, MonitorWorkArea, %MonitorPrimary%

GroupAdd, adobe, ahk_class OWL.DocumentWindow
GroupAdd, adobe, ahk_class illustrator
GroupAdd, adobe, ahk_class PSViewC
GroupAdd, adobe, ahk_class Photoshop
GroupAdd, adobe, Photoshop

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

;calling screen script
MakeScreen(arguments)
{
	baseFileName := "Z:\" . RandomFileName() . ".png"
	RunWait, % "Z:\software\utilities\scrsh.exe --path " . baseFileName . " " . arguments, "Z:\", Hide
	SoundPlay, Z:\clutter\sounds\ping.wav
	return baseFileName
}



#If FileExist(CygPath)
	;cygwin - activate/run
	+^![::
	{
		X := MonitorWorkAreaRight - 920
		Y := 45
		Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "120`,40" --position "%X%`,%Y%" --class "mintty_thetty" --exec /bin/bash -l, %CygPath%
		return
	}
	^![::
	{
		if (!WinExist("ahk_class mintty_thetty"))
		{
			X := MonitorWorkAreaRight - 920
			Y := 45
			Run, %CygPath%\bin\mintty.exe --title "Terminal" --size "120`,40" --position "%X%`,%Y%" --class "mintty_thetty" --exec /bin/bash -l -c 'while /bin/true`; do /bin/bash`; cygstart "%A_AhkPath%" "Z:\src\scripts\hide.ahk"`; clear; done', %CygPath%
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
		X := 45
		Y := 45
		Run, %CygPath%\bin\mintty.exe --title "Remote terminal" --size "200`,70" --position "%X%`,%Y%" --class mintty_ssh --exec /bin/ssh -p 65000 rr-@sakuya.pl -t /bin/bash -i, %CygPath%/bin
		return
	}
	^!]::
	{
		X := 45
		Y := 45
		if (!WinExist("ahk_class mintty_ssh"))
		{
			Run, %CygPath%\bin\mintty.exe --title "Remote terminal" --size "200`,70" --position "%X%`,%Y%" --class mintty_ssh --exec /bin/ssh -p 65000 rr-@sakuya.pl, %CygPath%/bin
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
			Run, %CygPath%\bin\mintty.exe --size "240`,90" --position "100`,45" --class "Vim" --exec /bin/bash -l -c /bin/vim, %CygPath%/bin
			WinWait, ahk_class Vim
		}
		WinMove, , , 100, 100, 1600, 900
		return
	}
	+PrintScreen::MakeScreen("-g")
	!PrintScreen::MakeScreen("-r active-window --shift -8,-8,+16,+16 --force-gui")
	!#PrintScreen::MakeScreen("-r active-monitor")
	#PrintScreen::MakeScreen("-r all-monitors")


;explorer - activate/run
#E::FRun("ahk_class CabinetWClass", "Z:\", "Z:\")

;foobar - activate/run
#If FileExist("C:\program files (x86)\foobar2000\foobar2000.exe")
	Launch_Media::FRun("ahk_class {97E27FAA-C0B3-4b8e-A693-ED7881E99FC1}", "C:\program files (x86)\foobar2000\foobar2000.exe", "C:\Program Files (x86)\foobar2000")

;wtw
#If FileExist(WTWPath)
	;wtw - activate/run
	+^!M::
		if (!WinExist("^WTW"))
		{
			Run, %WTWPath% -x
		}
		else
		{
			WinShow
			WinActivate
		}
		return

;cdisplayex - activate/run
#If FileExist("C:\Program Files (x86)\CDisplayEx\cdisplayex.exe")
	^!/::FRun("CDisplayEx", "C:\Program Files (x86)\CDisplayEx\cdisplayex.exe", "Z:\")

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
	^V::SendInput {Raw}%clipboard% ;paste on ctrl+v
	^!PgUp::SendInput ! {Up}{Up}{Up}{Right}{Up}{Up}{Enter}{PgUp}{Enter} ;scroll on ctrl+page up
	^!PgDn::SendInput ! {Up}{Up}{Up}{Right}{Up}{Up}{Enter}{PgDn}{Enter} ;scroll on ctrl+page down
#IfWinActive

;acdsee functionalities
#IfWinActive ahk_class ACDBrowser
	WheelDown::Send, ^{Down}^{Space}
	WheelUp::Send, ^{Up}^{Space}
	^!X::
		SendInput {Left 10}{Shift down}{Right 10}{Shift up}
		return
#IfWinActive
#IfWinActive ACDSee
	WheelDown::
		if (A_TickCount - OldTicks >= 80)
		{
			Send, {WheelDown}
			OldTicks := A_TickCount
		}
		return
	]:: ;send to document folder
	RButton & ~LButton::
		FormatTime, Folder,, 'Z:\'
		Send {LAlt down}c
		Send {LAlt up}
		SendInput %Folder%
		Send {Return}
		return
	[:: ;send to upload folder
	~LButton & RButton::
		Send {LAlt down}c
		Send {LAlt up}
		SendInput Z:\hub\yume.pl
		Send {Return}
		Sleep 100
		return
	XButton1::
		WinGet, Transparency, Transparent, A
		if ! Transparency
			WinSet, Transparent, 255, A
		else if Transparency = 255
			WinSet, Transparent, 0, A
		return
	XButton2:: ;start slideshow
		Send {Pause}
		return
#IfWinActive

;other functionalities

;autohotkey - reload this script
!F11::
{
	Process, Close, Rainmeter.exe
	Run, C:\Program Files \Rainmeter\Rainmeter.exe
	return
}
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
	else
	{
		ActiveHwnd := WinExist("A")
		PostMessage 0x112, 0xF020 ;WM_SYSCOMMAND, SC_MINIMIZE
	}
	return

;always on top
!A::WinSet, AlwaysOnTop, Toggle, A

;transparency
#1::WinSet, Transparent, 0, A
#2::WinSet, Transparent, 64, A
#3::WinSet, Transparent, 255, A
#WheelUp::
	WinGet, Transparency, Transparent, A
	if ! Transparency
		Transparency = 255
	Transparency := Transparency + 16
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
#WheelDown::
	WinGet, Transparency, Transparent, A
	if ! Transparency
		Transparency = 255
	Transparency := Transparency - 16
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
