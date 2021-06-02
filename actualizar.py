from bs4 import BeautifulSoup as soup
import requests
import pymongo


def partidosDB(jugador, partido):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["prueba"]
    collection = db["partidos"]

    partidoDB = {}

    partidoDB["jugador"] = jugador
    partidoDB["jornada"] = partido[0]
    partidoDB["fecha"] = partido[1]
    partidoDB["localizacion"] = partido[2]
    partidoDB["club"] = partido[3]
    partidoDB["adversario"] = partido[4]
    partidoDB["resultado"] = partido[5]

    if len(partido) == 7:
        partidoDB["problema"] = partido[6]
    else:
        partidoDB["posicion"] = partido[6]
        partidoDB["goles"] = partido[7]
        partidoDB["asistencias"] = partido[8]
        partidoDB["amarillas"] = partido[9]
        partidoDB["segundas_amarillas"] = partido[10]
        partidoDB["rojas"] = partido[11]
        partidoDB["tiempo_juego"] = partido[12]


    x = collection.insert_one(partido)


def jugadoresDB(datosJug, partido):

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["prueba"]
    collectionJugador = db["jugadores"]

    myquery = {'nombre': datosJug["nombre"]}

    goles = int(datosJug["goles"])
    asistencias = int(datosJug["asistencias"])
    amarillas = int(datosJug["amarillas"])
    segundas_amarillas = int(datosJug["segundas_amarillas"])
    rojas = int(datosJug["rojas"])
    tiempo_juego = int(datosJug["tiempo_juego"])
    victorias = int(datosJug["victorias"])
    derrotas = int(datosJug["derrotas"])
    empates = int(datosJug["empates"])
    ausencias = int(datosJug["ausencias"])

    if (len(partido) == 7):
        ausencias += 1

    else:
        goles += int(partido[7])
        asistencias += int(partido[8])
        amarillas += int(partido[9])
        segundas_amarillas += int(partido[10])
        rojas += int(partido[11])
        tiempo_juego += int(partido[12])

        if (partido[5].split(":")[0] > partido[5].split(":")[1]):
            if (partido[2] == "Fuera"):
                derrotas += 1
            elif (partido[2] == "Casa"):
                victorias += 1
        elif (partido[5].split(":")[0] < partido[5].split(":")[1]):
            if (partido[2] == "Fuera"):
                victorias += 1
            elif (partido[2] == "Casa"):
                derrotas += 1
        if (partido[5].split(":")[0] == partido[5].split(":")[1]):
            empates += 1

    datosJug["goles"] = goles
    datosJug["asistencias"] = asistencias
    datosJug["amarillas"] = amarillas
    datosJug["segundas_amarillas"] = segundas_amarillas
    datosJug["rojas"] = rojas
    datosJug["tiempo_juego"] = tiempo_juego
    datosJug["victorias"] = victorias
    datosJug["derrotas"] = derrotas
    datosJug["empates"] = empates
    datosJug["ausencias"] = ausencias

    collectionJugador.delete_one(myquery)

    x = collectionJugador.insert_one(datosJug)

if __name__ == "__main__":

    headers = {'User-Agent':
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["prueba"]
    cJugadores = db["jugadores"]

    for x in cJugadores.find():

        pagePartidos = "https://www.transfermarkt.es/x/leistungsdaten/spieler/" + x["id_jug"]

        treePartidos = requests.get(pagePartidos, headers=headers)
        soupPartidos = soup(treePartidos.content, 'html.parser')

        myquery = {"jugador": x["nombre"]}

        listaPartidos = []

        listaInfoPartidos = []

        partidoInfo = []

        league = ''

        for divs in soupPartidos.findAll("div", {"class": "box"}):

            if len(divs.findAll("a", {
                "name": ["ES1", "IT1", "GB1", "L1", "FR1", "PO1", "RU1", "BE1", "NL1", "A1", "SC1", "UKR1"]})) != 0:
                league = divs

        if (league == ''):
            print("El jugador no pertenece a las grandes ligas")

        else:

            tablaPartidos = league.find("tbody")

            for partido in tablaPartidos.findAll("tr"):
                listaPartidos.append(partido)

            i = 0

            for infoPartido in listaPartidos[-1].findAll("td"):

                if i == 0:
                    partidoInfo.append(infoPartido.find("a").text.strip())

                elif i == 1:
                    partidoInfo.append(infoPartido.text)

                elif i == 2:
                    if infoPartido.text == 'H':
                        partidoInfo.append('Casa')
                    elif infoPartido.text == 'A':
                        partidoInfo.append('Fuera')

                elif i == 3:
                    partidoInfo.append(infoPartido.find("img")['alt'])

                elif i == 5:
                    partidoInfo.append(infoPartido.find("img")['alt'])

                elif i == 7:
                    partidoInfo.append(infoPartido.text.strip())

                elif i == 8:
                    if len(infoPartido.text) > 5:
                        partidoInfo.append(infoPartido.text.strip())
                        continue
                    else:
                        partidoInfo.append(infoPartido.find("a")['title'])

                elif i == 9:
                    if infoPartido.text == '':
                        partidoInfo.append('0')
                    else:
                        partidoInfo.append(infoPartido.text)

                elif i == 10:
                    if infoPartido.text == '':
                        partidoInfo.append('0')
                    else:
                        partidoInfo.append(infoPartido.text)

                elif i == 11:
                    if infoPartido.text == '':
                        partidoInfo.append('0')
                    else:
                        partidoInfo.append('1')

                elif i == 12:
                    if infoPartido.text == '':
                        partidoInfo.append('0')
                    else:
                        partidoInfo.append('1')

                elif i == 13:
                    if infoPartido.text == '':
                        partidoInfo.append('0')
                    else:
                        partidoInfo.append('1')

                elif i == 14:
                    partidoInfo.append(infoPartido.text.strip("'"))

                i += 1

            listaInfoPartidos.append(partidoInfo)
            i = 0

            jugadoresDB(x, partidoInfo)

            partidosDB(x["nombre"], partidoInfo)
