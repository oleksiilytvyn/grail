# -*- coding: UTF-8 -*-
"""
    Create and compile NSI file for Windows installer
"""
import os
import sys

APPLICATION_NAME = 'Grail'
VERSION = '1.0'
FILE_LICENSE = 'path/to/license.txt'

# Icons
ICON = 'icon.ico'
ICON_UNINSTALL = 'icon-uninstall.ico'

# Installer graphics
IMAGE_HEADER = 'header.bmp'
IMAGE_SIDEBAR = 'sidebar.bmp'

NSI_CONTEXTS = '''
; Define your application name
!define APPNAME "Grail"
!define APPNAMEANDVERSION "Grail 1.0"

; Main Install settings
Name "${APPNAMEANDVERSION}"
InstallDir "$PROGRAMFILES\Grail"
InstallDirRegKey HKLM "Software\${APPNAME}" ""
OutFile "bin\Grail.exe"
RequestExecutionLevel highest  

; Use compression
SetCompressor LZMA

; Modern interface settings
!include "MUI.nsh"

BrandingText "Grail"

!define MUI_ICON "Resources\installer\icon.ico"
!define MUI_UNICON "Resources\installer\icon-uninstall.ico"

!define MUI_WELCOMEFINISHPAGE_BITMAP "Resources\installer\panel.bmp" 
!define MUI_HEADERIMAGE 
!define MUI_HEADERIMAGE_BITMAP "Resources\installer\header.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "Resources\installer\header-uninstall.bmp"
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH

!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\grail.exe"

Function "changecolor"
    ; header background
    GetDlgItem $r0 $HWNDPARENT 1034
    SetCtlColors $r0 "" 0x0096ff

    ; title colors
    GetDlgItem $r1 $HWNDPARENT 1037
    SetCtlColors $r1 0xFFFFFF 0x0096ff

    ; description colors
    GetDlgItem $r2 $HWNDPARENT 1038
    SetCtlColors $r2 0xFFFFFF 0x0096ff
FunctionEnd

!define MUI_PAGE_CUSTOMFUNCTION_PRE "changecolor"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Set languages (first is default language)
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_RESERVEFILE_LANGDLL

Section "Grail" Section1
    ; Set Section properties
    SetOverwrite on

    ; Set Section Files and Shortcuts
    CreateShortCut "$DESKTOP\Grail.lnk" "$INSTDIR\grail.exe"
    CreateDirectory "$SMPROGRAMS\Grail"
    CreateShortCut "$SMPROGRAMS\Grail\Grail.lnk" "$INSTDIR\grail.exe"
    CreateShortCut "$SMPROGRAMS\Grail\Uninstall.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

Section -FinishSection
    WriteRegStr HKLM "Software\${APPNAME}" "" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Modern install component descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${Section1} ""
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;Uninstall section
Section Uninstall
    ;Remove from registry...
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "SOFTWARE\${APPNAME}"

    ; Delete self
    Delete "$INSTDIR\uninstall.exe"

    ; Delete Shortcuts
    Delete "$DESKTOP\Grail.lnk"
    Delete "$SMPROGRAMS\Grail\Grail.lnk"
    Delete "$SMPROGRAMS\Grail\Uninstall.lnk"

    ; Clean up Grail
    Delete "$INSTDIR\grail.exe"

    ; Remove remaining directories
    ;;removedirs
    RMDir "$SMPROGRAMS\Grail"
SectionEnd

; On initialization
Function .onInit
    !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd
'''


def main():
    pass


if __name__ == '__main__':
    main()
