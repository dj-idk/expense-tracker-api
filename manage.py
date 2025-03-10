import argparse
import uvicorn
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.data import AsyncSessionLocal
from src.utils.seed import seed_expenses


def runserver(host: str, port: int, reload: bool):
    """Runs the FastAPI application with Uvicorn."""
    print(f"Starting server at {host}:{port} with reload={reload}")
    uvicorn.run("src.web.main:app", host=host, port=port, reload=reload)


async def seed_fake_expenses(expenses: int):
    """Creates a new database session and seeds expenses."""
    async with AsyncSessionLocal() as db:
        await seed_expenses(db, num_expenses=expenses)


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Manage the FastAPI application")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # runserver command
    run_parser = subparsers.add_parser("runserver", help="Run the FastAPI application")
    run_parser.add_argument(
        "--host", type=str, default="localhost", help="Host to bind the server to"
    )
    run_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    run_parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    # seed command
    seed_parser = subparsers.add_parser(
        "seed", help="Seed the database with fake expenses"
    )
    seed_parser.add_argument(
        "--expense", type=int, default=100, help="Number of expenses to seed"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.command == "runserver":
        runserver(host=args.host, port=args.port, reload=args.reload)
    elif args.command == "seed":
        print(f"Seeding {args.expense} expenses...")
        asyncio.run(seed_fake_expenses(args.expense))
