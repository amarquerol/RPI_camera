#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
###
   import RPi.GPIO as GPIO
   import time
   import os
   import io
   import commands
   import picamera
   import pygame 
   import subprocess
   import smtplib
   import mimetypes
   import email
   import email.mime.application
   import sys   
   import threading
   import glob
   import paramiko
   import queueFotos
   import workersPhotoUpload
   import enviar_mail
   import datetime

   # Noms dels elements
   element2 = 'doorDespatx'
   element3 = 'doorVDE'
   element8 = 'PIRPrincipal'
   element10 = 'PIRSecundari'

   # Si NO son elements PIR els afegim al array
   arrayDe_NO_PIRs = []
   arrayDe_NO_PIRs.append(element2)
   arrayDe_NO_PIRs.append(element3)

   # Simply set these config values to 1 to enable monitoring
   enable_element2_monitor = 1
   enable_element3_monitor = 1
   enable_element8_monitor = 1
#   enable_element10_monitor = 1

   # Sensor connected GPIO pin
   element2_contact = 4
   element3_contact = 27
   element8_contact = 25
#   element10_contact = 
   brunzidor_contact = 22
 
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(element2_contact,GPIO.IN)
   GPIO.setup(element3_contact,GPIO.IN)
   GPIO.setup(element8_contact,GPIO.IN)
#   GPIO.setup(element10_contact,GPIO.IN)
#   GPIO.setup(brunzidor_contact,GPIO.IN)
#   GPIO.setup(brunzidor_contact, GPIO.OUT, initial=GPIO.HIGH)

   shl_cmd= 'readlink -f $(dirname LKR0.00)'
   base_path = commands.getoutput(shl_cmd)
   img_base = base_path + '/images/'

   hostnamePrincipal = "RPiDespatx1"
   hostnameSecundari = "RPiDespatx2"
#   IPSecundari =  = '192.168.1.25'

   # Arra yde RPi secundaris (el principal es el de l entrada)
   arrayDeRPIs = []
   arrayDeRPIs.append(hostnameSecundari)


   def llegirHostname():
      fileName = "/etc/hostname"
      with open(fileName) as myfile:
           lastLine = list(myfile)[-1]
      print 'Hostname: '+lastLine
      return (lastLine)

   def algun_NO_PIRactivatRecentment(arrayDe_NO_PIRs):
      for unElement in arrayDe_NO_PIRs:
          ultimaDataArxiu = llegirDarreraDataDeFitxer(unElement)
          # La data ve en aquest format: 31/01/2016-18-10-00
          date_read = datetime.datetime.strptime(ultimaDataArxiu,"%d/%m/%Y-%H-%M-%S")
          print "Printo la date_read: ",date_read
          # Valors actuals
          date_now = datetime.datetime.now()
          print "Printo la date_now: ",date_now
          # Resta de valors
          date_resta = date_now - date_read
          print "Printo la date_resta: ",date_resta
          print "I ara printo el abs(date_resta.total_seconds(): ",abs(date_resta.total_seconds())
          if abs(date_resta.total_seconds()) <= 39:
              print "Fa menys de ",str(abs(date_resta.total_seconds()))," segons que s'ha obert la porta.\n"
              return 1  
      
      return 0

   def capture_frame():
      streamFoto = io.BytesIO()
      date_now = datetime.datetime.now()
      with picamera.PiCamera() as cam:
          cam.start_preview()
          # Camera warm-up time
          time.sleep(0.1)
          cam.capture(streamFoto, 'jpeg')
          print "Faig foto." + " Data: " + str(date_now) + "\n"
          queueFotos.myQueue.put(streamFoto)

   def rafaga_3_fotos():
       for x in range(3):
           capture_frame()

   def whichFileToPrintOn(elementAMonitortizar):
        if (elementAMonitortizar == element2):
		fileName = 'values/' + element2 + '_state.value'
		return fileName
        if (elementAMonitortizar == element3):
		fileName = 'values/' + element3 + '_state.value'
		return fileName
        if (elementAMonitortizar == element8):
                fileName = 'values/' + element8 + '_state.value'
                return fileName   
        if (elementAMonitortizar == element10):
                fileName = 'values/' + element10 + '_state.value'
                return fileName

   def llegirDarrerEstatDeFitxer(elementAMonitoritzar):
      fileName = whichFileToPrintOn(elementAMonitoritzar)

      with open(fileName) as myfile:
           lastLine = list(myfile)[-1]

      ultimValorArxiu = int(str(lastLine).split(";")[0].strip())
      return (ultimValorArxiu)

   def llegirDarreraDataDeFitxer(elementAMonitoritzar):
      fileName = whichFileToPrintOn(elementAMonitoritzar)

      with open(fileName) as myfile:
           lastLine = list(myfile)[-1]

      ultimValorArxiu = str(lastLine).split(";")[1].strip()
      return (ultimValorArxiu)

   def printToFile( elementAMonitoritzar, estatObertOTancat ):
      dataActualObert = time.strftime("\n1;%d/%m/%Y-%H-%M-%S")
      dataActualTancat = time.strftime("\n0;%d/%m/%Y-%H-%M-%S")
      elementAMonit = elementAMonitoritzar
      
      fileName = whichFileToPrintOn(elementAMonit)
     
      ultimValorArxiu=llegirDarrerEstatDeFitxer(elementAMonitoritzar)
      if estatObertOTancat:
          if not ultimValorArxiu:
              fa = open(fileName, "a")
              fa.write(dataActualObert)
              fa.close()
      if not estatObertOTancat: 
          if ultimValorArxiu:
              fa = open(fileName, "a")
              fa.write(dataActualTancat)
              fa.close()

   def accionsAlarma(state, nomElement, prev_input_element, tipusSensorPIR):
      printarEstat = nomElement + ' State: ' + state + '     |   ' + time.strftime("%d/%m/%Y-%H-%M-%S")
      
      if(state == 'Open'):
          prev_input_element = 1
      if(state == 'Close'):
          prev_input_element = 0
      print 'Updating API - Nom element: ' + str(nomElement) + "Data: " +  str(datetime.datetime.now())
      printToFile( nomElement, prev_input_element )

      # Si es la porta (no es un pir) faig una rafaga de 3 fotos. 
      if "yes" not in tipusSensorPIR: 
          print "Es la porta. No es un pir. Nom element: " + str(nomElement)          
          rafaga_3_fotos()

      algun_NO_PIRactivatRecentment_boolean = algun_NO_PIRactivatRecentment(arrayDe_NO_PIRs)

      print "Evaluo el tipusSensorPIR: ",tipusSensorPIR," i el algun_NO_PIRactivatRecentment_boolean: ",algun_NO_PIRactivatRecentment_boolean
      if "yes" in tipusSensorPIR and algun_NO_PIRactivatRecentment_boolean:
          print "Espero 3 segons i faig foto."
          time.sleep(3)
          capture_frame()

      print 'OK API Updated'
      
      return (prev_input_element)

   def elementMonitoritzable(enable, nomElement, element_contact, tipusSensorPIR ):
      
      prev_input_element = llegirDarrerEstatDeFitxer(nomElement)

      if(enable):
        input_element = GPIO.input(element_contact)
        if(input_element):
           if(not prev_input_element):
              prev_input_element = accionsAlarma('Open', nomElement, prev_input_element, tipusSensorPIR)
              
        if(not input_element):
           if(prev_input_element):
               prev_input_element = accionsAlarma('Close', nomElement, prev_input_element, tipusSensorPIR)

        time.sleep(0.05)


####  MAIN  ####

   #Per no sortir del bucle global de l arxiu
   enableGlobal = 1
   # Crido una unica vegada al module de la Queue
   queueFotos.init()
   # Llegeixo el hostname
   hostname = llegirHostname()
   # Crido al modul dels workers. Per pujar fotos al S3
   workersPhotoUpload.main(hostname)

   # Al principi val 0
   while enableGlobal:

       if hostnamePrincipal in hostname:
           elementMonitoritzable(enable_element2_monitor, element2, element2_contact, 'no' )
           elementMonitoritzable(enable_element3_monitor, element3, element3_contact, 'no' )
           elementMonitoritzable(enable_element8_monitor, element8, element8_contact, 'yes' )
           #elementMonitoritzable(enable_element10_monitor, element10, element10_contact, 'yes' )

except IOError as (errno, strerror):
    directory_path = "/home/pi/raspberrydespatx/RPiDespatx.py"
    text_subject = "[RPi Despatx][Telecogresca] Error amb el script de les fotos"
    text_error = "I/O error({0}): {1}".format(errno, strerror)
    enviar_mail.main(text_subject,text_error,directory_path)
except ValueError:
    directory_path = "/home/pi/raspberrydespatx/RPiDespatx.py"
    text_subject = "[RPi Despatx][Telecogresca] Error amb el script de les fotos"
    text_error = "Could not convert data to an integer."
    enviar_mail.main(text_subject,text_error,directory_path)
except:
    directory_path = "/home/pi/raspberrydespatx/RPiDespatx.py"
    text_error = "Unexpected error:", sys.exc_info()[0]
    text_subject = "[RPi Despatx][Telecogresca] Error amb el script de les fotos"
    enviar_mail.main(text_subject,text_error,directory_path)
