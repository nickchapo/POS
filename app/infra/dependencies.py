import sqlite3
from fastapi import Depends
from functools import lru_cache

from sqlite.campaign_repository import CampaignRepository
from .core.campaign_service import CampaignService


@lru_cache()
def get_database_connection():
    conn = sqlite3.connect("pos_system.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_campaign_repository(db_conn=Depends(get_database_connection)):
    return CampaignRepository(db_conn)


def get_campaign_service(repository=Depends(get_campaign_repository)):
    return CampaignService(repository)