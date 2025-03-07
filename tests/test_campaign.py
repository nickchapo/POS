import unittest
from datetime import datetime, timedelta

from app.core.campaign import (
    BuyNGetNCampaign,
    Campaign,
    CampaignType,
    ComboCampaign,
    DiscountCampaign,
)


class TestCampaign(unittest.TestCase):
    def test_campaign_is_valid_now(self):
        campaign = Campaign(active=True)
        self.assertTrue(campaign.is_valid_now())

    def test_inactive_campaign_is_valid_now(self):
        campaign = Campaign(active=False)
        self.assertFalse(campaign.is_valid_now())

    def test_future_campaigns(self):
        tomorrow = datetime.now() + timedelta(days=1)
        campaign = Campaign(active=True, start_date=tomorrow)
        self.assertFalse(campaign.is_valid_now())

    def test_expired_campaigns(self):
        yesterday = datetime.now() - timedelta(days=1)
        campaign = Campaign(active=True, end_date=yesterday)
        self.assertFalse(campaign.is_valid_now())

    def test_active_campaigns(self):
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)
        campaign = Campaign(active=True, start_date=yesterday, end_date=tomorrow)
        self.assertTrue(campaign.is_valid_now())

    def test_discount_campaign_initialization(self):
        discount_campaign = DiscountCampaign(
            discount_percentage=10.0, product_id=1, min_total=100.0
        )

        self.assertEqual(discount_campaign.campaign_type, CampaignType.DISCOUNT)
        self.assertEqual(discount_campaign.discount_percentage, 10.0)
        self.assertEqual(discount_campaign.product_id, 1)
        self.assertEqual(discount_campaign.min_total, 100.0)
        self.assertTrue(discount_campaign.active)

    def test_buy_n_get_n_campaign_initialization(self):
        buy_n_get_n_campaign = BuyNGetNCampaign(
            product_id=2, buy_quantity=3, free_quantity=1
        )

        self.assertEqual(buy_n_get_n_campaign.campaign_type, CampaignType.BUY_N_GET_N)
        self.assertEqual(buy_n_get_n_campaign.product_id, 2)
        self.assertEqual(buy_n_get_n_campaign.buy_quantity, 3)
        self.assertEqual(buy_n_get_n_campaign.free_quantity, 1)
        self.assertTrue(buy_n_get_n_campaign.active)

    def test_combo_campaign_initialization(self):
        combo_campaign = ComboCampaign(combo_products=[1, 2, 3], combo_discount=15.0)

        self.assertEqual(combo_campaign.campaign_type, CampaignType.COMBO)
        self.assertEqual(combo_campaign.combo_products, [1, 2, 3])
        self.assertEqual(combo_campaign.combo_discount, 15.0)
        self.assertTrue(combo_campaign.active)

    def test_default_empty_list(self):
        combo_campaign = ComboCampaign(combo_discount=15.0)
        self.assertEqual(combo_campaign.combo_products, [])


if __name__ == "__main__":
    unittest.main()
