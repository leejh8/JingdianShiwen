import pandas as pd
import os
import json
import string

# 파일 상수 정의
VARIANT_FILE = 'variants.json'
CHOICE_FILE = 'choices.json'

def load_json(filename):
    """JSON 파일을 불러옵니다."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(filename, data):
    """JSON 데이터를 파일에 즉시 저장합니다."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"   [경고] {filename} 저장 실패: {e}")

def process_files():
    # 1. 파일 이름 입력 및 확인
    target_filename = input("작업할 파일명(예: input.txt)을 입력하세요: ").strip()
    if not os.path.exists(target_filename):
        print(f"오류: '{target_filename}' 파일을 찾을 수 없습니다.")
        return

    guangyun_filename = 'guangyun.txt'
    if not os.path.exists(guangyun_filename):
        print(f"오류: '{guangyun_filename}' 파일이 필요합니다.")
        return

    try:
        # 2. 데이터 로딩
        print("파일 및 라이브러리를 읽어오는 중...")
        df_target = pd.read_csv(target_filename, header=None, names=['Char'], encoding='utf-8', sep='\t')
        
        # 데이터 타입을 문자열로 통일하여 읽기 (dtype=str 옵션 추가) -> 숫자형 불일치 원천 차단
        df_guangyun = pd.read_csv(guangyun_filename, sep='\t', encoding='utf-8', dtype=str)
        
        # 라이브러리 로드
        variant_dict = load_json(VARIANT_FILE)
        choice_dict = load_json(CHOICE_FILE)
        
        print(f"   -> 이형자 DB 로드됨 ({len(variant_dict)}개)")
        print(f"   -> 중복 선택 DB 로드됨 ({len(choice_dict)}개)")

        # 3. 타겟 열 지정
        print(f"\n[guangyun.txt 열 목록]: {list(df_guangyun.columns)}")
        target_col = input("데이터를 가져올 '지정 열'의 이름을 입력하세요: ").strip()

        if target_col not in df_guangyun.columns:
            print(f"오류: '{target_col}' 열이 존재하지 않습니다.")
            return

        print("\n데이터 매칭을 시작합니다...")
        
        mapped_values = []

        # 4. 한 줄씩 순회하며 처리
        for idx, row in df_target.iterrows():
            char = str(row['Char']) # 입력 파일 글자도 문자열로 확실화
            search_char = char

            # (A) 이형자 처리 확인
            if char in variant_dict:
                search_char = variant_dict[char]
            
            # (B) 광운 데이터 검색
            matches = df_guangyun[df_guangyun['字'] == search_char]
            
            # --- CASE 1: 검색 결과가 없음 ---
            if matches.empty:
                print(f"\n[찾을 수 없음] 원본: '{char}' (검색어: '{search_char}')")
                alt_input = input(f"   -> 대신 검색할 글자를 입력하세요 (없으면 Enter): ").strip()
                
                if alt_input:
                    matches_retry = df_guangyun[df_guangyun['字'] == alt_input]
                    if not matches_retry.empty:
                        variant_dict[char] = alt_input
                        save_json(VARIANT_FILE, variant_dict)
                        print(f"   [학습] '{char}' -> '{alt_input}' 관계 저장됨.")
                        matches = matches_retry
                        search_char = alt_input
                    else:
                        print(f"   [실패] '{alt_input}'도 데이터에 없습니다.")
                        mapped_values.append("")
                        continue
                else:
                    print("   [건너뜀]")
                    mapped_values.append("")
                    continue

            # --- CASE 2: 검색 결과가 1개임 ---
            if len(matches) == 1:
                val = str(matches.iloc[0][target_col])
                mapped_values.append(val)
                continue

            # --- CASE 3: 검색 결과가 여러 개임 (중복 선택) ---
            # 모든 값을 문자열로 변환하여 유니크 값 추출 (핵심 수정 사항)
            unique_vals = matches[target_col].dropna().astype(str).unique()
            
            if len(unique_vals) == 1:
                mapped_values.append(unique_vals[0])
                continue

            # 선택이 필요한 경우
            choice_key = f"{char}_{target_col}"
            
            # 이미 저장된 선택이 있는지 확인
            if choice_key in choice_dict:
                saved_val = str(choice_dict[choice_key]) # 저장된 값도 문자열로 확실화
                
                # 저장된 값이 현재 후보군(문자열 리스트)에 존재하는지 확인
                if saved_val in unique_vals:
                    mapped_values.append(saved_val)
                    # (선택사항) 자동 선택 로그를 보고 싶으면 주석 해제
                    # print(f"   [자동적용] '{char}' -> '{saved_val}'")
                    continue
            
            # 사용자에게 선택 요청
            print(f"\n[중복 발견] 글자 '{char}'에 대해 {len(matches)}개의 행이 있습니다.")
            print(f"   가져올 열: [{target_col}]")
            
            options = list(string.ascii_lowercase)[:len(matches)]
            match_list = []
            
            # 보기 출력
            for i, (m_idx, m_row) in enumerate(matches.iterrows()):
                context = []
                # 컨텍스트 정보 출력 (값이 있는 경우만)
                for ctx_col in ['反切', '聲調', '韻', '小韻', '等第']: 
                    if ctx_col in df_guangyun.columns and pd.notna(m_row[ctx_col]):
                        context.append(f"{ctx_col}:{m_row[ctx_col]}")
                
                target_val = str(m_row[target_col]) # 값을 문자열로 변환
                match_list.append(target_val)
                
                print(f"   {options[i]}) 값: [ {target_val} ]  (정보: {' '.join(context)})")

            # 입력 받기
            while True:
                sel = input(f"   -> 선택할 항목({options[0]}~{options[-1]})을 입력하세요: ").strip().lower()
                if sel in options:
                    selected_idx = options.index(sel)
                    final_val = match_list[selected_idx]
                    
                    mapped_values.append(final_val)
                    
                    # 메모리 갱신 및 파일 저장
                    choice_dict[choice_key] = final_val
                    save_json(CHOICE_FILE, choice_dict)
                    print(f"   [저장] '{char}'의 '{target_col}'값으로 '{final_val}' 선택을 기억합니다.")
                    break
                else:
                    print(f"   오류: {options[0]}~{options[-1]} 중에서 선택해주세요.")

        # 5. 결과 파일 저장
        df_target['Mapped_Value'] = mapped_values
        
        file_base, file_ext = os.path.splitext(target_filename)
        output_filename = f"{file_base}_{target_col}{file_ext}"
        df_target.to_csv(output_filename, sep='\t', index=False, header=False, encoding='utf-8')

        print(f"\n---------------------------------------------------------")
        print(f"작업 완료! 결과 파일: {output_filename}")
        print(f"이형자 DB: {len(variant_dict)}개 | 선택 DB: {len(choice_dict)}개")

    except Exception as e:
        print(f"\n오류 발생: {e}")

if __name__ == "__main__":
    process_files()