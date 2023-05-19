import GonioTest

isCollect = False  # フラッグの値に応じて変更する

if isCollect:
    gonio_instance = GonioTest.GonioNormal()
    print(gonio_instance.common_variable)
else:
    gonio_instance = GonioTest.GonioSpecial()
    print(gonio_instance.common_variable)

gonio_instance.process()
