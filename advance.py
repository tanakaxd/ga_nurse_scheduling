from employee import Employee


class Advance(Employee):
    def __init__(self,name,able_to,on_duty_per_week,date_off_duty,plot_preference = {"A":3,"B":3,"C":3,"E":3,"NE":3}):
        super().__init__(name,able_to,on_duty_per_week,date_off_duty,plot_preference)
