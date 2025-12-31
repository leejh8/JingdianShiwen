import re
import os

def run_regex_replacer():
    print("=== Regex 찾아 바꾸기 (확장 한자 지원) ===")
    
    # 1. 파일 읽기
    while True:
        input_filename = input("읽어올 파일명 (예: input.txt): ").strip()
        if os.path.exists(input_filename):
            break
        print("파일이 존재하지 않습니다. 다시 입력해주세요.")

    try:
        # utf-8 인코딩으로 파일을 엽니다. (확장 한자 처리에 필수)
        with open(input_filename, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"[{input_filename}] 파일을 성공적으로 읽었습니다. ({len(content)} 글자)")
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    # 2. 반복적으로 Find & Replace 수행
    step = 1
    while True:
        print(f"\n[Step {step}]")
        find_pattern = input("Find (Regex) [엔터 입력 시 종료]: ")
        
        # 엔터만 입력하면 루프 종료 및 저장 단계로 이동
        if not find_pattern:
            break
        
        replace_pattern = input(f"Replace with (그룹 참조: \\1, \\2 ...): ")

        try:
            # re.subn은 (변경된 문자열, 변경된 횟수) 튜플을 반환합니다.
            # Python의 re.sub는 기본적으로 \1, \2 같은 역참조를 지원합니다.
            new_content, count = re.subn(find_pattern, replace_pattern, content)
            
            if count > 0:
                content = new_content
                print(f"-> {count}건이 변경되었습니다.")
            else:
                print("-> 매칭되는 내용이 없습니다.")
            
            step += 1

        except re.error as e:
            print(f"!! 정규표현식 오류: {e}")
            print("   (괄호 짝이 맞는지, 특수문자 처리가 올바른지 확인해주세요)")

    # 3. 파일 저장
    print("\n=== 작업 종료 ===")
    while True:
        output_filename = input("저장할 파일명 (예: output.txt): ").strip()
        if output_filename:
            break
        print("파일명을 입력해야 합니다.")

    try:
        # 저장할 때도 utf-8을 사용하여 확장 한자를 보존합니다.
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[{output_filename}] 파일에 저장이 완료되었습니다.")
    except Exception as e:
        print(f"저장 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    run_regex_replacer()