import requests
import json
import os

API_URL = "http://localhost:8000"

def imprimir_menu():
    print("\n--- CLI DE PRUEBAS SAFIPN ---")
    print("1. Ver estado de la API (Health Check)")
    print("2. Registrar Visitante (POST /acceso/visitante/)")
    print("3. Listar Usuarios (GET /usuarios/)")
    print("4. Registrar Nuevo Usuario con Biometría (POST /usuarios/)")
    print("5. Verificar Acceso Biométrico (POST /acceso/verificar/)")
    print("6. Salir")
    return input("Selecciona una opción: ")

def test_health():
    try:
        response = requests.get(f"{API_URL}/")
        print("\n[Health Check] Status:", response.status_code)
        print("Respuesta:", response.json())
    except requests.exceptions.ConnectionError:
        print("\n[Error] No se pudo conectar. ¿El servidor está corriendo en localhost:8000?")

def test_registrar_visitante():
    print("\n-- Registrar Nuevo Visitante --")
    nombre = input("Ingresa el motivo o nombre del visitante: ")
    try:
        puerta = int(input("ID de la puerta (ej. 1, 2, 3): "))
        tipo_mov = int(input("Tipo de movimiento (1=Entrada, 2=Salida): "))
    except ValueError:
        print("Por favor, ingresa números válidos para puerta y movimiento.")
        return

    payload = {
        "motivo": nombre,
        "puerta_id": puerta,
        "tipo_mov": tipo_mov
    }

    try:
        response = requests.post(f"{API_URL}/acceso/visitante/", json=payload)
        print("\n[Registro de Visitante] Status:", response.status_code)
        print("Respuesta:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"\n[Error] {e}")

def test_listar_usuarios():
    try:
        response = requests.get(f"{API_URL}/usuarios/")
        print("\n[Listar Usuarios] Status:", response.status_code)
        usuarios = response.json()
        print(f"Total de usuarios encontrados: {len(usuarios)}")
        for u in usuarios:
            print(f"- ID: {u.get('id_usuario')} | Nombre: {u.get('nombre')} {u.get('ap_pat')} | Matrícula: {u.get('matricula')} | Vigencia: {u.get('vigencia')}")
    except Exception as e:
        print(f"\n[Error] {e}")

def test_registrar_usuario(nombre:str, ap_pat:str, ap_mat:str, fech_naci:str, curp:str, sexo:str, turno:str, roles_id:int, matricula:str    ):
    print("\n-- Registrar Nuevo Usuario con Foto --")
    nombre = input("Nombre: ")
    ap_pat = input("Apellido Paterno: ")
    ap_mat = input("Apellido Materno (opcional): ")
    fech_naci = input("Fecha de nacimiento (YYYY-MM-DD): ")
    curp = input("CURP (18 caracteres): ")
    sexo = input("Sexo (M/F): ")
    turno = input("Turno (M/V): ")
    
    try:
        roles_id = int(input("ID del rol (1=Personal, 2=Alumnos): "))
        matricula = input("Matrícula (opcional): ")
    except ValueError:
        print("Entrada inválida.")
        return

    # IMPORTANTE: Captura automática por cámara
    print("\n[Cámara] Inicializando webcam. Por favor, colócate frente a la cámara...")
    import cv2
    import face_recognition

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara web. Verifica los permisos o conexión.")
        return

    foto_path = "temp_registro.jpg"
    rostro_valido = False
    
    print("[Cámara] Muestra la ventana de la cámara. Acomódate y presiona 'ESPACIO' para tomar la foto. (Presiona 'q' para salir)")
    
    mensaje = "Presiona ESPACIO para capturar"
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error leyendo el dispositivo de video.")
            break
            
        # Reflejar la imagen (efecto espejo) para que sea más natural
        frame = cv2.flip(frame, 1)
        
        # Poner instrucciones en pantalla
        cv2.putText(frame, mensaje, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Registro Biometrico SAFIPN", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == 32:  # 32 es el código ASCII para ESPACIO
            # Convertir a RGB para procesar
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            print("\nAnalizando foto capturada...")
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if len(face_locations) == 1:
                print("¡Rostro detectado correctamente! Guardando captura...")
                # Dibujar rectángulo en el rostro para feedback visual (opcional)
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.imshow("Registro Biometrico SAFIPN", frame)
                cv2.waitKey(500) # Mostrar resultado medio segundo
                
                # Guardar el frame limpio que no tiene el rectangulo para el backend (o sí lo tiene, no importa)
                # Mejor lo guardamos sin rectángulo para el encoding
                cv2.imwrite(foto_path, cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))
                rostro_valido = True
                break
            elif len(face_locations) > 1:
                mensaje = "Error: Multiples rostros detectados."
                print("Se detectaron varias caras. Intenta de nuevo.")
            else:
                mensaje = "Error: Ningun rostro detectado."
                print("No se encontró ningún rostro. Intenta de nuevo.")
            
    cap.release()
    try:
        cv2.destroyAllWindows()
    except:
        pass

    if not rostro_valido:
        print("Captura cancelada o fallida.")
        return

    # Construir data del formulario
    form_data = {
        "nombre": nombre,
        "ap_pat": ap_pat,
        "ap_mat": ap_mat if ap_mat else None,
        "fech_naci": fech_naci,
        "curp": curp,
        "sexo": sexo,
        "turno": turno if turno else None,
        "vigencia": 1,
        "roles_id": roles_id,
        "matricula": int(matricula) if matricula.isdigit() else None
    }

    print(f"\nSubiendo datos biométricos y creando usuario...")
    try:
        with open(foto_path, 'rb') as f:
            files = {'file': ('rostro_captura.jpg', f, 'image/jpeg')}
            response = requests.post(f"{API_URL}/usuarios/", data=form_data, files=files)
            
            print("\n[Registro de Usuario] Status:", response.status_code)
            if response.status_code == 201:
                print("¡Usuario registrado exitosamente (rostro procesado)!")
            print("Respuesta:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
        # Limpiar archivo temporal
        if os.path.exists(foto_path):
            os.remove(foto_path)
    except Exception as e:
        print(f"\n[Error] {e}")

def test_acceso_biometrico():
    print("\n-- Control de Acceso Biométrico --")
    try:
        puerta = int(input("ID de la puerta (ej. 1, 2, 3): "))
        tipo_mov = int(input("Tipo de movimiento (1=Entrada, 2=Salida): "))
    except ValueError:
        print("Por favor, ingresa números válidos para puerta y movimiento.")
        return

    print("\n[Cámara] Inicializando webcam. Por favor, colócate frente a la cámara...")
    import cv2
    import face_recognition

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara web.")
        return

    foto_path = "temp_acceso.jpg"
    rostro_valido = False
    
    print("[Cámara] Muestra la ventana de la cámara. Acomódate y presiona 'ESPACIO' para escanear tu rostro. (Presiona 'q' para salir)")
    mensaje = "Presiona ESPACIO para escanear"
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error leyendo el dispositivo de video.")
            break
            
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, mensaje, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Acceso Biometrico SAFIPN", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 32:  
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print("\nAnalizando rostro...")
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if len(face_locations) == 1:
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
                cv2.imshow("Acceso Biometrico SAFIPN", frame)
                cv2.waitKey(500) 
                cv2.imwrite(foto_path, cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))
                rostro_valido = True
                break
            elif len(face_locations) > 1:
                mensaje = "Error: Multiples rostros detectados."
            else:
                mensaje = "Error: Ningun rostro detectado."
            
    cap.release()
    try:
        cv2.destroyAllWindows()
    except:
        pass

    if not rostro_valido:
        print("Escaneo cancelado o fallido.")
        return

    form_data = {
        "puerta_id": puerta,
        "tipo_mov": tipo_mov
    }

    print(f"\nVerificando identidad con la base de datos...")
    try:
        with open(foto_path, 'rb') as f:
            files = {'file': ('rostro_acceso.jpg', f, 'image/jpeg')}
            response = requests.post(f"{API_URL}/acceso/verificar/", data=form_data, files=files)
            
            print("\n[Control de Acceso] Status:", response.status_code)
            try:
                data = response.json()
                estatus = data.get("estatus_acce")
                motivo = data.get("motivo")
                
                print("========================================")
                if estatus == 1:
                    print("✅ ACCESO PERMITIDO")
                else:
                    print(f"❌ ACCESO DENEGADO (Motivo: {motivo})")
                print("========================================")
                
                print("Detalles completos:")
                print(json.dumps(data, indent=2))
            except:
                print(response.text)
                
        if os.path.exists(foto_path):
            os.remove(foto_path)
    except Exception as e:
        print(f"\n[Error] {e}")

def main():
    while True:
        opcion = imprimir_menu()
        if opcion == '1':
            test_health()
        elif opcion == '2':
            test_registrar_visitante()
        elif opcion == '3':
            test_listar_usuarios()
        elif opcion == '4':
            test_registrar_usuario()
        elif opcion == '5':
            test_acceso_biometrico()
        elif opcion == '6':
            print("Saliendo de la herramienta de prueba...")
            break
        else:
            print("Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
