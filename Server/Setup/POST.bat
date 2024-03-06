@echo off
curl -X POST -H "Content-Type: application/json" -d @Ficheros/parkings_Valencia.json "http://localhost:1026/v2/entities"
cmd /k