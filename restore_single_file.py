#!/usr/bin/env python3
"""
単一ファイルの逆変換用スクリプト
使用例: python restore_single_file.py data/output/schedule_2025July_3.csv
"""

import sys
import json
from inverse_transform_schedule import perfect_inverse_transform_improved, validate_schedule_restoration

def restore_file(*, input_file, metadata_file=None):
    """
    指定されたファイルを逆変換する
    """
    if metadata_file is None:
        # デフォルトのメタデータファイルを使用
        metadata_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB_metadata.json"
    
    print(f"🔄 逆変換開始...")
    print(f"📁 入力ファイル: {input_file}")
    print(f"📋 メタデータ: {metadata_file}")
    
    try:
        # 逆変換実行
        restored_data = perfect_inverse_transform_improved(
            input_file=input_file,
            metadata_file=metadata_file
        )
        
        # バリデーション
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        errors = validate_schedule_restoration(restored_data=restored_data, metadata=metadata)
        
        if errors:
            print("⚠️  バリデーションエラー:")
            for error in errors[:5]:
                print(f"     - {error}")
            if len(errors) > 5:
                print(f"     ... 他{len(errors)-5}件のエラー")
        else:
            print("✅ 復元成功！全てのバリデーションをパス")
        
        # 出力ファイル名を表示
        output_file = input_file.replace('.csv', '_perfectly_restored.csv')
        print(f"💾 出力ファイル: {output_file}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ ファイルが見つかりません: {e}")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python restore_single_file.py <GAで最適化されたCSVファイル> [メタデータファイル]")
        print("例: python restore_single_file.py data/output/schedule_2025July_3.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    metadata_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = restore_file(input_file=input_file, metadata_file=metadata_file)
    sys.exit(0 if success else 1)