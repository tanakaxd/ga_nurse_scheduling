class Employee(object):
    def __init__(self,name,able_to,on_duty_per_week,date_off_duty,plot_preference = {"A":3,"B":3,"C":3,"E":3,"NE":3}):
        self.name = name
        self.able_to = able_to
        self.on_duty_per_week = on_duty_per_week
        self.date_off_duty = date_off_duty
        self.plot_preference = plot_preference
        total = sum(self.plot_preference.values())
        self.plot_preference_normalized = {k: v/total for k,v in self.plot_preference.items()}
        #休みに幸福度を設定する可能性