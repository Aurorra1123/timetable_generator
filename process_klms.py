#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KLMS课程数据处理脚本
将KLMS格式的课程数据转换为课表生成器可识别的格式
"""

import re
import sys

def parse_klms_data(file_path):
    """解析KLMS数据文件"""
    courses = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # 按课程分割（以课程代码开头的行作为分割点）
    course_blocks = re.split(r'\n(?=[A-Z]{4}\d{4})', content)
    
    for block in course_blocks:
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 6:  # 至少需要6行基本信息
            continue
            
        course = parse_single_course(lines)
        if course:
            courses.extend(course)
    
    return courses

def parse_single_course(lines):
    """解析单个课程块"""
    courses = []
    
    # 第一行：课程代码和名称
    course_info = lines[0]
    course_code_match = re.match(r'^([A-Z]{4}\d{4})', course_info)
    if not course_code_match:
        return courses
    
    base_course_code = course_code_match.group(1)
    
    i = 1
    while i < len(lines):
        # 跳过学分信息行
        if lines[i].startswith('[') and 'Credits' in lines[i]:
            i += 1
            continue
            
        # 查找课程section (如 L1, L2, Aerobic Dance I 等)
        section_match = re.match(r'^(.+?)\s*\((\d+)\)$', lines[i])
        if not section_match:
            i += 1
            continue
            
        section_name = section_match.group(1)
        course_id = section_match.group(2)
        
        # 构建完整课程代码
        if section_name.startswith(('L', 'T')):  # 标准格式 L1, T1
            full_course_code = f"{base_course_code}-{section_name}"
        else:  # 体育课等特殊格式
            full_course_code = f"{base_course_code}-{section_name}"
        
        # 查找时间和地点信息
        if i + 3 < len(lines):
            date_range = lines[i + 1]  # 日期范围
            time_info = lines[i + 2]   # 时间信息
            location = lines[i + 3]    # 地点
            instructor = lines[i + 4] if i + 4 < len(lines) else "TBA"
            
            # 解析时间信息
            time_match = re.match(r'^(\w+)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})$', time_info)
            if time_match:
                day = time_match.group(1)
                start_time = time_match.group(2)
                end_time = time_match.group(3)
                
                # 转换日期格式
                day_mapping = {
                    'Mon': 'Mo', 'Tue': 'Tu', 'Wed': 'We', 
                    'Thu': 'Th', 'Fri': 'Fr', 'Sat': 'Sa', 'Sun': 'Su'
                }
                
                if day in day_mapping:
                    formatted_day = day_mapping[day]
                    
                    course_entry = {
                        'code': full_course_code,
                        'id': course_id,
                        'time': f"{formatted_day} {start_time} - {end_time}",
                        'location': location,
                        'instructor': instructor
                    }
                    courses.append(course_entry)
        
        # 跳过当前section的其他信息行（通常是数字）
        i += 1
        while i < len(lines) and (lines[i].isdigit() or lines[i] == 'Pending'):
            i += 1
    
    return courses

def format_for_timetable(courses):
    """将解析后的课程格式化为课表生成器格式"""
    formatted_output = []
    
    for course in courses:
        formatted_course = f"""{course['code']}
({course['id']})
{course['time']}
{course['location']}
{course['instructor']}
3.00"""
        formatted_output.append(formatted_course)
    
    return '\n\n'.join(formatted_output)

def main():
    if len(sys.argv) != 2:
        print("使用方法: python process_klms.py <klms_data_file>")
        print("示例: python process_klms.py klms.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = input_file.replace('.json', '_processed.txt')
    
    try:
        print(f"正在处理文件: {input_file}")
        courses = parse_klms_data(input_file)
        print(f"成功解析 {len(courses)} 门课程")
        
        formatted_output = format_for_timetable(courses)
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        
        print(f"处理完成！输出文件: {output_file}")
        print("\n前5门课程预览:")
        print("=" * 50)
        preview_courses = courses[:5]
        for course in preview_courses:
            print(f"{course['code']}")
            print(f"({course['id']})")
            print(f"{course['time']}")
            print(f"{course['location']}")
            print(f"{course['instructor']}")
            print(f"3.00")
            print()
        
        if len(courses) > 5:
            print(f"... 还有 {len(courses) - 5} 门课程")
            
    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    main()