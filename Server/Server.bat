
:menu
cls
echo Menú:
echo 1. Iniciar
echo 2. Parar
echo 3. Comprobar entidades
echo 4. Instalar
echo 5. Desinstalar
echo 6. Salir
set /p option=Selecciona una opción (1-6):

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
echo Has seleccionado la opción 4
call Setup/install.bat
goto menu

:opcion_5
echo Has seleccionado la opción 5
call Setup/uninstall.bat
goto menu

:opcion_6
echo Saliendo...
exit /b