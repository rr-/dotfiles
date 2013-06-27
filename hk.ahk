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

GroupAdd, adobe, ahk_class OWL.DocumentWindow
GroupAdd, adobe, ahk_class illustrator
GroupAdd, adobe, ahk_class PSViewC
GroupAdd, adobe, ahk_class Photoshop
GroupAdd, adobe, Photoshop
return

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

UploadFiles()
{
	ToolTip, Uploading files..., -1920+50, 50
	RunWait, C:\Program Files (x86)\cygwin\bin\mintty.exe /bin/bash -l -c send_to_pinkyard.py|clip, C:\Program Files (x86)\cygwin
	ToolTip
	return
}

MakeScreen(arguments)
{
	baseFileName := "Z:\hub\pinkyard\queued\" . RandomFileName()
	PNGFileName := "Z:\tmp.png"
	JPGFileName := "Z:\tmp.jpg"
	RunWait, % "C:\program files (x86)\scrsh.exe --path " . PNGFileName . " " . arguments, "Z:\", Hide
	if %ErrorLevel% = 0
	{
		RunWait, % "Z:\src\optipng\support\optipng.exe -o1 " . PNGFileName, "Z:\", Hide
		RunWait, % "C:\Program Files (x86)\cygwin\bin\convert.exe " . PNGFileName . " -quality 80 " . JPGFileName, "Z:\", Hide
		FileGetSize, JPGFileSize, % JPGFileName
		FileGetSize, PNGFileSize, % PNGFileName
		if % PNGFileSize > JPGFileSize
		{
			path1 := JPGFileName
			path2 := baseFileName . ".jpg"
		}
		else
		{
			path1 := PNGFileName
			path2 := baseFileName . ".png"
		}
		FileCopy, % path1, % path2
		FileDelete, % JPGFileName
		FileDelete, % PNGFileName
		SoundPlay, Z:\clutter\sounds\ping.wav
	}
	return path
}

OnClipboardChange:
	if (A_EventInfo == 1) and (SubStr(clipboard, 1, 7) == "http://")
	{
		StringReplace, clipboard, clipboard, `%5b, [, All
		StringReplace, clipboard, clipboard, `%5d, ], All
	}
	return

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


;programs
#E::FRun("ahk_class CabinetWClass", "Z:\", "Z:\") ;explorer
Launch_Media::FRun("ahk_class {97E27FAA-C0B3-4b8e-A693-ED7881E99FC1}", "C:\program files (x86)\foobar2000\foobar2000.exe", "C:\Program Files (x86)\foobar2000") ;foobar

+^!U::UploadFiles() ;upload files
+^M::
	if (WinExist("ahk_class TfrmSend")) {
		WinShow
		WinActivate
	}
	return

+^!M::
	if (!WinExist("^WTW")) {
		;RunWait, taskkill /im miranda32.exe /f
		Run, "C:\Program Files\WTW\WTW.exe" -x, "C:\Program Files\WTW"
	} else {
		WinShow
		WinActivate
	}
	return

+^![::FRun(false, "C:\Program Files (x86)\cygwin\bin\mintty.exe -", "C:\Program Files (x86)\cygwin\bin") ;cygwin
 ^![::
	if (!WinExist("ahk_class mintty_thetty")) {
		Run, "C:\Program Files (x86)\cygwin\bin\mintty.exe" --size "120`,40" --position "1050`,45" --class "mintty_thetty" --exec "/bin/bash" --login -i -c 'while /bin/true; do /bin/bash; cygstart "%A_AhkPath%" "Z:\src\hide.ahk"; clear; done', "C:/program files(x86)/cygwin/bin"
		WinWait ahk_class mintty_thetty
	} else {
		WinShow
		WinActivate
	}
	WinSet, Style, -0x004b0000
	return


; putty @burza - activate/run + fix screen position
+^!]::
	Run, "C:\Program Files (x86)\putty\putty.exe" -load burza, "C:\Program Files (x86)"
	WinWaitActive ahk_class PuTTY
	WinMove, , , 100, 100
	return
 ^!]::
	if (!WinExist("ahk_class PuTTY")) {
		Run, "C:\Program Files (x86)\putty\putty.exe" -load burza, "C:\Program Files (x86)"
		WinWait ahk_class PuTTY
		WinMove, , , 100, 100
	} else {
		WinShow
		WinActivate
	}
	return
 ^!/::FRun("CDisplayEx", "C:\Program Files (x86)\CDisplayEx\cdisplayex.exe", "Z:\") ;cdisplay
 ^!;::
	IfWinExist, Mozilla Firefox
	{
		WinShow
		WinActivate
		Send, !d
	}
	else
	{
		Run, "C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
	}
	return


+^!N:: ;text editor - activate/run + fix screen position
	IfWinExist, ahk_class Vim
	{
		WinShow
		WinActivate
	} else {
		Run, "C:\Program Files (x86)\cygwin\bin\mintty.exe" --size "240`,90" --position "100`,45" --class "Vim" --exec "vim" --cmd 'cd /cygdrive/z', "C:/program files(x86)/cygwin/bin"
		WinWait, ahk_class Vim
	}
	WinMove, , , 100, 100, 1600, 900
	return




;windows powershell / cmd functionalities
#IfWinActive ahk_class ConsoleWindowClass
^V::SendInput {Raw}%clipboard% ;paste on ctrl+v
^!PgUp::Send ! el{PgUp}{Enter} ;scroll on ctrl+page up
^!PgDn::Send ! el{PgDn}{Enter} ;scroll on ctrl+page down
#IfWinActive



;acdsee functionalities
#IfWinActive ahk_class ACDBrowser
	WheelDown::Send, ^{Down}^{Space}
	WheelUp::Send, ^{Up}^{Space}
#IfWinActive
#IfWinActive ACDSee
	WheelDown::
		if (A_TickCount - OldTicks >= 80) {
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
		SendInput Z:\hub\pinkyard\queued
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
!F12::Reload
!M:: ;maximize active window
	ActiveHwnd := WinExist("A")
	PostMessage 0x112, 0xf030 ;WM_SYSCOMMAND, SC_MAXIMIZE
	return
!R:: ;restore active window
	ActiveHwnd := WinExist("A")
	PostMessage 0x112, 0xf120 ;WM_SYSCOMMAND, SC_RESTORE
	return
!W:: ;minimize active window
	if WinActive("WTW$") {
		WinHide
	} else {
		ActiveHwnd := WinExist("A")
		PostMessage 0x112, 0xF020 ;WM_SYSCOMMAND, SC_MINIMIZE
	}
	return
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



 +PrintScreen::MakeScreen("-g")
 !PrintScreen::MakeScreen("-r active-window --shift -8,-8,+16,+16 --force-gui")
!#PrintScreen::MakeScreen("-r active-monitor")
 #PrintScreen::MakeScreen("-r all-monitors")



;explorer
#IfWinActive ahk_class CabinetWClass
	;new folder
	^n::
		Send {AppsKey}wf
		return
#IfWinActive



#IfWinActive ahk_class PuTTY
	;putty ctrl+alt+pageup/pagedown
	^!PgUp::SendInput {Escape}:tabprev{Return}
	^!PgDn::SendInput {Escape}:tabnext{Return}
	;putty pasting
	+Numpad0::
	+NumpadIns::
	+Insert::
		WinGetPos, winX, winY, winW, winH
		tempX := winX+(winW//2)
		tempY := winY+(winH//2)
		MouseClick, Right, %tempX%, %tempY%
		return
#IfWinActive



#IfWinActive ahk_group adobe
	~LAlt::return
	LAlt UP::Send {Escape}
#IfWinActive
