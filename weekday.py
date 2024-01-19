from enum import Enum

class Weekday(Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

    @staticmethod
    def value_of_weekday_from_date(starting_weekday_of_month, date):
        return (date % 7 + starting_weekday_of_month.value - 1) % 7
    
    @staticmethod
    def weekday_from_date(starting_weekday_of_month, date):
        value = (date % 7 + starting_weekday_of_month.value - 1) % 7
        return Weekday(value)
    
# print(Weekday.value_of_weekday_from_date(Weekday.MONDAY,19))
# print(Weekday.value_of_weekday_from_date(Weekday.MONDAY,3))
# print(Weekday.value_of_weekday_from_date(Weekday.THURSDAY,19))
# print(Weekday.weekday_from_date(Weekday.THURSDAY,19))
# print(Weekday.weekday_from_date(Weekday.MONDAY,19))
# print(Weekday.weekday_from_date(Weekday.MONDAY,3))
# print(Weekday.weekday_from_date(Weekday.THURSDAY,19))
