import requests
from urllib.parse import urlparse, quote, unquote
from bs4 import BeautifulSoup as Soup

class Sholat:
    def __init__(self):
        self.GET = "GET"
        self.POST = "POST"

        self.cookies = None
        self.session = requests.session()
        self.history = None

        self.url_utama = "https://bimasislam.kemenag.go.id/jadwalshalat"
        self.url_kabupaten = "https://bimasislam.kemenag.go.id/ajax/getKabkoshalat"
        self.url_jadwal = "https://bimasislam.kemenag.go.id/ajax/getShalatbln"

        self.history = self.get(self.url_utama)
        self.cookies = self.history.cookies

        self.jadwal = {}
        self.data_daerah = {}
        self.load_daerah()

    def load_daerah(self, *args, **kwargs ):
        html_utama = self.req_html(self.url_utama, *args, **kwargs)
        for el_provinsi in html_utama.find("select", {"id":  "search_prov"}).find_all("option"):
            token_provinsi = el_provinsi.get("value")

            data = {"x": token_provinsi}
            html_kabupaten = self.req_html(self.url_kabupaten, self.POST, data=data)
            if len(html_kabupaten.contents) <= 0 :
                html_kabupaten = self.req_html(self.url_kabupaten, self.POST, data={"x":""})
            
            if len(html_kabupaten.contents) > 0:
                for el_kabupaten in html_kabupaten.find_all("option"):
                    self.data_daerah.update({
                        el_kabupaten.text: {
                            "provinsi": el_provinsi.text,
                            "x": token_provinsi,
                            "y": el_kabupaten.get("value")
                        }
                    })
                 
    def get(self, url, *args, **kwargs):
        return self.session.get(url, *args, **kwargs)
        
    def post(self, url, *args, **kwargs):
        return self.session.post(url, *args, **kwargs)
    
    def req_html(self, url, method="GET" , *args, **kwargs):

        if method == self.GET:

            self.history = self.get(url, *args, **kwargs)
            self.cookies = self.history.cookies
            return Soup(self.history.content.decode("utf-8"), features="lxml")

        elif method == self.POST:

            self.history = self.post(url, *args, **kwargs)
            self.cookies = self.history.cookies
            return Soup(self.history.content.decode("utf-8"), features="lxml")

    def req_json(self, url, method="GET" , *args, **kwargs):

        if method == self.GET:

            self.history = self.get(url, *args, **kwargs)
            self.cookies = self.history.cookies
            return self.history.json()

        elif method == self.POST:

            self.history = self.post(url, *args, **kwargs)
            self.cookies = self.history.cookies
            return self.history.json()

    def cari_kabupaten(self, kata, *args, **kwargs):
        if len(self.data_daerah) <= 0 :
            self.load_daerah(*args, **kwargs)

        result = {}
        if len(kata) <= 0:
            return result
        else:
            for kabupaten, data in self.data_daerah.items():
                if kata.lower() in kabupaten.lower():
                    result.update({kabupaten: data})
            
            return result

    def cari_provinsi(self, kata, *args, **kwargs):
        if len(self.data_daerah) <= 0 :
            self.load_daerah(*args, **kwargs)

        result = {}
        if len(kata) <= 0:
            return result
        else:
            for kabupaten, data in self.data_daerah.items():
                if kata.lower() in data.get("provinsi", "").lower():
                    result.update({
                        kabupaten: data
                    })
            
            return result

    def sebulan(self, nama_kabupaten, tahun, bulan, *args, **kwargs):
        if len(self.data_daerah) <= 0 :
            self.load_daerah(*args, **kwargs)


        if nama_kabupaten in self.data_daerah:
            data = self.data_daerah[nama_kabupaten]

            bulanan_key = f'{nama_kabupaten}-{tahun}-{bulan}'
            if bulanan_key in self.jadwal:
                return self.jadwal[bulanan_key].copy()
            else:
                if "provinsi" in data:
                    data.pop("provinsi")
                bulan = str(bulan).rjust(2, "0")
                data.update({
                    "thn": tahun,
                    "bln": bulan
                })

                json_jadwal = self.req_json(self.url_jadwal, self.POST, data=data)
                if len(json_jadwal) > 3:
                    json_jadwal.pop("status")
                    json_jadwal.pop("message")
                    self.jadwal.update({
                        bulanan_key: json_jadwal
                    })

                    return json_jadwal.copy()
                   
        return {}

    def sehari(self, nama_kabupaten, tahun, bulan, tanggal, *args, **kwargs):
        if len(self.data_daerah) <= 0 :
            self.load_daerah(*args, **kwargs)
        
        bulan = str(bulan).rjust(2, "0")
        tanggal = str(tanggal).rjust(2, "0")

        sebulan = self.sebulan(nama_kabupaten, tahun, bulan, *args, **kwargs)
        if len(sebulan) > 0:
            waktu = f"{str(tahun)}-{str(bulan)}-{str(tanggal)}"
            if waktu in sebulan["data"]:
                sebulan["data"] = {
                    waktu: sebulan["data"].get(waktu)
                }
            
            return sebulan

        return {}
		
