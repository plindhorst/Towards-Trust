import json
import pandas as pd
import pingouin as pg

def _read_questionnaire_answers(file_name):
    f = open(file_name)
    data = json.load(f)
    return data









def cronbachsAlpha():
    #Initialize panda frame control group.
    jsonControlLists = [_read_questionnaire_answers("control_20220526-194337.json"), _read_questionnaire_answers("control_20220527-103717.json"),
                        _read_questionnaire_answers("control_20220527-161542.json"), _read_questionnaire_answers("control_20220527-164814.json"),
                        _read_questionnaire_answers("control_20220527-171953.json"), _read_questionnaire_answers("control_20220527-181119.json"),
                        _read_questionnaire_answers("control_20220527-182129.json"), _read_questionnaire_answers("control_20220527-212910.json"),
                        _read_questionnaire_answers("control_20220528-104209.json"), _read_questionnaire_answers("control_20220528-204645.json"),
                        _read_questionnaire_answers("control_20220529-200223.json"), _read_questionnaire_answers("control_20220529-210446.json"),
                        _read_questionnaire_answers("control_20220530-180421.json"), _read_questionnaire_answers("control_20220531-150113.json"),
                        _read_questionnaire_answers("control_20220531-155807.json"), _read_questionnaire_answers("control_20220601-163733.json"),
                        _read_questionnaire_answers("control_20220601-201737.json"), _read_questionnaire_answers("control_20220602-124236.json"),
                        _read_questionnaire_answers("control_20220603-222013.json"), _read_questionnaire_answers("control_20220603-223812.json")]

    jsonExperimentalLists = [_read_questionnaire_answers("control_20220526-194337.json"), _read_questionnaire_answers("control_20220527-103717.json"),
                             _read_questionnaire_answers("control_20220527-161542.json"), _read_questionnaire_answers("control_20220527-164814.json"),
                             _read_questionnaire_answers("control_20220527-171953.json"), _read_questionnaire_answers("control_20220527-181119.json"),
                             _read_questionnaire_answers("control_20220527-182129.json"), _read_questionnaire_answers("control_20220527-212910.json"),
                             _read_questionnaire_answers("control_20220528-104209.json"), _read_questionnaire_answers("control_20220528-204645.json"),
                             _read_questionnaire_answers("control_20220529-200223.json"), _read_questionnaire_answers("control_20220529-210446.json"),
                             _read_questionnaire_answers("control_20220530-180421.json"), _read_questionnaire_answers("control_20220531-150113.json"),
                             _read_questionnaire_answers("control_20220531-155807.json"), _read_questionnaire_answers("control_20220601-163733.json"),
                             _read_questionnaire_answers("control_20220601-201737.json"), _read_questionnaire_answers("control_20220602-124236.json"),
                             _read_questionnaire_answers("control_20220603-222013.json"), _read_questionnaire_answers("control_20220603-223812.json")]

    transformedObjectsListControl = []
    transformedObjectsListExperimental = []

    # print(jsonList)
    for jsonControlList in jsonControlLists:
        fullObject = {}
        for d in (jsonControlList[0], jsonControlList[1], jsonControlList[2], jsonControlList[3], jsonControlList[4], jsonControlList[5], jsonControlList[6], jsonControlList[7], jsonControlList[8], jsonControlList[9], jsonControlList[10], jsonControlList[11], jsonControlList[12], jsonControlList[13], jsonControlList[14], jsonControlList[15], jsonControlList[16], jsonControlList[17], jsonControlList[18], jsonControlList[19]):
            fullObject.update(d)
        transformedObjectsListControl.append(fullObject)

    for jsonExperimentalList in jsonExperimentalLists:
        fullObject = {}
        for d in (jsonExperimentalList[0], jsonExperimentalList[1], jsonExperimentalList[2], jsonExperimentalList[3], jsonExperimentalList[4], jsonExperimentalList[5], jsonExperimentalList[6], jsonExperimentalList[7], jsonExperimentalList[8], jsonExperimentalList[9], jsonExperimentalList[10], jsonExperimentalList[11], jsonExperimentalList[12], jsonExperimentalList[13], jsonExperimentalList[14], jsonExperimentalList[15], jsonExperimentalList[16], jsonExperimentalList[17], jsonExperimentalList[18], jsonExperimentalList[19]):
            fullObject.update(d)
        transformedObjectsListExperimental.append(fullObject)

    pandaFrameControl = pd.DataFrame.from_records(transformedObjectsListControl)
    pandaFrameControl = pandaFrameControl.apply(pd.to_numeric, args=('coerce',))
    pandaFrameExperimental = pd.DataFrame.from_records(transformedObjectsListExperimental)
    pandaFrameExperimental = pandaFrameExperimental.apply(pd.to_numeric, args=('coerce',))

    abilityControl = pandaFrameControl.iloc[:, 5:10]
    benevolenceControl = pandaFrameControl.iloc[:, 10:15]
    integrityControl = pandaFrameControl.iloc[:, 15:20]

    abilityExperimental = pandaFrameExperimental.iloc[:, 5:10]
    benevolenceExperimental = pandaFrameExperimental.iloc[:, 10:15]
    integrityExperimental = pandaFrameExperimental.iloc[:, 15:20]

    #Calculate cronbach_alpha
    print("Cronbach's alpha, control group, ability: ")
    print(pg.cronbach_alpha(data=abilityControl)[0])

    print("Cronbach's alpha, experimental group, ability: ")
    print(pg.cronbach_alpha(data=abilityExperimental)[0])

    print("Cronbach's alpha, control group, benevolence: ")
    print(pg.cronbach_alpha(data=benevolenceControl)[0])

    print("Cronbach's alpha, experimental group, benevolence: ")
    print(pg.cronbach_alpha(data=benevolenceExperimental)[0])

    print("Cronbach's alpha, control group, integrity: ")
    print(pg.cronbach_alpha(data=integrityControl)[0])

    print("Cronbach's alpha, experimental group, integrity: ")
    print(pg.cronbach_alpha(data=integrityExperimental)[0])


