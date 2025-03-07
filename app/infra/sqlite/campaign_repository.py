import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..core.campaign import (Campaign, CampaignType, DiscountCampaign, BuyNGetNCampaign, ComboCampaign)


class CampaignRepository:
    def __init__(self, db_connection):
        self.conn = db_connection
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_type TEXT NOT NULL,
            active BOOLEAN NOT NULL DEFAULT 1,
            start_date TEXT,
            end_date TEXT,
            parameters TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def _campaign_to_row(self, campaign: Campaign) -> Dict[str, Any]:
        parameters = {}

        if isinstance(campaign, DiscountCampaign):
            parameters = {
                "discount_percentage": campaign.discount_percentage,
                "product_id": str(campaign.product_id) if campaign.product_id else None,
                "min_total": campaign.min_total
            }
        elif isinstance(campaign, BuyNGetNCampaign):
            parameters = {
                "product_id": str(campaign.product_id) if campaign.product_id else None,
                "buy_quantity": campaign.buy_quantity,
                "free_quantity": campaign.free_quantity
            }
        elif isinstance(campaign, ComboCampaign):
            parameters = {
                "combo_products": [str(p) for p in campaign.combo_products] if campaign.combo_products else [],
                "combo_discount": campaign.combo_discount
            }

        return {
            "campaign_type": campaign.campaign_type.value,
            "active": 1 if campaign.active else 0,
            "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
            "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
            "parameters": json.dumps(parameters)
        }

    def _row_to_campaign(self, row: Dict[str, Any]) -> Campaign:
        parameters = json.loads(row["parameters"])
        campaign_type = CampaignType(row["campaign_type"])

        base_args = {
            "id": row["id"],
            "active": bool(row["active"]),
            "start_date": datetime.fromisoformat(row["start_date"]) if row["start_date"] else None,
            "end_date": datetime.fromisoformat(row["end_date"]) if row["end_date"] else None,
        }

        if campaign_type == CampaignType.DISCOUNT:
            return DiscountCampaign(
                **base_args,
                discount_percentage=parameters.get("discount_percentage", 0.0),
                product_id=UUID(parameters.get("product_id")) if parameters.get("product_id") else None,
                min_total=parameters.get("min_total")
            )
        elif campaign_type == CampaignType.BUY_N_GET_N:
            return BuyNGetNCampaign(
                **base_args,
                product_id=UUID(parameters.get("product_id")) if parameters.get("product_id") else None,
                buy_quantity=parameters.get("buy_quantity", 0),
                free_quantity=parameters.get("free_quantity", 0)
            )
        elif campaign_type == CampaignType.COMBO:
            return ComboCampaign(
                **base_args,
                combo_products=[UUID(p) for p in parameters.get("combo_products", [])] if parameters.get("combo_products") else [],
                combo_discount=parameters.get("combo_discount", 0.0)
            )

        return None

    def save(self, campaign: Campaign) -> Campaign:
        cursor = self.conn.cursor()
        row = self._campaign_to_row(campaign)

        if campaign.id is None:
            placeholders = ", ".join(["?"] * len(row))
            columns = ", ".join(row.keys())
            values = tuple(row.values())

            cursor.execute(
                f"INSERT INTO campaigns ({columns}) VALUES ({placeholders})",
                values
            )
            campaign.id = cursor.lastrowid
        else:
            set_clause = ", ".join([f"{column} = ?" for column in row.keys()])
            values = tuple(row.values()) + (campaign.id,)

            cursor.execute(
                f"UPDATE campaigns SET {set_clause} WHERE id = ?",
                values
            )

        self.conn.commit()
        return campaign

    def find_by_id(self, campaign_id: int) -> Optional[Campaign]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM campaigns WHERE id = ?",
            (campaign_id,)
        )
        row = cursor.fetchone()

        if row:
            return self._row_to_campaign(dict(row))
        return None

    def find_all(self) -> List[Campaign]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM campaigns")
        rows = cursor.fetchall()

        return [self._row_to_campaign(dict(row)) for row in rows]

    def find_active(self) -> List[Campaign]:
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
        SELECT * FROM campaigns 
        WHERE active = 1
        AND (start_date IS NULL OR start_date <= ?)
        AND (end_date IS NULL OR end_date >= ?)
        """, (now, now))

        rows = cursor.fetchall()
        return [self._row_to_campaign(dict(row)) for row in rows]

    def find_active_for_product(self, product_id: UUID) -> List[Campaign]:
        all_active = self.find_active()
        result = []

        for campaign in all_active:
            if isinstance(campaign, DiscountCampaign) and campaign.product_id == product_id:
                result.append(campaign)
            elif isinstance(campaign, BuyNGetNCampaign) and campaign.product_id == product_id:
                result.append(campaign)
            elif isinstance(campaign, ComboCampaign) and product_id in campaign.combo_products:
                result.append(campaign)

        return result

    def find_active_receipt_campaigns(self) -> List[Campaign]:
        all_active = self.find_active()
        return [c for c in all_active if isinstance(c, DiscountCampaign) and c.min_total is not None]