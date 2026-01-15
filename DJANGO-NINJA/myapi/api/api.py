from ninja import NinjaAPI
from django.http import JsonResponse

api = NinjaAPI()

@api.get("/hello")
def hello(request, name: str = "World"):
    return {"message": f"Hello {name}!"}