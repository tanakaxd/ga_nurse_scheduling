import csv
import json
import random
from datetime import datetime, timedelta

def perfect_inverse_transform_improved(*, input_file, metadata_file=None, output_file=None):
    """
    メタデータを使用した完全復元（改善版）
    GAで最適化された清掃区画割り当てに基づいてメガネ番号を適切に割り当て
    
    Args:
        input_file: GA最適化済みCSVファイル
        metadata_file: メタデータJSONファイル（Noneの場合は自動推定）
        output_file: 出力ファイル（Noneの場合は自動生成）
    
    Returns:
        復元されたデータのリスト
    """
    # メタデータファイルの推定
    if metadata_file is None:
        metadata_file = input_file.replace('.csv', '_metadata.json').replace('_transformed', '')
        if not metadata_file.endswith('_metadata.json'):
            metadata_file = input_file.replace('.csv', '_metadata.json')
    
    # メタデータの読み込み
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"メタデータファイルが見つかりません: {metadata_file}")
    
    # 変換済みCSVの読み込み
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        transformed_data = list(reader)
    
    # 出力ファイル名の設定
    if output_file is None:
        output_file = input_file.replace('.csv', '_perfectly_restored.csv')
    
    # 完全復元の実行
    output_data = []
    
    # ヘッダー行の復元
    output_data.append(metadata['headers'])
    
    # 各行の復元
    for row_idx, transformed_row in enumerate(transformed_data):
        if row_idx >= len(metadata['rows_data']):
            break
            
        row_meta = metadata['rows_data'][row_idx]
        restored_row = [''] * len(metadata['headers'])
        
        # 日付と曜日の復元
        if '日付' in metadata['headers']:
            restored_row[metadata['headers'].index('日付')] = row_meta['date']
        if '曜日' in metadata['headers']:
            restored_row[metadata['headers'].index('曜日')] = row_meta['weekday']
        
        # 働いているスタッフの特定と清掃区画の復元
        working_staff = []
        for staff_name, staff_info in row_meta['staff_data'].items():
            if staff_name in metadata['headers']:
                staff_col_idx = metadata['headers'].index(staff_name)
                
                # GAで最適化された新しい清掃区画を取得
                transformed_col_idx = staff_info['column_index']
                if transformed_col_idx < len(transformed_row):
                    current_value = transformed_row[transformed_col_idx]
                    
                    # 逆変換ルール適用（清掃区画の復元）
                    if current_value == 'R':
                        if staff_info['original_shift'] == '':
                            restored_shift = ''
                        else:
                            restored_shift = '休'
                    elif current_value == 'C':
                        restored_shift = 'C/D'
                    else:
                        restored_shift = current_value
                    
                    # 清掃区画の設定（GAで最適化された新しい値を使用）
                    restored_row[staff_col_idx] = restored_shift
                    
                    # 働いているスタッフのリスト作成
                    if restored_shift not in ['', '休']:
                        working_staff.append({
                            'name': staff_name,
                            'col_idx': staff_col_idx,
                            'original_megane': staff_info.get('priority', '')
                        })
        
        # メガネコーナー割当の復元（働いているスタッフに1-5を割り当て）
        if working_staff:
            # 元の清掃割当と新しい清掃割当を比較
            original_assignments = {}
            new_assignments = {}
            
            for staff in working_staff:
                staff_name = staff['name']
                # 元の清掃割当を取得
                original_assignments[staff_name] = row_meta['staff_data'][staff_name].get('original_shift', '')
                # 新しい清掃割当を取得
                new_assignments[staff_name] = restored_row[staff['col_idx']]
            
            # 割当が変更されたかチェック
            assignments_changed = original_assignments != new_assignments
            
            if not assignments_changed:
                # 割当が変更されていない場合：元のメガネ番号を保持
                for staff in working_staff:
                    if staff['original_megane'].isdigit():
                        megane_col_idx = staff['col_idx'] + 1
                        if megane_col_idx < len(metadata['headers']):
                            restored_row[megane_col_idx] = staff['original_megane']
            else:
                # 割当が変更された場合：ランダムに割り当て
                available_numbers = list(range(1, 6))
                random.shuffle(available_numbers)  # ランダムに並び替え
                
                for i, staff in enumerate(working_staff):
                    megane_col_idx = staff['col_idx'] + 1
                    if megane_col_idx < len(metadata['headers']) and i < len(available_numbers):
                        restored_row[megane_col_idx] = str(available_numbers[i])
        
        # 休んでいるスタッフのメガネ割当は空にする
        for staff_name, staff_info in row_meta['staff_data'].items():
            if staff_name in metadata['headers']:
                staff_col_idx = metadata['headers'].index(staff_name)
                megane_col_idx = staff_col_idx + 1
                if megane_col_idx < len(metadata['headers']):
                    if restored_row[staff_col_idx] in ['', '休'] and restored_row[megane_col_idx] == '':
                        restored_row[megane_col_idx] = ''
        
        # メタデータ列の復元
        meta_data = row_meta['meta_data']
        for meta_key, header_name in [('remark', '備考'), ('cnt', 'cnt'), ('vld', 'vld'), ('megane', 'メガネ')]:
            if header_name in metadata['headers']:
                restored_row[metadata['headers'].index(header_name)] = meta_data.get(meta_key, '')
        
        output_data.append(restored_row)
    
    # CSVファイルに書き込み
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(output_data)
    
    print(f"改善された完全復元完了: {output_file}")
    return output_data

def validate_schedule_restoration(*, restored_data, metadata):
    """
    復元されたスケジュールのバリデーション
    
    Args:
        restored_data: 復元されたスケジュールデータ
        metadata: 元のメタデータ
    
    Returns:
        バリデーションエラーのリスト
    """
    validation_errors = []
    
    for row_idx, row in enumerate(restored_data[1:], 1):  # ヘッダー行をスキップ
        if row_idx > len(metadata['rows_data']):
            break
            
        # 働いているスタッフの特定
        working_staff = []
        megane_assignments = []
        
        for staff_name in metadata['staff_columns']:
            if staff_name in metadata['headers']:
                staff_col_idx = metadata['headers'].index(staff_name)
                if staff_col_idx < len(row):
                    shift = row[staff_col_idx]
                    megane_col_idx = staff_col_idx + 1
                    megane = row[megane_col_idx] if megane_col_idx < len(row) else ''
                    
                    if shift not in ['', '休']:
                        working_staff.append(staff_name)
                        if megane.isdigit():
                            megane_assignments.append(megane)
        
        # バリデーションチェック
        # 1. 働いているスタッフ全員にメガネ番号が割り当てられているか
        if len(working_staff) != len(megane_assignments):
            validation_errors.append(f"行{row_idx}: 働いているスタッフ数({len(working_staff)})とメガネ割当数({len(megane_assignments)})が一致しません")
        
        # 2. メガネ番号の重複チェック
        if len(megane_assignments) != len(set(megane_assignments)):
            validation_errors.append(f"行{row_idx}: メガネ番号に重複があります: {megane_assignments}")
        
        # 3. メガネ番号が1-5の範囲内か
        for megane in megane_assignments:
            if not (1 <= int(megane) <= 5):
                validation_errors.append(f"行{row_idx}: 無効なメガネ番号: {megane}")
    
    return validation_errors

def inverse_transform_schedule(*, input_file, staff_names=None, start_date=None, output_file=None):
    """
    逆変換: 簡略化されたCSVから元の日本語表形式に戻す（従来版）
    メタデータを使わずに推定で復元する簡易版
    
    Args:
        input_file: 変換済みCSVファイルのパス
        staff_names: スタッフ名のリスト（Noneの場合はデフォルト名を使用）
        start_date: 開始日（'YYYY-MM-DD'形式、Noneの場合は当月1日）
        output_file: 出力ファイルパス（Noneの場合は元ファイル名_reversed.csvを使用）
    
    Returns:
        逆変換されたデータのリスト
    """
    
    # デフォルトのスタッフ名（constants.pyから取得したもの）
    if staff_names is None:
        staff_names = ['大場', '渡辺', '村岡', '志村', '田中', '松本', '久保', '渡辺（社', '山城', '真渕']
    
    # 開始日の設定
    if start_date is None:
        # 当月の1日を設定
        today = datetime.now()
        start_date = f"{today.year}-{today.month:02d}-01"
    
    # 曜日名の日本語表記
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    
    # 出力ファイル名の設定
    if output_file is None:
        output_file = input_file.replace('.csv', '_reversed.csv')
    
    # 変換済みCSVファイルを読み込み
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        schedule_data = list(reader)
    
    # 出力データの準備
    output_data = []
    
    # ヘッダー行の作成
    header = ['日付', '曜日']
    for staff in staff_names:
        header.extend([staff, ''])  # スタッフ名の後に空列を追加
    header.extend(['備考', 'cnt', 'vld', 'メガネ'])
    output_data.append(header)
    
    # 各日のデータを処理
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    
    for day_idx, day_schedule in enumerate(schedule_data):
        current_date = start_dt + timedelta(days=day_idx)
        
        # 日付と曜日
        date_str = str(current_date.day)
        weekday_str = weekdays[current_date.weekday()]
        
        row = [date_str, weekday_str]
        
        # 各スタッフのシフトを変換
        shift_count = 0
        for staff_idx, shift in enumerate(day_schedule):
            if staff_idx < len(staff_names):
                # 逆変換ルール
                if shift == 'R':
                    display_shift = '休'
                    priority = ''
                elif shift == 'C':
                    display_shift = 'C/D'
                    priority = '4'  # デフォルト優先度
                    shift_count += 1
                elif shift in ['A', 'B', 'E', 'NE']:
                    display_shift = shift
                    # 優先度をシフトタイプに基づいて設定
                    priority_map = {'A': '1', 'B': '3', 'E': '5', 'NE': '2'}
                    priority = priority_map.get(shift, '1')
                    shift_count += 1
                else:
                    display_shift = shift
                    priority = '1'
                    shift_count += 1
                
                row.extend([display_shift, priority])
        
        # 不足分を空で埋める
        while len(row) < 2 + len(staff_names) * 2:
            row.extend(['', ''])
        
        # 備考、cnt、vld、メガネの列
        is_valid = shift_count == 5  # 5人勤務の場合有効
        cnt_value = shift_count if shift_count > 0 else 0
        vld_value = 5 if is_valid else -1
        megane_value = 'TRUE' if is_valid else 'FALSE'
        
        row.extend(['', str(cnt_value), str(vld_value), megane_value])
        
        output_data.append(row)
    
    # CSVファイルに書き込み
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(output_data)
    
    print(f"逆変換完了: {output_file}")
    return output_data

# Example usage
if __name__ == "__main__":
    # 改善された完全復元テスト
    print("=== inverse_transform_schedule.py テスト ===")
    
    input_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/output/schedule_2025July_3.csv"
    metadata_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB_metadata.json"
    
    try:
        # メタデータの読み込み
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 改善された完全復元
        restored_data = perfect_inverse_transform_improved(input_file=input_file, metadata_file=metadata_file)
        
        # バリデーション実行
        validation_errors = validate_schedule_restoration(restored_data=restored_data, metadata=metadata)
        if validation_errors:
            print("バリデーションエラー:")
            for error in validation_errors[:3]:  # 最初の3つだけ表示
                print(f"  - {error}")
            if len(validation_errors) > 3:
                print(f"  ... 他{len(validation_errors)-3}件のエラー")
        else:
            print("バリデーション: 全てのチェックをパス")
        
        print("inverse_transform_schedule.py テスト完了")
        
    except Exception as e:
        print(f"テストエラー: {e}")