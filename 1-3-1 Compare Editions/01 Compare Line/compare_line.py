import sys

def compare_files(file_a_path, file_b_path):
    # 연속 불일치 횟수를 저장할 변수
    consecutive_mismatches = 0
    # 불일치한 행의 정보를 임시 저장할 리스트
    mismatch_buffer = []

    try:
        print(f"\n[알림] '{file_a_path}' 와 '{file_b_path}' 비교를 시작합니다...")
        
        # 두 파일을 UTF-8 인코딩으로 엽니다.
        with open(file_a_path, 'r', encoding='utf-8') as fa, \
             open(file_b_path, 'r', encoding='utf-8') as fb:
            
            # zip을 사용하여 두 파일을 동시에 한 행씩 읽어옵니다.
            for line_no, (line_a, line_b) in enumerate(zip(fa, fb), 1):
                
                # 개행 문자(\n) 및 앞뒤 공백 제거
                clean_a = line_a.strip()
                clean_b = line_b.strip()

                # 빈 줄 처리 (빈 줄은 불일치로 간주하거나, 필요시 로직 변경 가능)
                if not clean_a or not clean_b:
                    is_match = False
                else:
                    # 첫 글자와 마지막 글자가 모두 같은지 검사
                    first_char_match = (clean_a[0] == clean_b[0])
                    last_char_match = (clean_a[-1] == clean_b[-1])
                    is_match = first_char_match and last_char_match

                # 2.1 모두 일치하면 플래그 초기화
                if is_match:
                    consecutive_mismatches = 0
                    mismatch_buffer = [] 
                
                # 2.2 불일치 시 플래그 증가 및 정보 저장
                else:
                    consecutive_mismatches += 1
                    mismatch_buffer.append({
                        'line': line_no,
                        'content_a': clean_a,
                        'content_b': clean_b
                    })

                # 3. 플래그가 연속 3행 세워지면 종료
                if consecutive_mismatches == 3:
                    print("\n" + "=" * 50)
                    print("!!! 연속 3회 불일치 발생 - 프로그램 종료 !!!")
                    print("=" * 50)
                    
                    for info in mismatch_buffer:
                        print(f"[행 번호: {info['line']}]")
                        print(f"  - 파일A: {info['content_a']}")
                        print(f"  - 파일B: {info['content_b']}")
                        print("-" * 30)
                    
                    sys.exit() # 프로그램 강제 종료

        print("\n파일 검사가 완료되었습니다. (연속 3회 불일치 없음)")

    except FileNotFoundError:
        print(f"\n[오류] 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
    except Exception as e:
        print(f"\n[오류] 예기치 않은 문제가 발생했습니다: {e}")

if __name__ == "__main__":
    print("--- 텍스트 파일 비교 프로그램 ---")
    
    # 사용자로부터 파일명을 입력받습니다.
    # strip()을 사용하여 입력 시 실수로 들어간 앞뒤 공백을 제거합니다.
    file_name_A = input("파일A의 이름(또는 경로)을 입력하세요: ").strip()
    file_name_B = input("파일B의 이름(또는 경로)을 입력하세요: ").strip()

    # 입력값이 비어있지 않은지 간단히 확인
    if not file_name_A or not file_name_B:
        print("[오류] 파일 이름을 정확히 입력해야 합니다.")
    else:
        compare_files(file_name_A, file_name_B)