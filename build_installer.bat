@echo off
echo ========================================
echo    SRT Maker Installer Build Script
echo ========================================

:: Check if NSIS is available
set "NSIS_PATH="
where makensis >nul 2>&1
if %errorlevel% equ 0 (
    set "NSIS_PATH=makensis"
) else (
    :: Check common NSIS installation paths
    if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
        set "NSIS_PATH=C:\Program Files (x86)\NSIS\makensis.exe"
    ) else if exist "C:\Program Files\NSIS\makensis.exe" (
        set "NSIS_PATH=C:\Program Files\NSIS\makensis.exe"
    ) else (
        echo NSIS not found in PATH or common locations.
        echo Please add NSIS to PATH or use build_advanced.bat for portable version.
        pause
        exit /b 1
    )
)

echo Found NSIS at: %NSIS_PATH%

:: Build executable first
echo Building executable...
call build.bat

if not exist "dist\SRT_Maker.exe" (
    echo Executable not found. Build failed.
    pause
    exit /b 1
)

:: Create NSIS installer script
echo Creating installer script...
(
echo !include "LogicLib.nsh"
echo.
echo !define APPNAME "SRT Maker"
echo !define COMPANYNAME "Subtitle Translator Pro"
echo !define DESCRIPTION "Professional Subtitle Translation Tool"
echo !define VERSIONMAJOR 1
echo !define VERSIONMINOR 0
echo !define VERSIONBUILD 0
echo !define HELPURL "https://github.com/Anas-KhanWP/srt_maker"
echo !define UPDATEURL "https://github.com/Anas-KhanWP/srt_maker/releases"
echo !define ABOUTURL "https://github.com/Anas-KhanWP/srt_maker"
echo !define INSTALLSIZE 150000
echo.
echo RequestExecutionLevel admin
echo InstallDir "$PROGRAMFILES\${APPNAME}"
echo Name "${APPNAME}"
echo Icon "icon.ico"
echo outFile "SRT_Maker_Installer.exe"
echo.
echo page directory
echo page instfiles
echo.
echo function .onInit
echo     setShellVarContext all
echo     UserInfo::GetAccountType
echo     pop $0
echo     ${If} $0 != "admin"
echo         messageBox mb_iconstop "Administrator rights required!"
echo         setErrorLevel 740
echo         quit
echo     ${EndIf}
echo functionEnd
echo.
echo section "install"
echo     setOutPath $INSTDIR
echo     file "dist\SRT_Maker.exe"
echo     file /nonfatal "README.md"
echo     file /nonfatal "requirements.txt"
echo     file /nonfatal "install_pytorch.bat"
echo     createDirectory "$INSTDIR\cache"
echo     file /nonfatal /r "cache\*.*"
echo.
echo     writeUninstaller "$INSTDIR\uninstall.exe"
echo.
echo     createShortCut "$SMPROGRAMS\${APPNAME}.lnk" "$INSTDIR\SRT_Maker.exe" "" "$INSTDIR\SRT_Maker.exe"
echo     createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\SRT_Maker.exe" "" "$INSTDIR\SRT_Maker.exe"
echo.
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\SRT_Maker.exe$\""
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
echo     WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
echo     WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
echo     WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
echo     WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
echo     WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
echo     WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
echo.
echo     ; Install PyTorch with CUDA support
echo     MessageBox MB_YESNO "Install PyTorch with CUDA support for GPU acceleration?" IDYES install_pytorch IDNO skip_pytorch
echo     install_pytorch:
echo     ExecWait '"$INSTDIR\install_pytorch.bat"' $0
echo     ${If} $0 != 0
echo         MessageBox MB_OK "PyTorch installation failed. You can run install_pytorch.bat manually later."
echo     ${Else}
echo         MessageBox MB_OK "PyTorch with CUDA support installed successfully!"
echo     ${EndIf}
echo     skip_pytorch:
echo sectionEnd
echo.
echo section "uninstall"
echo     delete "$INSTDIR\SRT_Maker.exe"
echo     delete "$INSTDIR\README.md"
echo     delete "$INSTDIR\requirements.txt"
echo     delete "$INSTDIR\install_pytorch.bat"
echo     rmDir /r "$INSTDIR\cache"
echo     delete "$INSTDIR\uninstall.exe"
echo     rmDir "$INSTDIR"
echo.
echo     delete "$SMPROGRAMS\${APPNAME}.lnk"
echo     delete "$DESKTOP\${APPNAME}.lnk"
echo.
echo     DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
echo sectionEnd
) > installer.nsi

:: Build installer
echo Building installer...
"%NSIS_PATH%" installer.nsi

if %errorlevel% neq 0 (
    echo Installer build failed!
    pause
    exit /b 1
)

:: Clean up
del installer.nsi

echo ========================================
echo    Installer build completed!
echo ========================================
echo Installer created: SRT_Maker_Installer.exe
if exist "SRT_Maker_Installer.exe" (
    for %%A in ("SRT_Maker_Installer.exe") do echo Installer size: %%~zA bytes
)
pause