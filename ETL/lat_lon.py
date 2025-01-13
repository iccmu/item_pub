import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def get_google_maps_coordinates(lugar):
    # Configuración del driver de Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Añadir más configuraciones para evitar la página de consentimiento
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Primero navegar a Google Maps directamente
        print("Accediendo a Google Maps...")
        driver.get("https://www.google.com/maps")
        time.sleep(3)
        
        # Manejar la página de consentimiento si aparece
        try:
            consent_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Aceptar todo')]"))
            )
            consent_button.click()
            time.sleep(2)
        except:
            print("No se encontró página de consentimiento o ya fue aceptada")
        
        # Ahora buscar el lugar
        search_url = f"https://www.google.com/maps/search/{lugar}"
        print(f"\nBuscando coordenadas para: {lugar}")
        print(f"URL de búsqueda: {search_url}")
        
        driver.get(search_url)
        time.sleep(5)
        
        url_completa = driver.current_url
        print(f"URL resultante: {url_completa}")
        
        # Extraer coordenadas
        if '@' in url_completa:
            coords = url_completa.split('@')[1].split(',')[:2]
            lat, lon = coords[0], coords[1]
            print(f"\n✅ Coordenadas encontradas:")
            print(f"Latitud: {lat}")
            print(f"Longitud: {lon}")
            return lat, lon
        else:
            print("\n❌ No se pudieron extraer las coordenadas")
            return None, None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None, None
    finally:
        driver.quit()

def process_csv():
    # Obtener el directorio donde está el script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'data_con_coordenadas.csv')
    
    # Leer el CSV original
    print("Leyendo archivo CSV...")
    print(f"Buscando archivo en: {csv_path}")
    df = pd.read_csv(csv_path, sep='|')
    
    # Iterar sobre las filas que tienen coordenadas vacías
    for index, row in df.iterrows():
        # Solo buscar coordenadas si el lugar no es NaN y las coordenadas están vacías
        if pd.isna(row['lat']) or pd.isna(row['lon']):
            if not pd.isna(row['Lugar de estreno']):
                print(f"\nProcesando fila {index + 1}: {row['Lugar de estreno']}")
                lat, lon = get_google_maps_coordinates(row['Lugar de estreno'])
                if lat and lon:
                    df.at[index, 'lat'] = float(lat)
                    df.at[index, 'lon'] = float(lon)
            else:
                print(f"\nFila {index + 1}: Lugar de estreno es NaN, saltando...")
    
    # Guardar el DataFrame actualizado
    print("\nGuardando resultados...")
    df.to_csv(csv_path, sep='|', index=False)
    print("✅ Proceso completado")

def main():
    print("=== Actualizador de Coordenadas desde Google Maps ===")
    process_csv()

if __name__ == "__main__":
    main()