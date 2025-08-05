import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
import os
from process_methods import *
from threading import Thread
import pandas as pd
import socket
import time
from Super_Stream import *
#from pynput.keyboard import Listener

#def on_press(key):
#    try:
#        print(key.char)
#    except:
#        print(key)

#with Listener(on_press=on_press) as listener:
#    listener.join()

def main(url, ubicacion, posicion):
    def finalizar_vuelo():
        stream_reader.stop()
        csv_path, json_path = json_csv_export(saved_codebars, ubicacion, posicion, output_dir)
        print(f"Archivos exportados a: \n {csv_path} \n {json_path}")
        saved_codebars.iloc[0:0]
        return

    if url is not None:
        isRunning = True
        stream_reader = VideoStreamReader(url)
        output_dir = f"Backup_{ubicacion}_{posicion}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        border_trigger = False
        saved_codebars = pd.DataFrame()
        info_tuple = []
        prev_detections = []
        last_codebar_found = "None"
        frame_count = 0
        rack_counter = 0
        id_length = 10
        still_frame = None
    else:
        print("URL no especificada, cerrando programa...")
        return
    
    if not stream_reader.ret:
        print("\nError al abrir la fuente de video.")
        isRunning = False
        return
    else:
        height_frame, width_frame, fps = stream_reader.get_info()
        new_height = int(height_frame/4)
        new_width = int(width_frame/4)
        print(height_frame)
        print(width_frame)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"El directorio {output_dir} ha sido creado")
    
    while isRunning:
        frame, ret = stream_reader.read()
        if frame is None:
            print("No se encontró Frame")
            if ret:
                print("Stream aún activo, recibiendo frame...")
                time.sleep(0.1)
                continue
            else:
                print("Stream no encontrado o finalizado")
                finalizar_vuelo()
                isRunning = False
                cv2.destroyAllWindows()
                return
        
        if frame_count % 2 == 0:
            found_codes, processed_frame, current_roi, on_screen, current_text = coil_processing(frame, rack_counter, id_length, saved_codebars, frame_count)
            print(found_codes)
            print(current_text)
            #if not last_codebar_found == current_text and current_text is not None:
            saved_codebars, was_updated, border_trigger, last_codebar_found = dataframe_update(found_codes, saved_codebars, current_roi, output_dir, on_screen, current_text)
            #print("Dataframe Actualizado")
            processed_frame = draw_frame_with_border(processed_frame, border_trigger)
            still_frame = processed_frame
        else:
            if still_frame is not None:
                processed_frame = draw_frame_with_border(still_frame, border_trigger) 
        
        frame_count+=1
        chopped_array = cv2.resize(processed_frame, (new_width,new_height))
        #frame_rgb = cv2.cvtColor(chopped_array, cv2.COLOR_BGR2RGBA)
        cv2.imshow('MainAudit', chopped_array)
        #cv2.imshow('MainAudit', processed_frame)
        cv2.waitKey(1)

        time.sleep(0.033)
    
#print("Ingrese la dirección del stream o video a usar para el programa:")
#url = input()
url = r"C:\Games\python\DJI_BEST.MP4"
print(f"Leyendo video desde: {url}\nEl programa se encargará de leer las etiquetas en el video y al terminar o no recibir más frames, exportará las etiquetas leídas en formato CSV y JSON")
print("Ingrese la ubicación:")
ubi = input()
print("Ahora ingrese la posicion:")
pos = input()
main(url, ubi, pos)
