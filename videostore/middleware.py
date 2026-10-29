class MiddlewareIp:
    def __init__(self, get_response):
        self.get_response = get_response
    def get_ip(self, request):
        req_headers = request.META
        str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if str_lista_ip:
            return str_lista_ip.split(',')[-1].strip()
        else:
            return request.META.get('REMOTE_ADDR')

    def __call__(self, request):
        request.IP = self.get_ip(request)
        # se apelează indirect funcția de vizualizare (din views.py)
        response = self.get_response(request)      

        
        return response
