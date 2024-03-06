@echo off
:menu
cls
echo Menú:
echo 1. Iniciar
echo 2. Parar
echo 3. Comprobar entidades
echo 4. Transformar y cargar datos
echo 5. Instalar
echo 6. Desinstalar
echo 7. Salir
set /p option=Selecciona una opción (1-7):

goto opcion_%option%

:opcion_1
call Setup/run.bat
goto menu

:opcion_2
call Setup/stop.bat
goto menu

:opcion_3
curl -G -X GET http://localhost:1026/v2/entities
pause
goto menu

:opcion_4
call Setup/POST.bat
goto menu

:opcion_5
call Setup/install.bat
goto menu

:opcion_6
call Setup/uninstall.bat
goto menu

:opcion_7
echo Saliendo...
exit /b