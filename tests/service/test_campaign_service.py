import unittest
from unittest.mock import Mock
from app.infra.core.campaign import Campaign, DiscountCampaign
from app.infra.core.campaign_service import CampaignService


class TestCampaignService(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = CampaignService(self.repository)

        self.test_campaign = DiscountCampaign(
            id=1,
            discount_percentage=10.0,
            product_id=1
        )

    def test_create_campaign(self):
        self.repository.save.return_value = self.test_campaign

        result = self.service.create_campaign(self.test_campaign)

        self.repository.save.assert_called_once_with(self.test_campaign)
        self.assertEqual(result, self.test_campaign)

    def test_get_campaign(self):
        self.repository.find_by_id.return_value = self.test_campaign

        result = self.service.get_campaign(1)

        self.repository.find_by_id.assert_called_once_with(1)
        self.assertEqual(result, self.test_campaign)

    def test_list_campaigns(self):
        self.repository.find_all.return_value = [self.test_campaign]

        result = self.service.list_campaigns()

        self.repository.find_all.assert_called_once()
        self.assertEqual(result, [self.test_campaign])

    def test_list_active_campaigns(self):
        self.repository.find_active.return_value = [self.test_campaign]

        result = self.service.list_campaigns(active_only=True)

        self.repository.find_active.assert_called_once()
        self.assertEqual(result, [self.test_campaign])

    def test_deactivate_campaign_success(self):
        self.repository.find_by_id.return_value = self.test_campaign

        result = self.service.deactivate_campaign(1)

        self.repository.find_by_id.assert_called_once_with(1)
        self.assertFalse(self.test_campaign.active)
        self.repository.save.assert_called_once_with(self.test_campaign)
        self.assertTrue(result)

    def test_deactivate_campaign_not_found(self):
        self.repository.find_by_id.return_value = None

        result = self.service.deactivate_campaign(999)

        self.repository.find_by_id.assert_called_once_with(999)
        self.repository.save.assert_not_called()
        self.assertFalse(result)

    def test_get_active_campaigns_for_product(self):
        self.repository.find_active_for_product.return_value = [self.test_campaign]

        result = self.service.get_active_campaigns_for_product(1)

        self.repository.find_active_for_product.assert_called_once_with(1)
        self.assertEqual(result, [self.test_campaign])

    def test_get_active_receipt_campaigns(self):
        self.repository.find_active_receipt_campaigns.return_value = [self.test_campaign]

        result = self.service.get_active_receipt_campaigns()

        self.repository.find_active_receipt_campaigns.assert_called_once()
        self.assertEqual(result, [self.test_campaign])


if __name__ == "__main__":
    unittest.main()