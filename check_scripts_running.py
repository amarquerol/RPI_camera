#/usr/bin/env python
# -*- coding: utf-8 -*-

### Imports ###
import subprocess,enviar_mail,os

### Variables ###
path_base = "/home/pi/raspberrydespatx"
nom_arxiu_log = "RPiDespatx_log.txt"
script1 = "python /home/pi/raspberrydespatx/RPiDespatx.py"
cmd = "ps aux | grep python "
list_of_scripts = []

### MAIN ###

# Afegim tots els scripts pels que volem fer check que estan corrent a la llista
list_of_scripts.append(script1)

result = subprocess.check_output(cmd, shell=True)

# Recorrem tots els scripts
for one_script in list_of_scripts:
    if one_script not in result:
        #Enviem mail informant de que aquest script en particular no esta corrent
        textSubject = '[RPI TELECOGRESCA DESPATX][SCRIPT CAMARA] ' + 'Script no esta corrent'
        textBody = 'Un dels scripts no esta executant-se' + '. El nom del script es: ' + one_script
        FILE_PATH = path_base + "/" + nom_arxiu_log
        enviar_mail.main(textSubject,textBody,FILE_PATH)
