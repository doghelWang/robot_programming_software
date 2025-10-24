import openpyxl
import re

def test_can_logic():
    """测试CAN接口逻辑"""
    print("测试CAN接口逻辑...")
    
    # 模拟Excel数据结构
    # 根据之前的分析，第13行的CAN信息应该属于202904335单板
    # 但实际应该从第15行开始才是202904335单板的开始
    
    # 模拟单板识别逻辑
    boards = []
    
    # 模拟第4行：202903931单板
    board4 = {
        '序号': 4,
        '单板型号': '202903931',
        'start_row': 4,
        'can_start_row': max(1, 4 - 3),  # 1
        'can_end_row': 4 + 30,  # 34
        'can_info': None
    }
    boards.append(board4)
    
    # 模拟第15行：202904335单板
    board15 = {
        '序号': 15,
        '单板型号': '202904335',
        'start_row': 15,
        'can_start_row': max(1, 15 - 3),  # 12
        'can_end_row': 15 + 30,  # 45
        'can_info': None
    }
    boards.append(board15)
    
    # 模拟第13行的CAN信息
    can_row_13 = {
        'row': 13,
        'p_value': '接入RCU_uCAN',
        'is_can': True
    }
    
    # 模拟第15行的CAN信息
    can_row_15 = {
        'row': 15,
        'p_value': '车后急停',
        'is_can': False
    }
    
    # 模拟第75行的CAN信息
    can_row_75 = {
        'row': 75,
        'p_value': '接入RCU_CANOPEN',
        'is_can': True
    }
    
    print(f"单板4 (202903931) - CAN查找范围: {board4['can_start_row']}-{board4['can_end_row']}")
    print(f"单板15 (202904335) - CAN查找范围: {board15['can_start_row']}-{board15['can_end_row']}")
    
    print(f"行13 (CAN信息): {can_row_13}")
    print(f"行15 (非CAN): {can_row_15}")
    print(f"行75 (CAN信息): {can_row_75}")
    
    # 测试逻辑：行13应该属于单板4的查找范围(1-34)，但不应该被记录为单板15的CAN信息
    # 行75应该属于单板15的查找范围(12-45)，但行号超出范围
    
    print("\n测试结果:")
    print("行13的CAN信息应该被记录为单板4的CAN信息（如果在范围1-34内）")
    print("行75的CAN信息应该被记录为单板15的CAN信息（如果在范围12-45内）")
    
    # 修复后的逻辑：只在单板自己的查找范围内记录CAN信息
    print("\n修复后的逻辑：")
    print("- 单板4的CAN查找范围：1-34")
    print("- 单板15的CAN查找范围：12-45")
    print("- 行13在单板4的查找范围内，但应该只记录在单板4的can_info中")
    print("- 行75不在单板15的查找范围内，不应该被记录")

if __name__ == "__main__":
    test_can_logic()
