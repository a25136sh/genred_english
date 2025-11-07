from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import Problem

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/problems")
async def get_problems(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Problem)
        .order_by(Problem.created_at.desc())
        .limit(30)
    )
    problems = result.scalars().all()

    return {
        "problems": [
            {
                "id": problem.id,
                "genre_id": problem.genre_id,
                "text": problem.text,
                "answer_file_path": problem.answer_file_path,
                "created_at": problem.created_at.isoformat() if problem.created_at else None,
            }
            for problem in problems
        ]
    }
