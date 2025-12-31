import re
import os

# 결과를 저장할 TSV 파일 이름
RESULT_FILE = "character_counts.tsv"

def write_header_if_needed():
    """결과 파일이 없으면 헤더(열 제목)를 작성합니다."""
    if not os.path.exists(RESULT_FILE):
        try:
            with open(RESULT_FILE, 'w', encoding='utf-8') as f_out:
                # 규칙 10: 파일명, 경문, 주석, 합계 4개 열
                f_out.write("파일명\t경문글자수\t주석글자수\t합계글자수\n")
        except IOError as e:
            print(f"결과 파일 헤더 작성 중 오류 발생: {e}")

def count_characters(filename):
    """지정된 파일의 글자 수를 규칙에 따라 계산합니다."""
    main_text_count = 0
    comment_text_count = 0

    try:
        with open(filename, 'r', encoding='utf-8') as f_in:
            all_lines = f_in.readlines()

        # 규칙 8: 내용이 있는 마지막 행은 세지 않습니다.
        # 뒤에서부터 순회하며 내용이 있는 첫 번째 줄(즉, 파일의 마지막 내용 줄)의 인덱스를 찾습니다.
        last_content_line_index = -1
        for i in range(len(all_lines) - 1, -1, -1):
            if all_lines[i].strip():
                last_content_line_index = i
                break

        if last_content_line_index == -1:
            print(f"'{filename}' 파일이 비어있거나 내용이 없습니다.")
            return None, None, None # 처리할 내용이 없음

        # 마지막 내용 줄을 *제외*하고 처리하기 위해 슬라이싱합니다.
        # all_lines[:last_content_line_index] 는 0부터 last_content_line_index - 1 까지의 모든 줄을 포함합니다.
        for line in all_lines[:last_content_line_index]:
            line = line.strip()

            # 규칙 2: #로 시작하는 행은 무시
            if line.startswith('#'):
                continue

            # 규칙 3: <[^>]+> (HTML 태그 등) 무시
            line = re.sub(r'<[^>]+>', '', line)

            # 규칙 4: ¶와 /는 무시
            line = line.replace('¶', '').replace('/', '')

            # 규칙 6: &KR\d+; 문자열은 1개 글자로 간주
            # '임시' 문자(예: '_')로 대체하여 나중에 공백 제거 후 1글자로 카운트되도록 함
            line = re.sub(r'&KR\d+;', '_', line)

            # 규칙 7: (와 ) 사이는 주석, 나머지는 경문
            # re.findall로 모든 주석 괄호 안의 내용을 추출합니다.
            comment_parts = re.findall(r'\((.*?)\)', line)
            comment_text = " ".join(comment_parts) # 모든 주석 내용을 하나로 합침

            # re.sub로 괄호와 그 안의 내용을 모두 제거하여 경문만 남깁니다.
            main_text = re.sub(r'\(.*?\)', '', line)

            # 규칙 5: 공백 문자는 세지 않음
            # 경문과 주석 각각에서 모든 공백(스페이스, 탭 등)을 제거
            cleaned_main = re.sub(r'\s', '', main_text)
            cleaned_comment = re.sub(r'\s', '', comment_text)

            # 글자 수 누적
            main_text_count += len(cleaned_main)
            comment_text_count += len(cleaned_comment)

        total_count = main_text_count + comment_text_count
        return main_text_count, comment_text_count, total_count

    except FileNotFoundError:
        print(f"[오류] '{filename}' 파일을 찾을 수 없습니다. 파일 이름을 확인하세요.")
        return None, None, None
    except Exception as e:
        print(f"[오류] 파일 처리 중 예외 발생: {e}")
        return None, None, None

def main():
    """메인 실행 함수"""
    # 규칙 9: 결과 파일이 없으면 헤더를 미리 만듭니다.
    write_header_if_needed()

    # 규칙 9: 사용자의 입력을 받아 작업을 반복합니다.
    while True:
        filename_input = input("분석할 파일 이름을 입력하세요 (종료: q 또는 exit): ")
        
        if filename_input.lower() in ['q', 'exit']:
            print("작업을 종료합니다.")
            break
            
        if not filename_input:
            continue

        # 규칙 1: ".txt"를 쓰지 않아도 TXT 파일로 간주
        if not filename_input.endswith('.txt'):
            filename = filename_input + ".txt"
        else:
            filename = filename_input

        # 글자 수 계산
        main_count, comment_count, total_count = count_characters(filename)

        # 계산이 성공적으로 완료된 경우에만 결과를 출력하고 저장합니다.
        if main_count is not None:
            print(f"--- 분석 결과: {filename} ---")
            print(f"경문 글자수: {main_count}")
            print(f"주석 글자수: {comment_count}")
            print(f"합계 글자수: {total_count}")
            print("-" * (20 + len(filename)))

            # 규칙 9: 결과를 TSV 파일에 추가 (append)
            try:
                with open(RESULT_FILE, 'a', encoding='utf-8') as f_out:
                    f_out.write(f"{filename}\t{main_count}\t{comment_count}\t{total_count}\n")
                print(f"결과를 '{RESULT_FILE}'에 성공적으로 저장했습니다.\n")
            except IOError as e:
                print(f"결과 파일('{RESULT_FILE}') 저장 중 오류 발생: {e}\n")
        else:
            # count_characters 함수 내에서 오류 메시지가 이미 출력됨
            print("다음 파일 이름을 입력하세요.\n")

if __name__ == "__main__":
    main()
