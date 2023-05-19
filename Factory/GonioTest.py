import GonioBase

class GonioBL44XU(GonioBase.GonioBase):
    def process(self, **kwargs):
        print(kwargs)
        for key, value in kwargs.items():
            print(key, value)
        # 共通の処理
        print("GonioBL44XU process")

class GonioNormal(GonioBase.GonioBase):
    def process(self, **kwargs):
        print(kwargs)
        for key, value in kwargs.items():
            print(key, value)

        # 共通の処理
        print("GonioNormal process")
