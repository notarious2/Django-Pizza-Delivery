from django.test import TestCase
from order.forms import CouponApplyForm


class TestCouponApplyForm(TestCase):
    """Test user Coupon apply form"""

    def test_coupon_apply_valid_data(self):
        """Test coupon apply form with valid data"""
        form = CouponApplyForm({"code": "TestCode"})
        self.assertTrue(form.is_valid())

    def test_coupon_apply_invalid_data(self):
        """Test coupon apply form with invalid data"""
        form = CouponApplyForm(
            {"code": "TestCodeTestCodeTestCodeTestCodeTestCodeTestCodeTestCode"}
        )
        self.assertFalse(form.is_valid())
