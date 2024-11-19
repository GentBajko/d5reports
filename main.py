import uvicorn

from config.env import ENV

if __name__ == "__main__":
    uvicorn.run(
        "backend.server:app",
        host=ENV.API_HOST,
        port=ENV.API_PORT,
        reload=ENV.ENV == "dev",
    )
