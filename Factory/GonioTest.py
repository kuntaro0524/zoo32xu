import GonioBase

class GonioNormal(GonioBase.GonioBase):
    def process(self):
        # 共通の処理
        print("GonioNormal process")

class GonioSpecial(GonioBase.GonioBase):
    def process(self):
        # 共通の処理
        print("GonioSpecial process")
