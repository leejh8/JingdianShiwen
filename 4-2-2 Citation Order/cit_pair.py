import pandas as pd
import re
import os
import itertools

def load_data():
    """사용자 입력으로 파일을 불러오는 함수"""
    while True:
        filename = input("📂 분석할 파일명을 입력하세요 (예: cleaned_data.txt): ").strip()
        
        if not os.path.exists(filename):
            print(f"❌ 오류: '{filename}' 파일을 찾을 수 없습니다.\n")
            continue
            
        try:
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.csv':
                df = pd.read_csv(filename, encoding='utf-8-sig')
            elif ext in ['.tsv', '.txt']:
                df = pd.read_csv(filename, sep='\t', encoding='utf-8-sig')
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(filename)
            else:
                print("❌ 지원하지 않는 파일 형식입니다.\n")
                continue
            
            if 'book' not in df.columns or 'content' not in df.columns:
                print("⚠️ 필수 컬럼('book', 'content')이 없습니다.")
                continue
                
            print(f"✅ 파일 로드 성공: {len(df)}행")
            return df
        except Exception as e:
            print(f"❌ 오류 발생: {e}\n")

def extract_citations(text):
    """텍스트에서 서명/인명 추출하여 리스트로 반환"""
    pattern = r'(《[^》]+》|〚[^〛]+〛)'
    if pd.isna(text):
        return []
    return re.findall(pattern, str(text))

def analyze_pair_correlations(sequences, threshold=5):
    """
    모든 쌍(Pair)에 대해 (빈도, 확률)을 계산하여 리스트로 반환
    """
    # 1. 데이터를 저장할 딕셔너리
    # key: (A, B) 튜플 (순서 구분 없음, 정렬해서 저장)
    # value: {'total': 총공기횟수, 'A_first': A가 먼저 나온 횟수, 'B_first': B가 먼저 나온 횟수}
    stats = {}

    print("🔄 쌍(Pair) 분석 및 확률 계산 중...")

    for seq in sequences:
        if len(seq) < 2:
            continue
        
        # 시퀀스 내의 모든 조합 탐색 (순서 유지)
        # 예: [A, B, C] -> (A, B), (A, C), (B, C) 순서로 등장함
        for i in range(len(seq)):
            for j in range(i + 1, len(seq)):
                first = seq[i]
                second = seq[j]
                
                if first == second:
                    continue
                
                # 키는 항상 정렬된 튜플로 사용하여 (A, B)와 (B, A)를 같은 쌍으로 인식
                if first < second:
                    key = (first, second)
                    is_sorted_order = True # 원래 순서와 키 순서가 같음
                else:
                    key = (second, first)
                    is_sorted_order = False # 원래 순서가 키 순서와 반대임 (second가 먼저 나옴)
                
                if key not in stats:
                    stats[key] = {'total': 0, 'key0_first': 0, 'key1_first': 0}
                
                stats[key]['total'] += 1
                
                if is_sorted_order:
                    stats[key]['key0_first'] += 1 # key[0] (first)가 먼저 나옴
                else:
                    stats[key]['key1_first'] += 1 # key[1] (first)가 먼저 나옴 (즉 second가 먼저)

    # 2. 결과 리스트 생성 (Threshold 적용)
    results = []
    
    for (item_a, item_b), data in stats.items():
        total = data['total']
        
        if total < threshold:
            continue
            
        # A -> B 확률 계산 및 추가
        prob_a_b = round(data['key0_first'] / total, 4)
        results.append({
            'cit1': item_a,
            'cit2': item_b,
            'probability': prob_a_b,
            'quantity': total
        })
        
        # B -> A 확률 계산 및 추가 (양방향 모두 생성하여 분석 용이성 증대)
        # 필요 없으면 이 부분 주석 처리 가능
        prob_b_a = round(data['key1_first'] / total, 4)
        results.append({
            'cit1': item_b,
            'cit2': item_a,
            'probability': prob_b_a,
            'quantity': total
        })

    return pd.DataFrame(results)

# === 메인 실행 로직 ===
if __name__ == "__main__":
    # 1. 데이터 로드
    df = load_data()
    
    # 2. 시퀀스 추출
    df['sequence'] = df['content'].apply(extract_citations)
    
    # 3. 기준값 입력
    while True:
        try:
            th_input = input("🔢 최소 공기(Co-occurrence) 횟수를 입력하세요 (기본값 5): ").strip()
            if not th_input:
                threshold = 5
            else:
                threshold = int(th_input)
            break
        except ValueError:
            print("⚠️ 정수를 입력해주세요.")

    # 4. 분석 수행
    all_sequences = df['sequence'].tolist()
    result_df = analyze_pair_correlations(all_sequences, threshold)
    
    if not result_df.empty:
        # 5. 정렬 (quantity 많은 순 -> probability 높은 순)
        result_df = result_df.sort_values(by=['quantity', 'probability'], ascending=[False, False])
        
        print(f"\n✅ 분석 완료! 총 {len(result_df)}개의 관계가 추출되었습니다.")
        print("=== 상위 5개 결과 예시 ===")
        print(result_df.head(5).to_string(index=False))
        
        # 6. 저장
        save_filename = "cit_pair_analysis.txt"
        try:
            result_df.to_csv(save_filename, sep='\t', index=False, encoding='utf-8-sig')
            print(f"\n💾 결과가 '{save_filename}' 파일로 저장되었습니다.")
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
            
    else:
        print("\n⚠️ 설정한 기준(Threshold)을 만족하는 쌍이 하나도 없습니다.")