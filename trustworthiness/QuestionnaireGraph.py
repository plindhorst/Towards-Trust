import glob
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _compute_questionaire(answers):
    f = open('./trustworthiness/questionnaire.json')
    questions = json.load(f)

    abi = [0, 0, 0]
    counts = [0, 0, 0]

    for i, concept in enumerate(["Ability", "Benevolence", "Integrity"]):
        for question in questions:
            if question["type"] == concept:
                for answer in answers:
                    try:
                        abi[i] += int(answer[question["name"]])
                        counts[i] += 1
                        break
                    except KeyError:
                        continue
        abi[i] /= counts[i]

    abi = [round(x / 6, 2) for x in abi]

    return abi


class QuestionnaireGraph:
    def __init__(self):
        list_of_files = glob.glob('./data/questionnaire/*.json')
        control_a = []
        control_b = []
        control_i = []
        experimental_a = []
        experimental_b = []
        experimental_i = []
        count = 0
        if len(list_of_files) > 0:

            for questionnaireFile in list_of_files:
                f = open(questionnaireFile)
                data = json.load(f)
                abi_questionnaire = _compute_questionaire(data)
                if 'control' in questionnaireFile:
                    control_a.append(abi_questionnaire[0])
                    control_b.append(abi_questionnaire[1])
                    control_i.append(abi_questionnaire[2])
                if 'advice' in questionnaireFile:
                    count += 1
                    experimental_a.append(abi_questionnaire[0])
                    experimental_b.append(abi_questionnaire[1])
                    experimental_i.append(abi_questionnaire[2])

            if count == 0:
                print("ERROR: You forgot to include your experimental data in the questionnaire folder. Exiting.")
                return

            control_avg_ability = np.average(np.array(control_a))
            control_avg_benevolence = np.average(np.array(control_b))
            control_avg_integrity = np.average(np.array(control_i))
            control_abi = np.array([control_avg_ability, control_avg_benevolence, control_avg_integrity]) # contains the average score for ability, benevolence and integrity
            # of the control group

            experimental_avg_ability = np.average(np.array(experimental_a))
            experimental_avg_benevolence = np.average(np.array(experimental_b))
            experimental_avg_integrity = np.average(np.array(experimental_i))
            experimental_abi = np.array([experimental_avg_ability, experimental_avg_benevolence, experimental_avg_integrity]) # contains the average score for ability, benevolence
            # and integrity of the experimental group

            df = pd.DataFrame({'control group': control_abi, 'experimental group': experimental_abi}, index=["Ability", "Benevolence", "Integrity"])
            df.plot(kind='bar')
            plt.title("ABI Questionnaire Score comparison")
            plt.show()