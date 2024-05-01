import numpy as np
from sklearn.preprocessing import MinMaxScaler


class Employee(object):
    def __init__(self,name,able_to_cnt,on_duty_per_week,date_off_duty,plot_preference = {"A":3,"B":3,"C":3,"E":3,"NE":3}):
        self.name = name
        # self.able_to = able_to
        self.able_to_cnt = able_to_cnt
        self.on_duty_per_week = on_duty_per_week
        self.date_off_duty = date_off_duty
        self.plot_preference = plot_preference

        scaler = MinMaxScaler(feature_range=(0.99, 1.01))
        # 辞書の値をnumpy配列に変換
        values = np.array(list(plot_preference.values())).reshape(-1, 1)

        # 値を正規化
        scaled_values = scaler.fit_transform(values)

        # 正規化された値を辞書に戻す
        normalized_dict = dict(zip(plot_preference.keys(), scaled_values.flatten()))

        self.plot_preference_normalized = normalized_dict
        print(self.plot_preference_normalized)

        #休みに幸福度を設定する可能性。別の言い方をすれば、予定より多く勤務することをどの程度嫌うか

    def wish(self,schedule,index):
        return 0