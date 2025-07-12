import cv2
import numpy as np
import joblib
from skimage.feature import hog
from ultralytics import YOLO
from config_dictionaries import color_map
import math
from deskew import determine_skew
from zxingcpp import read_barcodes
from pyzbar.pyzbar import decode, ZBarSymbol
from datetime import datetime
import os
import json
import pandas as pd

#Valores máximos y mínimos para la detección de cada color en HSV
#Azul
lower_blue = np.array([90, 50, 50], dtype="uint8")
upper_blue = np.array([130, 255, 255], dtype="uint8")
#Naranja (Este color es un naranja que tiende a rojo, por lo que usar valores de naranja común no funciona)
lower_orange = np.array([2, 90, 90], dtype="uint8")
upper_orange = np.array([7, 255, 255], dtype="uint8")

model_path=r"C:\Games\python\homebrew_hog_svm_rack_classifier.pkl"
clf = joblib.load(model_path)

# Cargar el modelo
model_path_codebar = 'best.pt'  # Reemplaza con la ruta de tu modelo entrenado
model = YOLO(model_path_codebar)
# Obtener el diccionario de nombres del modelo
model_names = model.names

width_margin = 250  # Margen horizontal para el ROI del código de barras
height_margin = 250  # Margen vertical para el ROI del código de barras 
# Umbral de distancia para considerar detecciones similares
umbral_deteccion = 400

# Global: tiempo de última ejecución
last_coil_detection_time = 0

#Método para la obtención de las coordenadas para los 3 checkpoints horizontales para el conteo de racks
#TODO: Añadir los cálculos para los checkpoints verticales para usar con el filtro azul
def obtain_checkpoints(width, height,horizontal_checkpoints):
    half_height = int(height / 2)
    #half_width = int(width / 2)
    if horizontal_checkpoints:
        x, y, w, h = width // 4, 50, width // 2, 150           # Área superior central
        x2, y2, w2, h2 = width // 4, half_height - 50, width // 2, half_height + 50  # Área centro
        x3, y3, w3, h3 = width // 4, height - 150, width // 2, height - 50        # Área inferior

    return [(x,y,w,h), (x2,y2,w2,h2), (x3,y3,w3,h3)]

#Método para la aplicación de cada máscara de manera individual (Para el color azul  y naranja)
def genera_masc(frame,lower,upper):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame_hsv, lower, upper)
    return mask

#Método para la búsqueda de contornos grandes después de aplicar una máscara y su guardado en un arreglo, tomándolos en cuenta
#al sobrepasar un área de 8000 píxeles, puede ser moddificado para acoplarse a diferentes tamaños de imágen
#HACER PRUEBAS CON 12000 Y 15000 PARA EVITAR DETECCIÓN DE FALSOS POSITIVOS
#ACTUALIZACIÓN: AL ESTAR TRABAJANDO CON LA MITAD DE LA RESOLUCION EN EL GUI, LAS ÁREAS MÍNIMAS TAMBIÉN SE DIVIDEN EN DOS
#Nuevas áreas: 7500
def contornosImg(mask,min_area=7500):
    big_contours = []
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            big_contours.append(cnt)
    #if len(big_contours) == 0:
        #print("No se encontraron contornos superiores a los 10000 píxeles")
    return big_contours

#Método para detectar la presencia de colores dentro de un checkpoint aplicando un filtro y devolviendo true
#solamente si la presencia de ese color sobrepasa el 10% del área total del checkpoint, para evitar que detecciones pequeñas
#generen un falso positivo
def detect_color_in_area(frame, x, y, w, h, color_ranges, threshold_ratio=0.07):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    area_hsv = hsv_frame[y:y+h, x:x+w]

    mask_total = np.zeros(area_hsv.shape[:2], dtype=np.uint8)
    for lower, upper in color_ranges:
        lower_np = np.array(lower, dtype=np.uint8)
        upper_np = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(area_hsv, lower_np, upper_np)
        mask_total = cv2.bitwise_or(mask_total, mask)

    # Calcula porcentaje de pixeles activados
    pixel_count = cv2.countNonZero(mask_total)
    total_pixels = mask_total.shape[0] * mask_total.shape[1]
    coverage_ratio = pixel_count / total_pixels

    return coverage_ratio >= threshold_ratio

def paint_checkpoint(frame, x, y, w, h):
    cv2.rectangle(frame, (x, y), (w, h), (0, 140, 255), 2)
    cv2.putText(frame, f"Color detectado", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 2)

#Método para la obtención de la máscara de 3 checkpoints generándolos de manera indicvidual y mezclándolos uno a uno
#para finalmente aplicar la máscara a la imagen con solo partes naranjas, regresando una imagen con solo partes visibles
#en los checkpoints
def checkpoint_mask_obtention(frame, mask_applied):
    height = frame.shape[0]
    width = frame.shape[1]

    (x, y, w, h), (x2, y2, w2, h2), (x3, y3, w3, h3) = obtain_checkpoints(width, height, horizontal_checkpoints=True)

    checkpoint_mask1 = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.rectangle(checkpoint_mask1, (x, y), (w + x, h), (255, 255, 255), -1)

    checkpoint_mask2 = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.rectangle(checkpoint_mask2, (x2, y2), (w2 + x2, h2), (255, 255, 255), -1)

    two_checkpoint_mask = cv2.bitwise_or(checkpoint_mask1, checkpoint_mask2)

    checkpoint_mask3 = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.rectangle(checkpoint_mask3, (x3, y3), (w3 + x3, h3), (255, 255, 255), -1)

    three_checkpoint_mask = cv2.bitwise_or(two_checkpoint_mask, checkpoint_mask3)

    checkpoint_orange = cv2.bitwise_and(mask_applied, mask_applied, mask=three_checkpoint_mask)

    return checkpoint_orange

#Método encargado de realizar la predicción del estado del Rack mediante un modelo de clasificación preentrenado (SVM)
#usando Histogram of Oriented Gradients (HOG), regresando True si el espacio está ocupado o False si no
def predict_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (128, 128))
    features = hog(gray, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), block_norm='L2-Hys')
    prediction = clf.predict([features])[0]
    label_map = {0: "vacio", 1: "parcial", 2: "lleno"}
    predicted_label = label_map[prediction]
    if(predicted_label == "vacio"):
        return False
    elif(predicted_label == "parcial" or predicted_label == "lleno"):
        return True
    else:
        print("Error en el proceso de predicción")
        return False
    
#Máquina de estados para el conteo de Racks usando la presencia 
# de objetos en los checkpoints 1,2 y 3, devuelve su estado actual y el conteo de racks
def state_machine(current_state, rack_counter, 
                found_rack, checkpoint_presence1, checkpoint_presence2, checkpoint_presence3):
    # Máquina de estados para detectar el paso secuencial por los checkpoints
    if current_state == 0 and checkpoint_presence1:
        current_state = 1
        #paint_checkpoint(frame_rgb, x, y, w+x, h)
        #print("Checkpoint 1 alcanzado")
    elif current_state == 1 and checkpoint_presence2:
        current_state = 2
        #paint_checkpoint(frame_rgb, x2, y2, w2+x2, h2)
        #print("Checkpoint 2 alcanzado")
    elif current_state == 2 and checkpoint_presence3:
        #paint_checkpoint(frame_rgb, x3, y3, w3+x3, h3)
        if found_rack:
            rack_counter += 1
            #print("Rack contado")
        else:
            print("Checkpoint 3 alcanzado pero no se encontró rack")
        current_state = 0  # Reiniciar máquina de estados
    return current_state, rack_counter

#Método principal del procesamiento del frame para racks
def rack_preprocessing(frame_rgb, rack_counter, current_state):
    width_frame = len(frame_rgb[0])
    height_frame = len(frame_rgb)

    (x, y, w, h), (x2, y2, w2, h2), (x3, y3, w3, h3) = obtain_checkpoints(width_frame, height_frame, horizontal_checkpoints=True)

    #Obtención de ambas máscaras
    mask_blue= genera_masc(frame_rgb,lower_blue,upper_blue)
    mask_orange= genera_masc(frame_rgb,lower_orange,upper_orange)

    #combined_mask = cv2.bitwise_or(mask_blue, mask_orange)
    orange_mask_applied = cv2.bitwise_and(frame_rgb, frame_rgb, mask=mask_orange)
    checkpoint_orange = checkpoint_mask_obtention(frame_rgb, orange_mask_applied)

    #Obtención de los contornos en un arreglo más los contornos combinados de ambos colores
    contour_orange = contornosImg(mask_orange)
    contour_blue = contornosImg(mask_blue)
    #contour_ex = contornosImg(combined_mask)

    checkpoint_presence1 = detect_color_in_area(checkpoint_orange, x, y, w + x, h, [([2, 90, 90], [7, 255, 255])])
    checkpoint_presence2 = detect_color_in_area(checkpoint_orange, x2, y2, w2 + x2, h2, [([2, 90, 90], [7, 255, 255])])
    checkpoint_presence3 = detect_color_in_area(checkpoint_orange, x3, y3, w3 + x3, h3, [([2, 90, 90], [7, 255, 255])])

    if len(contour_blue) >= 2 and len(contour_orange) >= 1:
        #print("Espacio de Rack encontrado")
        cv2.drawContours(frame_rgb, contour_orange, -1, (8, 177, 239), 1)
        cv2.drawContours(frame_rgb, contour_blue, -1, (0, 255, 0), 1)
        found_rack = True

        if rack_counter == 0 and found_rack:
            rack_counter += 1

        is_occupied = predict_image(frame_rgb)
    else:
        #print("Espacio de Rack no encontrado")
        found_rack = False

    current_state, rack_counter = state_machine(current_state, rack_counter, found_rack, checkpoint_presence1, checkpoint_presence2, checkpoint_presence3)

    cv2.putText(frame_rgb, f"Racks: {rack_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 3)
    cv2.putText(frame_rgb, f"Is a rack fully visible?: {found_rack}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 3)
    if found_rack and is_occupied:
        cv2.putText(frame_rgb, f"Rack occupied", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 3)

    return frame_rgb, rack_counter, current_state

def coil_processing(frame_rgb, rack_counter, code_length, prev_detections, frame_count, min_width=250, min_height=250):
    results = model.predict(frame_rgb, conf=0.5, iou=0.45)
    detections_list = []
    #second_frame = frame_rgb
    frame_detections = []
    roi = []

    for obj in results[0].boxes:
        x1, y1, x2, y2 = map(int, obj.xyxy[0])
        widht = x2 - x1
        height = y2 - y1
        
        # Procesar detecciones
        detect = {
            "label": model_names[int(obj.cls[0])],
            "box": (x1, y1, x2, y2),
            "center_x": (x1 + x2) // 2,
            "center_y": (y1 + y2) // 2,
            "color": color_map.get(model_names[int(obj.cls[0])], None),
            "widht": widht,
            "height": height
        }
        detections_list.append(detect)

    for detection in detections_list:
        if (detection["label"] in ["Etiqueta"] or detection["label"] in ["Broken"]) and (detection["widht"] > width_margin or detection["height"] > height_margin):
            center_current = (detection["center_x"], detection["center_y"])
            x1, y1, x2, y2 = detection["box"]

            
            found_prev = None

            # Buscar en las detecciones previas si existe una con centro cercano
            for pd in prev_detections:
                distance = math.sqrt((center_current[0] - pd["center"][0])**2 + (center_current[1] - pd["center"][1])**2)
                # Umbral: si la distancia es menor al umbral, consideramos que es la misma etiqueta
                if distance < umbral_deteccion:
                    found_prev = pd
                    break

            if found_prev:
                text = found_prev["text"]
                # ACTUALIZAR LA DETECCIÓN PREVIA
                found_prev["center"] = center_current
                found_prev["last_frame"] = frame_count
                cv2.putText(frame_rgb, text, (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (45, 230, 39), 2)
                print(f"Alguna detección previa contaba con un centro cercano menor \nal umbral de {umbral_deteccion} para la deteccion {text}")

            else:
                roi = frame_rgb[y1+100:y2+100, x1-100:x2+100] #Debe ser mas grande que el QR o Codigo de barras
                if roi.size > 0:
                    # Lectura de codigo
                    text = process_image(roi, code_length)
                    if text is not None:
                        cv2.putText(frame_rgb, text, (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (45, 230, 39), 2)
                        print("Encontrado: ", text)
                        frame_detections.append({"type": "ID", "value": text})
                        prev_detections.append({
                            "center": center_current,
                            "text": text,
                            "last_frame": frame_count
                        })
                
            cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), detection["color"], 2)

    return frame_detections, frame_rgb, roi

def rotate_image(image, angle, bg_color=(255, 255, 255)):
    """Rota una imagen en el ángulo especificado"""
    # Obtener altura y anchura
    if len(image.shape) == 3:
        height, width, _ = image.shape
    else:
        height, width = image.shape
    
    # Calcular el centro de la imagen
    center = (width / 2, height / 2)
    
    # Obtener matriz de rotación
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Calcular nuevas dimensiones para encajar toda la imagen rotada
    abs_cos = abs(rotation_matrix[0, 0])
    abs_sin = abs(rotation_matrix[0, 1])
    
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)
    
    # Ajustar la matriz de transformación
    rotation_matrix[0, 2] += bound_w / 2 - center[0]
    rotation_matrix[1, 2] += bound_h / 2 - center[1]
    
    # Aplicar rotación con el color de fondo especificado
    if len(image.shape) == 3:
        rotated = cv2.warpAffine(image, rotation_matrix, (bound_w, bound_h), 
                                borderMode=cv2.BORDER_CONSTANT, borderValue=bg_color)
    else:
        rotated = cv2.warpAffine(image, rotation_matrix, (bound_w, bound_h), 
                                borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    
    return rotated

def process_image(image, code_lenght):
    """Procesa una imagen usando deskew para corregir la inclinación"""
    text = None

    try:
        #Guardado de las ROI para revisarlas
        #output_dir = "temp_data"
        #os.makedirs(output_dir, exist_ok=True)
        #filename = datetime.now().strftime("code_%Y%m%d_%H%M%S_%f.jpg")
        #filepath = os.path.join(output_dir, filename)
        #cv2.imwrite(filepath, image)

        # Convertir a escala de grises
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Determinar el ángulo de inclinación
        angle = determine_skew(gray)
        
        # Rotar la imagen para corregir la inclinación
        rotated = rotate_image(image, angle)

        blurred = cv2.GaussianBlur(rotated, (3, 3), 0)

        result = read_barcodes(blurred)
        #print("Resultado obtenido de read_barcodes: ", result)

        if result:
            text = result[0].text
            #print(text)
        else:
            code = decode(blurred)
            #print("Resultado obtenido de decode: ", code)
            if code:
                text = code[0].data.decode('utf-8')
                #print(text)

        if text is not None and len(text) >= code_lenght:
            return text
        else:       
            return None
        
    except Exception as e:
        print(e)
        print(f"Error procesando")
        return None

def dataframe_update(codebars, df_actual, current_roi):
    new_entries = []
    output_dir = "Backup"
    void_detection = False
    was_updated = False

    # Asegurar que el DataFrame tiene al menos la columna "ID"
    if "ID" not in df_actual.columns:
        df_actual["ID"] = pd.Series(dtype=str)
        df_actual["timestamp"] = pd.Series(dtype=str)

    for codigo in codebars:
        valor = codigo.get("value", "").strip()
        if valor and valor not in df_actual["ID"].values:
            new_entries.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ID": valor
            })
        elif valor and valor == "Etiqueta no encontrada" or valor == "Sin Rollo":
            new_entries.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ID": valor
            })
            void_detection = True
        elif valor and valor in df_actual["ID"].values:
            print(f"El código {valor} ya se encuentra registrado, no se guardará nuevamente")


    if new_entries and not void_detection:
        new_df = pd.DataFrame(new_entries)
        df_actual = pd.concat([df_actual, new_df], ignore_index=True)
        df_lenght = int(len(df_actual))

        filename = f"Detección_{df_lenght}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, current_roi)
        was_updated = True
    elif new_entries and void_detection:
        new_df = pd.DataFrame(new_entries)
        df_actual = pd.concat([df_actual, new_df], ignore_index=True)
        df_lenght = int(len(df_actual))
        was_updated = True
    return df_actual, was_updated

def json_csv_export(df, ubicacion, posicion, output_folder="Backup", base_name="detecciones_"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Exportar a CSV
    csv_path = os.path.join(output_folder, f"{base_name}_{ubicacion}_{posicion}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8')

    # Convertir a estructura JSON esperada
    json_data = {"detecciones": df.to_dict(orient="records")}
    json_path = os.path.join(output_folder, f"{base_name}_{ubicacion}_{posicion}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json")
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    return csv_path, json_path

def watermarker(frame, watermark, width, height):
    #verificar si la imagen se cargó correctamente
    if watermark is None:
        print("Error: No se pudo cargar la imagen de la marca de agua.")
        exit()

    # Redimensionar la marca de agua a 100 px de ancho manteniendo la relación de aspecto
    porcentaje = 0.2  # Porcentaje del ancho del video
    watermark_width = int(width * porcentaje) 
    aspect_ratio = watermark.shape[0] / watermark.shape[1]
    watermark_height = int(watermark_width * aspect_ratio)
    watermark = cv2.resize(watermark, (watermark_width, watermark_height), interpolation=cv2.INTER_AREA)

    # Convertir la marca de agua a formato BGR si tiene un canal alfa
    if watermark.shape[2] == 4:
        watermark = cv2.cvtColor(watermark, cv2.COLOR_BGRA2BGR)

    # Obtener las dimensiones de la marca de agua redimensionada
    (wH, wW) = watermark.shape[:2]

    #Posición de la marca de agua
    margin = 70  # Margen desde el borde del video
    wy1, wy2 = height - wH -margin, height - margin
    wx1, wx2 = width - wW - margin, width - margin

    overlay = frame.copy()
    overlay[wy1:wy2, wx1:wx2] = watermark
    frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    return frame
