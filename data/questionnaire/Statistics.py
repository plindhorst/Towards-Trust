import json
import pandas as pd
import pingouin as pg

def _read_questionnaire_answers(file_name):
    f = open(file_name)
    data = json.load(f)
    return data

jsonLists = [_read_questionnaire_answers("control_20220526-194337.json"), _read_questionnaire_answers("control_20220527-103717.json"),
             _read_questionnaire_answers("control_20220527-161542.json"), _read_questionnaire_answers("control_20220527-164814.json"),
             _read_questionnaire_answers("control_20220527-171953.json"), _read_questionnaire_answers("control_20220527-181119.json"),
             _read_questionnaire_answers("control_20220527-182129.json"), _read_questionnaire_answers("control_20220527-212910.json"),
             _read_questionnaire_answers("control_20220528-104209.json"), _read_questionnaire_answers("control_20220528-204645.json"),
             _read_questionnaire_answers("control_20220529-200223.json"), _read_questionnaire_answers("control_20220529-210446.json"),
             _read_questionnaire_answers("control_20220530-180421.json"), _read_questionnaire_answers("control_20220531-150113.json"),
             _read_questionnaire_answers("control_20220531-155807.json"), _read_questionnaire_answers("control_20220601-163733.json"),
             _read_questionnaire_answers("control_20220601-201737.json"), _read_questionnaire_answers("control_20220602-124236.json"),
             _read_questionnaire_answers("control_20220603-222013.json"), _read_questionnaire_answers("control_20220603-223812.json")]

transformedObjectsList = []

# print(jsonList)
for jsonList in jsonLists:
    fullObject = {}
    for d in (jsonList[0], jsonList[1], jsonList[2], jsonList[3], jsonList[4], jsonList[5], jsonList[6], jsonList[7], jsonList[8], jsonList[9], jsonList[10], jsonList[11], jsonList[12], jsonList[13], jsonList[14], jsonList[15], jsonList[16], jsonList[17], jsonList[18], jsonList[19]):
        fullObject.update(d)
    transformedObjectsList.append(fullObject)

pandaFrame = pd.DataFrame.from_records(transformedObjectsList)
pandaFrame = pandaFrame.apply(pd.to_numeric, args=('coerce',))
ability = pandaFrame.iloc[:, 5:10]
benevolence = pandaFrame.iloc[:, 10:15]
integrity = pandaFrame.iloc[:, 15:20]

print("Cronbach's alpha, ability: ")
print(pg.cronbach_alpha(data=ability))

print("Cronbach's alpha, benevolence: ")
print(pg.cronbach_alpha(data=benevolence))

print("Cronbach's alpha, integrity: ")
print(pg.cronbach_alpha(data=integrity))