from fastapi import FastAPI
from loguru import logger
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.api_v1 import api_router as api_v1_router
from tasks.jobs import pdf2mdjob
from core.logging_setup import setup_logging

setup_logging()

scheduler = AsyncIOScheduler()
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动，启动定时任务调度器...")
    scheduler.add_job(pdf2mdjob, 'interval', seconds=10, id='check_records_job')
    scheduler.start()
    yield
    logger.info("应用关闭，关闭定时任务调度器...")
    scheduler.shutdown()


app = FastAPI(
    title="PDF 2 MD",
    lifespan=lifespan,
    version="1.0.0",
    openapi_prefix="/api"
)
app.include_router(api_v1_router)

@app.get("/")
def read_root():
    return {"Hello": "World!"}