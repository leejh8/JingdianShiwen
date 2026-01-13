import os
import sys
import difflib

# -------------------------------------------------------------------------
# 설정 및 색상 상수 정의
# -------------------------------------------------------------------------
COLOR_HIGHLIGHT = '\033[38;2;206;145;120m' # #CE9178 (살구색 계열)
COLOR_RESET = '\033[0m'
COLOR_GREEN = '\033[92m'
COLOR_CYAN = '\033[96m'
COLOR_YELLOW = '\033[93m'

def get_highlighted_diff(str_a, str_b):
    """두 문자열을 비교하여 차이점을 하이라이트 색상으로 반환"""
    matcher = difflib.SequenceMatcher(None, str_a, str_b)
    out_a, out_b = [], []
    
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == 'equal':
            out_a.append(str_a[a0:a1])
            out_b.append(str_b[b0:b1])
        elif opcode == 'replace':
            out_a.append(f"{COLOR_HIGHLIGHT}{str_a[a0:a1]}{COLOR_RESET}")
            out_b.append(f"{COLOR_HIGHLIGHT}{str_b[b0:b1]}{COLOR_RESET}")
        elif opcode == 'delete':
            out_a.append(f"{COLOR_HIGHLIGHT}{str_a[a0:a1]}{COLOR_RESET}")
        elif opcode == 'insert':
            out_b.append(f"{COLOR_HIGHLIGHT}{str_b[b0:b1]}{COLOR_RESET}")
            
    return "".join(out_a), "".join(out_b)

def count_lines(filepath):
    """파일의 라인 수를 세어 반환"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

def main():
    print("=== 텍스트 교감(Jiaokan) 프로그램 (이어하기 기능 포함) ===")
    
    # 1. 파일 이름 입력
    file_a_name = input("파일 A의 이름을 입력하세요: ").strip()
    file_b_name = input("파일 B의 이름을 입력하세요: ").strip()

    if not os.path.exists(file_a_name) or not os.path.exists(file_b_name):
        print("오류: 입력한 파일을 찾을 수 없습니다.")
        return

    # 2. 결과 파일 이름 생성
    base_name, ext = os.path.splitext(file_a_name)
    file_c_name = f"{base_name}_jiaokan{ext}"
    
    # 3. 이어하기 여부 확인
    start_line_index = 0
    file_mode = 'w' # 기본은 쓰기 모드

    if os.path.exists(file_c_name):
        print(f"\n{COLOR_YELLOW}[알림] 기존 작업 파일({file_c_name})이 존재합니다.{COLOR_RESET}")
        existing_lines = count_lines(file_c_name)
        
        if existing_lines > 0:
            print(f"현재 {existing_lines}행까지 작업되어 있습니다.")
            print(f"{COLOR_GREEN}>> {existing_lines + 1}행부터 작업을 이어합니다.{COLOR_RESET}\n")
            start_line_index = existing_lines
            file_mode = 'a' # 이어쓰기(append) 모드
        else:
            print("파일은 존재하지만 내용이 비어있습니다. 처음부터 시작합니다.\n")

    try:
        # 파일 열기 (결과 파일은 상황에 따라 'w' 혹은 'a')
        with open(file_a_name, 'r', encoding='utf-8') as fa, \
             open(file_b_name, 'r', encoding='utf-8') as fb, \
             open(file_c_name, file_mode, encoding='utf-8', buffering=1) as fc: 
             # buffering=1 : 라인 단위로 버퍼링 (비정상 종료 시 데이터 보존율 높임)
            
            lines_a = fa.readlines()
            lines_b = fb.readlines()
            
            # 작업해야 할 전체 라인 수 확인
            total_lines = min(len(lines_a), len(lines_b))
            
            # 이미 작업한 분량 이후부터 슬라이싱
            lines_to_process = zip(lines_a[start_line_index:], lines_b[start_line_index:])
            
            # enumerate 시작 번호를 (기존 작업량 + 1)로 설정
            for idx, (line_a_raw, line_b_raw) in enumerate(lines_to_process, start_line_index + 1):
                
                line_a = line_a_raw.rstrip('\n')
                line_b = line_b_raw.rstrip('\n')

                # 2.1 완전 일치
                if line_a == line_b:
                    fc.write(line_a + '\n')
                    continue

                # 2.2 불일치
                diff_a, diff_b = get_highlighted_diff(line_a, line_b)
                
                print("-" * 50)
                print(f"[{idx}/{total_lines}행 불일치]")
                print(f"파일A: {diff_a}")
                print(f"파일B: {diff_b}")
                print("-" * 50)
                
                while True:
                    choice = input("선택 [A:파일A / B:파일B / C:A+☆ / x:종료]: ").strip().lower()
                    
                    if choice == 'a':
                        fc.write(line_a + '\n')
                        print(f"{COLOR_GREEN}>> A 선택됨{COLOR_RESET}")
                        break
                    elif choice == 'b':
                        fc.write(line_b + '\n')
                        print(f"{COLOR_GREEN}>> B 선택됨{COLOR_RESET}")
                        break
                    elif choice == 'c':
                        fc.write(line_a + "☆\n")
                        print(f"{COLOR_GREEN}>> A+☆ 저장됨{COLOR_RESET}")
                        break
                    elif choice == 'x':
                        print(f"\n{COLOR_YELLOW}작업을 중단합니다. 현재까지의 내용은 [{file_c_name}]에 저장되었습니다.{COLOR_RESET}")
                        return
                    else:
                        print("잘못된 입력입니다.")

            # 루프 종료 후 안내
            if start_line_index >= total_lines:
                print(f"\n{COLOR_GREEN}이미 모든 작업이 완료된 상태입니다.{COLOR_RESET}")
            else:
                print(f"\n모든 작업이 완료되었습니다. 결과 파일: {file_c_name}")

    except Exception as e:
        print(f"\n오류 발생: {e}")

if __name__ == "__main__":
    main()