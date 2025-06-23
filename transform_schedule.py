import csv
import json
from datetime import datetime
from inverse_transform_schedule import perfect_inverse_transform_improved, validate_schedule_restoration, inverse_transform_schedule

def transform_schedule_with_metadata(input_file, save_metadata=True):
    """
    メタデータ保存機能付きスケジュール変換
    """
    # Initialize the output list
    output = []
    metadata = {
        'original_file': input_file,
        'headers': [],
        'staff_columns': [],
        'rows_data': [],
        'transformation_date': datetime.now().isoformat()
    }
    
    # Read the CSV file
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read headers manually
        metadata['headers'] = list(headers)
        
        # Identify staff columns (excluding meta columns)
        staff_cols = [col for col in headers if col not in ['日付', '曜日', '備考', 'cnt', 'vld', 'メガネ'] and col.strip()]
        metadata['staff_columns'] = staff_cols
        
        # Process each row
        row_index = 0
        for raw_row in reader:
            if len(raw_row) < 2 or not raw_row[1].strip():  # Stop if no weekday
                break
                
            # Convert row to dictionary for easier access
            row = {}
            for i, header in enumerate(headers):
                if i < len(raw_row):
                    row[header] = raw_row[i]
                else:
                    row[header] = ''
                
            # Save complete row metadata
            row_metadata = {
                'row_index': row_index,
                'date': row.get('日付', ''),
                'weekday': row.get('曜日', ''),
                'staff_data': {},
                'meta_data': {
                    'remark': row.get('備考', ''),
                    'cnt': row.get('cnt', ''),
                    'vld': row.get('vld', ''),
                    'megane': row.get('メガネ', '')
                }
            }
            
            day_schedule = []
            
            for i, staff in enumerate(staff_cols):
                # Get both shift value and priority (next column)
                shift_value = row.get(staff, '').strip()
                
                # Get priority value from next column if it exists
                staff_col_idx = headers.index(staff)
                priority_col_idx = staff_col_idx + 1
                priority_value = ''
                if priority_col_idx < len(raw_row):
                    priority_value = raw_row[priority_col_idx].strip()
                
                # Store original values
                row_metadata['staff_data'][staff] = {
                    'original_shift': shift_value,
                    'priority': priority_value,
                    'column_index': i
                }
                
                # Convert for GA processing
                if shift_value == '休' or shift_value == '':
                    day_schedule.append('R')
                elif shift_value == 'C/D':
                    day_schedule.append('C')
                else:
                    day_schedule.append(shift_value)
            
            metadata['rows_data'].append(row_metadata)
            output.append(','.join(day_schedule))
            row_index += 1
    
    # Save metadata to JSON file if requested
    if save_metadata:
        metadata_file = input_file.replace('.csv', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"メタデータ保存: {metadata_file}")
    
    # Return the transformed data and metadata
    return output, metadata

# 逆変換機能はinverse_transform_schedule.pyからインポート

def transform_schedule(input_file):
    """
    従来の変換関数（後方互換性のため保持）
    """
    result, _ = transform_schedule_with_metadata(input_file, save_metadata=False)
    return result

# Example usage
if __name__ == "__main__":
    # メタデータ付き正変換のテスト
    input_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB.csv"
    output_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB_with_metadata.csv"
    
    print("=== メタデータ付き正変換テスト ===")
    try:
        result, metadata = transform_schedule_with_metadata(input_file, save_metadata=True)
        
        # Write to CSV file
        with open(output_file, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            # Write each line as a row
            for line in result:
                writer.writerow(line.split(','))
        
        print(f"正変換完了: {output_file}")
        print(f"メタデータ保存: {len(metadata['rows_data'])}行分")
        print(f"変換結果（最初の3行）:")
        for i, line in enumerate(result[:3]):
            print(f"  {i+1}: {line}")
    except Exception as e:
        print(f"正変換エラー: {e}")
    
    # # 改善された完全復元テスト
    # print("\n=== 改善された完全復元テスト ===")
    # try:
    #     # メタデータの読み込み
    #     with open("/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB_metadata.json", 'r', encoding='utf-8') as f:
    #         metadata = json.load(f)
        
    #     restored_data = perfect_inverse_transform_improved(
    #         output_file,
    #         metadata_file="/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB_metadata.json"
    #     )
    #     print("改善された完全復元テスト完了")
        
    #     # バリデーション実行
    #     validation_errors = validate_schedule_restoration(restored_data, metadata)
    #     if validation_errors:
    #         print("バリデーションエラー:")
    #         for error in validation_errors[:5]:  # 最初の5つのエラーだけ表示
    #             print(f"  - {error}")
    #         if len(validation_errors) > 5:
    #             print(f"  ... 他{len(validation_errors)-5}件のエラー")
    #     else:
    #         print("バリデーション: 全てのチェックをパス")
        
    #     # 復元データの検証
    #     print("復元データの最初の行（ヘッダー）:")
    #     print(restored_data[0][:10])  # 最初の10列だけ表示
    #     print("復元データの2行目:")
    #     print(restored_data[1][:10])  # 最初の10列だけ表示
        
    # except Exception as e:
    #     print(f"改善された完全復元エラー: {e}")
    
    # # 従来の逆変換との比較
    # print("\n=== 従来の逆変換との比較 ===")
    # try:
    #     staff_names = ['大場', '渡辺', '村岡', '志村', '田中', '松本', '久保', '渡辺（社', '山城', '真渕']
    #     old_result = inverse_transform_schedule(
    #         output_file, 
    #         staff_names=staff_names, 
    #         start_date="2024-07-01"
    #     )
    #     print("従来の逆変換も正常動作")
    # except Exception as e:
    #     print(f"従来の逆変換エラー: {e}")