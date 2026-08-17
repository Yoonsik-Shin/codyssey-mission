class OutputUtils:
    @staticmethod
    def print_lines(*lines) -> None:
        """여러 문자열 또는 리스트 항목들을 줄바꿈(\n)으로 합쳐 단 1회 print로 출력합니다."""
        flattened = []
        for line in lines:
            if isinstance(line, list):
                flattened.extend(str(item) for item in line)
            else:
                flattened.append(str(line))
        print("\n".join(flattened))

