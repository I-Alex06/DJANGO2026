from django.http import HttpResponse
import datetime as dt
import re


LUNI = (
    "Ianuarie",
    "Februarie",
    "Martie",
    "Aprilie",
    "Mai",
    "Iunie",
    "Iulie",
    "August",
    "Septembrie",
    "Octombrie",
    "Noiembrie",
    "Decembrie"
)
ZILE = (
    "Luni",
    "Marti",
    "Miercuri",
    "Joi",
    "Vineri",
    "Sambata",
    "Duminica"
)


def formateaza_data_romana(moment, format):
    valori = {
        "a": ZILE[moment.weekday()][:3],
        "A": ZILE[moment.weekday()],
        "b": LUNI[moment.month - 1][:3],
        "B": LUNI[moment.month - 1],
        "d": f"{moment.day:02d}",
        "H": f"{moment.hour:02d}",
        "M": f"{moment.minute:02d}",
        "m": f"{moment.month:02d}",
        "S": f"{moment.second:02d}",
        "Y": f"{moment.year:04d}",
        "y": f"{moment.year % 100:02d}",
    }
    return re.sub(
        r"%([aAbBdHMSmyY])",
        lambda potrivire: valori[potrivire.group(1)],
        format,
    )


class Accesare:

    _urmatorul_id = 1
    FORMAT_DATA_IMPLICIT = "%A, %d %B %Y, %H:%M"

    def __init__(self, ip_client, url, parametri=None):
        self.id = Accesare._urmatorul_id
        Accesare._urmatorul_id += 1
        self.ip_client = ip_client
        self.url = url
        self.parametri = {} if parametri is None else dict(parametri)
        self.data = dt.datetime.now()

    def lista_parametri(self):
        return [(nume, valoare) for nume, valoare in self.parametri.items()]
    def string_url(self):
        return self.url + ("?" + "&".join(f"{nume}={valoare}" for nume, valoare in self.parametri.items()) if self.parametri else "")
    def pagina(self):
        return "/"+self.url.split("?")[0].split("/")[-2]
    def calculeaza_data(self, format=FORMAT_DATA_IMPLICIT,tip=""):
        if tip=="zi":
            return formateaza_data_romana(self.data, "%d %B %Y")
        elif tip=="timp":
            return formateaza_data_romana(self.data, "%H:%M:%S")
        return formateaza_data_romana(self.data, format)
    def __str__(self):
        return f"Id: {self.id}, IP: {self.ip_client}, string_url: {self.string_url()}, pagina: {self.pagina()}, calculeaza_data: {self.calculeaza_data()}, lista_parametri: {self.lista_parametri()}"


def creeaza_accesare(request):
    return Accesare(
        ip_client=request.IP,
        url=request.get_full_path(),
        parametri=request.GET.dict(),
    )

accesari = []

def index(request):
    accesare = creeaza_accesare(request)
    accesari.append(accesare)
    print(accesare)
    return HttpResponse("Un magazin web care vinde jocuri video in format digital si fizic.")


def info(request):
    accesare = creeaza_accesare(request)
    accesari.append(accesare)
    print(accesare)
    tip = request.GET.get("data", "")
    return HttpResponse(
		f"""<!DOCTYPE html>
<html>
<head>
    <title>Informații despre server</title>
</head>
<body>
    <h1>Informații despre server</h1>
    <h2>Data și ora:</h2>
    <p>{accesare.calculeaza_data(tip=tip)}</p>
</body>
</html>"""
	)
    
    
def log(request):
    accesare_originala = creeaza_accesare(request)
    accesari.append(accesare_originala)
    print(accesare_originala)
    
    erori = []
        

    valoare_ultimele = request.GET.get("ultimele")

    if valoare_ultimele is None:
        accesari_afisate = accesari
    else:
        try:
            ultimele = int(valoare_ultimele)
        except ValueError:
            return HttpResponse(
                "Eroare: ultimele nu este o valoare numerica intreaga",
                status=400,
            )

        if ultimele < 0:
            return HttpResponse(
                "Eroare: ultimele nu este pozitiv",
                status=400,
            )

        nr_accesari = len(accesari)

        if ultimele > nr_accesari:
            accesari_afisate = accesari
            erori.append( f"Exista doar {nr_accesari} accesari fata de {ultimele} accesari cerute")
        else:
            accesari_afisate = accesari[-ultimele:] if ultimele else []
    html = "<h1>Accesari</h1><ul>"
    for accesare in accesari_afisate:
            html += f"<li>{accesare}</li>"
    html += "</ul>"
    accesari_afisate = []
    
    iduri = request.GET.getlist("iduri")
    if iduri:
        try:
            iduri_cerute = [int(id_accesare) for valoare in iduri for id_accesare in valoare.split(",") if id_accesare.strip()]
        except ValueError:
            return HttpResponse(
                "Eroare: iduri nu sunt numere intregi",
                status=400,
            )

        dubluri = request.GET.get("dubluri", "false").lower() == "true"
        if not dubluri:
            iduri_cerute = list(dict.fromkeys(iduri_cerute))

        accesari_dupa_id = {accesare.id: accesare for accesare in accesari}
        accesari_afisate = [accesari_dupa_id[id_accesare] for id_accesare in iduri_cerute if id_accesare in accesari_dupa_id]
    
    if accesari_afisate:
        html += "<h2>Accesari dupa id</h2><ul>"
        for accesare in accesari_afisate:
            html += f"<li>{accesare}</li>"
        html += "</ul>"
    
    param_accesari = request.GET.get("accesari")
    if param_accesari == "detalii":
        html += "<h2>Detalii</h2><ul>"
        for accesare in accesari:
            html += "<li>"+str(accesare.id)+" , "+accesare.calculeaza_data()+"</li>"
    if param_accesari=="nr":
        html += f"<h3>Nr accesari: {len(accesari)}</h3>"

    l_param=accesare_originala.lista_parametri()
    html += "<h2>Parametri</h2>"
    html+= "<p>Nr param "+str(len(l_param))+"</p><p>"
    for item in l_param:
        html+= str(item[0])+" , "
    html += "</p>"
    

    

    if len(erori) > 0:
        html += "<h2>Erori</h2><ul>"
        for eroare in erori:
            html += f"<p>{eroare}</p>"

    return HttpResponse(f"<!DOCTYPE html><html><body>{html}</body></html>")