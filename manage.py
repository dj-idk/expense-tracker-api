import argparse
import uvicorn


def run(host: str, port: int, reload: bool):
    uvicorn.run("src.web.main:app", host=host, port=port, reload=reload)


def parse_args():
    parser = argparse.ArgumentParser(
        "run", description="Run the FastAPI application with Uvicorn"
    )
    parser.add_argument(
        "--host", type=str, default="localhost", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.host and args.port:
        print(f"Starting server at {args.host}:{args.port} with reload={args.reload}")
        run(host=args.host, port=args.port, reload=args.reload)
    else:
        print("Please provide the host and port.")
