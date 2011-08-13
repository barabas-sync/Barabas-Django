from barabasdjango.webserver import WebServer

class BarabasSessionMiddleware:
    def process_request(self, request):
        """Empty docstring"""
        request.store = WebServer.open_store()
    
    def process_response(self, request, response):
        """Empty docstring"""
        WebServer.close_store()
        return response
    
    def process_exception(self, request, exception):
        """Empty docstring"""
        WebServer.close_store()
        return None
