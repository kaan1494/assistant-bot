"""
Minimal availability checker used by app.py.
"""


class SmartAvailabilityChecker:
    def check_availability(self, user_id, query):
        return "📅 Şu anda bu tarih için kayıtlı bir yoğunluk görünmüyor."


availability_checker = SmartAvailabilityChecker()
