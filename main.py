from typing import Optional

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from sqlmodel import Field, SQLModel, create_engine, Session, select, update, delete

class Post(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    content: str

engine = create_engine("sqlite:///sample.db")

SQLModel.metadata.create_all(engine)

app = FastAPI()

class PostResponse(BaseModel):
    id: int

@app.post("/posts")
def post_posts(post: Post) -> PostResponse:
    with Session(engine) as session:
        session.add(post)
        session.commit()
        session.refresh(post)
        return PostResponse(id=post.id)

@app.get("/posts")
def get_posts() -> list[Post]:
    with Session(engine) as session:
        return session.scalars(select(Post)).all()

@app.get("/posts/{post_id}")
def get_post(post_id: int) -> Post:
    with Session(engine) as session:
        post = session.scalar(select(Post).where(Post.id == post_id))
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

@app.put("/posts/{post_id}")
def put_post(post_id: int, post: Post) -> None:
    with Session(engine) as session:
        affected_rows = session.execute(
            update(Post).where(Post.id == post_id).values({"content": post.content})
        )
        session.commit()
        if affected_rows.rowcount == 0:
            raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}")
def delete_post(post_id: int) -> None:
    with Session(engine) as session:
        affected_rows = session.execute(delete(Post).where(Post.id == post_id))
        session.commit()
        if affected_rows.rowcount == 0:
            raise HTTPException(status_code=404, detail="Post not found")
