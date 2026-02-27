import sys
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style

# Inicializamos variables
url = ""
votos_arg = ""

# Procesamos argumentos
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "-url" and i + 1 < len(args):
        url = args[i + 1]
        i += 2
    else:
        # Cualquier otro argumento lo consideramos votos
        votos_arg = args[i]
        i += 1

# Si no se pasó URL, pedimos interactivo
if not url:
    url = input("Escribe una URL válida: ")

# Aseguramos que la URL este completa
if "://" not in url:
    url = "http://" + url

scheme_end = url.find("://") + 3
slash_pos = url.find("/", scheme_end)
origin = url if slash_pos == -1 else url[:slash_pos]

# Obtenemos el contenido de la página
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# ESTRUCTURA DE DATOS
data = {
    "Metadata": {},
    "Options": {}
}

# Con BeautifulSoup buscamos la estructura de TotalPoll en la página.
# Primero intentamos encontrar el div principal de TotalPoll
div_info_totalpoll = soup.find("div", class_="totalpoll-wrapper")
# Si no lo encontramos, buscamos dentro de iframes que puedan contener la encuesta
if div_info_totalpoll is None:
    for iframe in soup.find_all("iframe"):
        iframe_src = iframe.get("src")
        if iframe_src and "/poll/" in iframe_src:
            response = requests.get(iframe_src)
            soup = BeautifulSoup(response.text, "html.parser")
            div_info_totalpoll = soup.find("div", class_="totalpoll-wrapper")
            if div_info_totalpoll:
                break
if not div_info_totalpoll:
    print(f"{Fore.RED}No se ha encontrado ninguna encuesta de TotalPoll en la página{Style.RESET_ALL}")
    exit()

# Metadata
# Extraemos el ID de la encuesta y el UID para usarlo en los votos
poll_id = div_info_totalpoll.get("totalpoll")
totalpoll_uid = div_info_totalpoll.get("totalpoll-uid")
data["Metadata"]["postId"] = poll_id

# Opciones
# Buscamos el div que contiene las opciones de la encuesta
choices_div = soup.find("div", class_="totalpoll-question-choices")
totalpollchoices_id = ""
if choices_div:
    option_number = 1
    for label in choices_div.find_all("label"):
        for_attr = label.get("for")
        if for_attr and for_attr.startswith("choice-") and for_attr.endswith("-selector"):
            option_id = for_attr.replace("choice-", "").replace("-selector", "")

            if totalpollchoices_id == "":
                input_txt = label.find("input", id=for_attr)
                inputName = input_txt.get("name")
                totalpollchoices_id = inputName.replace("totalpoll[choices][", "").replace("][]", "")
                data["Metadata"]["totalpollchoices-id"] = totalpollchoices_id

            item_label = label.find("div", class_="totalpoll-question-choices-item-label")
            if item_label:
                span = item_label.find("span")
                if span:
                    title = span.text.strip()
                    data["Options"][str(option_number)] = {
                        "Id": option_id,
                        "Title": title
                    }
                    option_number += 1

data["Metadata"]["wrapper-totalpoll-uid"] = totalpoll_uid
totalOpciones = data["Metadata"]["TotalOpciones"] = len(data["Options"])

# FUNCIÓN PARA MOSTRAR OPCIONES
def mostrar_opciones():
    print("\033[H\033[J")  # Limpiar pantalla
    print(f"Votando en → {url}")
    for i in range(1, totalOpciones + 1):
        option_id = str(i)
        option_data = data['Options'][option_id]
        if option_id in votos:
            print(f"{Fore.GREEN}[{i}]: {option_data['Title']} | Id: {option_data['Id']} {Style.RESET_ALL}")
        else:
            print(f"[{i}]: {option_data['Title']} | Id: {option_data['Id']}")

# FUNCIÓN PARA PROCESAR SELECCIONES
def procesar_seleccion(input_text):
    global votos
    entrada = input_text.lower().strip()
    partes = [p.strip() for p in entrada.split(",")]

    for part in partes:
        if part == "all":
            # Agrega todas las opciones, pero no elimina las existentes
            votos = [str(i) for i in range(1, totalOpciones + 1)]
        elif part.startswith("-"):
            # Deselecciona la opción
            opcion = part[1:]
            if opcion in votos:
                votos.remove(opcion)
        else:
            # Selecciona la opción si no estaba
            opcion = part
            if opcion not in votos and opcion.isdigit() and 1 <= int(opcion) <= totalOpciones:
                votos.append(opcion)

# VOTOS INICIALES DESDE ARGUMENTOS (modo automático)
votos = []
modo_automatico = False
if votos_arg:
    procesar_seleccion(votos_arg)
    modo_automatico = True

# SELECCIÓN INTERACTIVA SOLO SI NO HAY ARGUMENTOS
if not modo_automatico:
    continuar = "s"
    while continuar.lower() == "s":
        mostrar_opciones()
        entrada_valida = False

        while not entrada_valida:
            entrada = input(
                "Elige opción(es) (ej. 1,3,5 o 2-4). "
                "Se deselecciona si ya estaba elegida. "
                "Para seleccionar todas, escribe 'all'. "
            )
            procesar_seleccion(entrada)
            entrada_valida = True

        mostrar_opciones()

        continuar = ""
        while continuar.lower() not in ["n", "s"]:
            continuar = input("Quieres elegir mas opciones? (S/N): ")

print("\033[H\033[J")
print(f"{Fore.BLUE}Opciones seleccionadas para votar en → {url}{Style.RESET_ALL}")
for opcion in votos:
    option_data = data['Options'][opcion]
    print(f"{Fore.YELLOW}[{opcion}]: {option_data['Title']} | Id: {option_data['Id']}{Style.RESET_ALL}")
print(f"Enviando votos automaticos {Fore.LIGHTYELLOW_EX}⋝{Style.RESET_ALL}")

# PREPARAR HEADERS Y ENVIAR VOTOS
headers = {
    "accept": "*/*",
    "accept-language": "en-GB,en;q=0.6",
    "cache-control": "no-cache",
    "origin": origin,
    "pragma": "no-cache",
    "referer": url,
    "sec-ch-ua": '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, como Gecko) Chrome/142.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
while True:
    for opcion in votos:
        idVoto = data['Options'][opcion]['Id']
        post_data = {
            f'totalpoll[choices][{data["Metadata"]["totalpollchoices-id"]}][]': f"{idVoto}",
            'totalpoll[screen]': "vote",
            'totalpoll[pollId]': f"{data['Metadata']['postId']}",
            'totalpoll[action]': "vote"
        }

        try:
            response = requests.post(url, headers=headers, data=post_data)
            text = response.text
            if "You cannot vote again." in text:
                print(Fore.RED + f"Error: No puedes votar nuevamente por la opción {opcion}" + Style.RESET_ALL)
            else:
                print(Fore.GREEN + f"Voto registrado para la opción {opcion} [{data['Options'][opcion]['Title']}] [{idVoto}]" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Voto fallido: {e}" + Style.RESET_ALL)
