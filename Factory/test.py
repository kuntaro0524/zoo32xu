import GonioTest

isCollect = False  # フラッグの値に応じて変更する
isBL44XU = False

if isBL44XU:
    gonio_instance = GonioTest.GonioBL44XU()
    print(gonio_instance.common_variable)
    print(gonio_instance.cmount_position)
else:
    gonio_instance = GonioTest.GonioNormal()
    print(gonio_instance.common_variable)
    print(gonio_instance.cmount_position)


dddd = {'test': 320, 'test2': 3325}
gonio_instance.process(**dddd)