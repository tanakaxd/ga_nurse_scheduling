from employee import Employee


class Shimura(Employee):
    def __init__(self, *, name, able_to, on_duty_per_week, date_off_duty, plot_preference={"A":3,"B":3,"C":3,"E":3,"NE":3}):
        super().__init__(name=name, able_to_cnt=able_to, on_duty_per_week=on_duty_per_week, date_off_duty=date_off_duty, plot_preference=plot_preference)

    def wish(self, *, schedule, index):
        # 連休に対してマイナス評価を加える
        temp_fitness = 0
        for i in range(len(schedule.days)-1):
            if schedule.days[i].cells[index]=="R" and schedule.days[i+1].cells[index]=="R":
                temp_fitness -= 10
        return temp_fitness