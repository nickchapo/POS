import json
import sqlite3
import unittest
from datetime import datetime, timedelta
from uuid import UUID

from app.core.campaign import (
    BuyNGetNCampaign,
    CampaignType,
    ComboCampaign,
    DiscountCampaign,
)
from app.infra.sqlite.campaign_repository import CampaignRepository


class TestCampaignRepository(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.repository = CampaignRepository(self.conn)

        self.discount_campaign = DiscountCampaign(
            discount_percentage=10.0,
            product_id=UUID("00000000-0000-0000-0000-000000000001"),
        )

        self.buy_n_get_n_campaign = BuyNGetNCampaign(
            product_id=UUID("00000000-0000-0000-0000-000000000002"),
            buy_quantity=3,
            free_quantity=1,
        )

        self.combo_campaign = ComboCampaign(
            combo_products=[1, 2, 3], combo_discount=15.0
        )

    def tearDown(self):
        self.conn.close()

    def test_save_new_campaign(self):
        result = self.repository.save(self.discount_campaign)

        self.assertIsNotNone(result.id)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (result.id,))
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["campaign_type"], CampaignType.DISCOUNT.value)
        self.assertEqual(row["active"], 1)

        parameters = json.loads(row["parameters"])
        self.assertEqual(parameters["discount_percentage"], 10.0)
        self.assertEqual(
            parameters["product_id"], "00000000-0000-0000-0000-000000000001"
        )

    def test_save_update_campaign(self):
        campaign = self.repository.save(self.discount_campaign)

        campaign.discount_percentage = 20.0
        campaign.active = False

        result = self.repository.save(campaign)

        self.assertEqual(result.id, campaign.id)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (result.id,))
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["active"], 0)

        parameters = json.loads(row["parameters"])
        self.assertEqual(parameters["discount_percentage"], 20.0)

    def test_find_by_id(self):
        saved = self.repository.save(self.buy_n_get_n_campaign)

        found = self.repository.find_by_id(saved.id)

        self.assertEqual(found.id, saved.id)
        self.assertEqual(found.campaign_type, CampaignType.BUY_N_GET_N)
        self.assertEqual(found.product_id, UUID("00000000-0000-0000-0000-000000000002"))
        self.assertEqual(found.buy_quantity, 3)
        self.assertEqual(found.free_quantity, 1)

    def test_find_all(self):
        self.repository.save(self.discount_campaign)
        self.repository.save(self.buy_n_get_n_campaign)

        campaigns = self.repository.find_all()

        self.assertEqual(len(campaigns), 2)
        campaign_types = {c.campaign_type for c in campaigns}
        self.assertEqual(
            campaign_types, {CampaignType.DISCOUNT, CampaignType.BUY_N_GET_N}
        )

    def test_find_active(self):
        active_campaign = self.discount_campaign
        self.repository.save(active_campaign)

        inactive_campaign = self.buy_n_get_n_campaign
        inactive_campaign.active = False
        self.repository.save(inactive_campaign)

        active_campaigns = self.repository.find_active()

        self.assertEqual(len(active_campaigns), 1)
        self.assertEqual(active_campaigns[0].campaign_type, CampaignType.DISCOUNT)

    def test_find_active_with_dates(self):
        yesterday = datetime.now() - timedelta(days=1)
        valid_campaign = self.discount_campaign
        valid_campaign.start_date = yesterday
        self.repository.save(valid_campaign)

        tomorrow = datetime.now() + timedelta(days=1)
        future_campaign = self.buy_n_get_n_campaign
        future_campaign.start_date = tomorrow
        self.repository.save(future_campaign)

        active_campaigns = self.repository.find_active()

        self.assertEqual(len(active_campaigns), 1)
        self.assertEqual(active_campaigns[0].campaign_type, CampaignType.DISCOUNT)

    def test_find_active_for_product(self):
        product_id_1 = UUID("00000000-0000-0000-0000-000000000001")
        product_id_2 = UUID("00000000-0000-0000-0000-000000000002")
        product_id_3 = UUID("00000000-0000-0000-0000-000000000003")

        discount_campaign = DiscountCampaign(
            product_id=product_id_1, discount_percentage=10.0
        )
        self.repository.save(discount_campaign)

        buy_n_get_n_campaign = BuyNGetNCampaign(
            product_id=product_id_2, buy_quantity=3, free_quantity=1
        )
        self.repository.save(buy_n_get_n_campaign)

        combo_campaign = ComboCampaign(
            combo_products=[product_id_1, product_id_3], combo_discount=15.0
        )
        self.repository.save(combo_campaign)

        campaigns = self.repository.find_active_for_product(product_id_1)

        self.assertEqual(len(campaigns), 2)
