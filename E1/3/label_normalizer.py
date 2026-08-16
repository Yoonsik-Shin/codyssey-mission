class LabelNormalizer:
    @staticmethod
    def normalize(raw):
        key = str(raw).strip().lower()
        if key in ("+", "cross"):
            return "Cross"
        if key == "x":
            return "X"
        return None