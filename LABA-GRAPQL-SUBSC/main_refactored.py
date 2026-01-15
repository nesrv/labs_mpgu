from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from src.schema import schema
from pubsub import PubSubManager

pubsub = PubSubManager()

graphql_app = GraphQLRouter(
    schema,
    graphql_ide="graphiql",
)

app = FastAPI(
    title="Messenger Channel API",
    description="GraphQL API для информационного канала мессенджера",
    version="1.0.0",
)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "API доступен",
        "graphql": "/graphql",
        "graphql_playground": "/graphql (откройте в браузере)",
        "swagger": "/docs",
        "redoc": "/redoc",
    }

@app.get("/info")
async def info():
    return {
        "graphql_endpoint": "/graphql",
        "graphql_playground": "Откройте /graphql в браузере для интерактивного тестирования",
        "swagger_ui": "/docs - только для REST эндпоинтов",
        "note": "GraphQL запросы тестируются через GraphQL Playground, а не Swagger",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)