from components.quiz import Quiz

FALLBACK_QUIZZES = [
    Quiz(
        "LIFO(Last-In, First-Out) 특징을 가지는 자료구조는 무엇인가?",
        ["큐 (Queue)", "스택 (Stack)", "트리 (Tree)", "그래프 (Graph)"],
        1,
        {
            "sentence": "입력된 순서의 반대로 출력되는 후입선출 자료구조입니다.",
            "cost": 100
        },
        "Data Structure",
        "Easy"
    ),
    Quiz(
        "OSI 7계층 중 IP 주소를 기반으로 패킷의 경로를 결정하는 3계층(네트워크 계층)의 주요 장비는?",
        ["스위치 (Switch)", "라우터 (Router)", "리피터 (Repeater)", "허브 (Hub)"],
        1,
        {
            "sentence": "데이터 전송 최적의 경로를 지정해주는 장비입니다.",
            "cost": 100
        },
        "Network",
        "Medium"
    ),
    Quiz(
        "데이터베이스 트랜잭션의 안전성을 보장하기 위한 ACID 특성에 포함되지 않는 것은?",
        ["원자성 (Atomicity)", "일관성 (Consistency)", "보안성 (Security)", "고립성 (Isolation)"],
        2,
        {
            "sentence": "보안성(Security)은 독립적인 대분류 보안 영역에 속합니다.",
            "cost": 100
        },
        "Database",
        "Medium"
    ),
    Quiz(
        "두 개 이상의 프로세스가 서로 자원을 점유한 상태에서 상대방의 자원을 요구하며 무한히 대기하는 현상은?",
        ["교착 상태 (Deadlock)", "문맥 교환 (Context Switching)",
         "인터럽트 (Interrupt)", "임계 구역 (Critical Section)"],
        0,
        {
            "sentence": "영문으로 Deadlock이라 불리는 교착 현상입니다.",
            "cost": 100
        },
        "OS",
        "Medium"
    ),
    Quiz(
        "최악의 경우(Worst-case)에도 O(n log n)의 시간 복잡도를 보장하는 정렬 알고리즘은?",
        ["버블 정렬 (Bubble Sort)", "선택 정렬 (Selection Sort)",
         "삽입 정렬 (Insertion Sort)", "병합 정렬 (Merge Sort)"],
        3,
        {
            "sentence": "분할 정복(Divide and Conquer) 방식을 사용하는 정렬입니다.",
            "cost": 100
        },
        "Algorithm",
        "Hard"
    )
]
