class FinalPriceCalculator:
    @staticmethod
    def calculate(
        listed_price: int,
        coupon_discount: int = 0,
        bank_discount: int = 0,
        exchange_bonus: int = 0,
        delivery_charge: int = 0
    ) -> int:
        """
        Calculates final price:
        final_price = listed_price - coupon_discount - bank_discount - exchange_bonus + delivery_charge
        Ensures final price is never below 0.
        """
        final_price = listed_price - coupon_discount - bank_discount - exchange_bonus + delivery_charge
        return max(0, final_price)
