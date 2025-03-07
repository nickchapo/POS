import sqlite3
from functools import lru_cache

from fastapi import Depends

from app.core.service.campaign_service import CampaignService

from .sqlite.campaign_repository import CampaignRepository


@lru_cache()
def get_database_connection():
    conn = sqlite3.connect("pos.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_campaign_repository(db_conn=Depends(get_database_connection)):
    return CampaignRepository(db_conn)


def get_campaign_service(repository=Depends(get_campaign_repository)):
    return CampaignService(repository)
