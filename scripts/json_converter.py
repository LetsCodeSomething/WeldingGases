import json
from copy import deepcopy

terminal_node_template =  {
    "value" : "",
    "type" : "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
    "valtype" : "",
    "meta" : ""
}
non_terminal_node_template = {
    "name" : "",
    "type" : "НЕТЕРМИНАЛ",
    "meta" : "",
    "successors" : []
}

CHEMICAL_ELEMENT_LIST = ["Fe", "C",  "Mn", "Si", "Al", "Cr", "Sn", "Sb", "Cu", "As", 
                         "Zn", "Bi", "Co", "Sm", "Zr", "Ni", "Ti", "V",  "Nb", "S", 
                         "P",  "Mg", "Pb", "B",  "Mo", "O",  "N",  "H",  "Ce", "Be", 
                         "He", "Ar", "Ne", "Cd"] 

def convert_to_universal_json(extracted_info,
                              user_email: str,
                              infores_name: str
                              ):
    INFORES_PATH = user_email + " / Мой Фонд / " + infores_name + "$;"
    ONTOLOGY_PATH = user_email + " / Мой Фонд / Загрузки / Онтология базы технологических газов$;"
    CHEMICAL_ELEMENT_PATH_TEMPLATE = user_email + " / Мой Фонд / Загрузки / База химических элементов$/{:s}/{:s};"

    root_node = {
        "title" : infores_name,
        "code" : " ", #Должен игнорироваться при импорте.
        "path" : INFORES_PATH,
        "date" : " ", #Должен игнорироваться при импорте.
        "creation" : " ", #Должен игнорироваться при импорте.
        "owner_id" : 0, #Должен игнорироваться при импорте.
        "json_type" : "universal",
        "ontology" : ONTOLOGY_PATH,
        "id" : 17940078395396, #Должен игнорироваться при импорте.
        "name" : infores_name,
        "type" : "КОРЕНЬ",
        "meta" : "Онтология базы технологических газов",
        "successors" : [
            {
                "name" : "Моногазы",
                "type" : "НЕТЕРМИНАЛ",
                "meta" : "Моногазы",
                "successors" : []
            },
            {
                "name" : "Многокомпонентные газовые смеси",
                "type" : "НЕТЕРМИНАЛ",
                "meta" : "Многокомпонентные газовые смеси",
                "successors" : []
            }
        ]
    }

    print("Преобразование извлечённой информации в файл формата \"universal.json\"...")
    if (type(extracted_info) != list or
        len(extracted_info) != 3 or
        type(extracted_info[0]) != list or
        type(extracted_info[1]) != list or
        type(extracted_info[2]) != list or
        len(extracted_info[0]) != len(extracted_info[1]) or
        len(extracted_info[0]) != len(extracted_info[2]) or
        len(extracted_info[1]) != len(extracted_info[2])):
        print("ОШИБКА: Входные данные должны быть списком, содержащим три подсписка одинаковой длины.")
    else:
        extracted_info_len = len(extracted_info[0])
        for i in range(0, extracted_info_len):
            print("    Преобразование информации о газе " + str(i + 1) + "/" + str(extracted_info_len) + "...")

            #Проверка формата данных.
            basic_info_json = None
            mark_info_json = None
            composition_json = None

            try:
                basic_info_json = extracted_info[0][i]
                if type(basic_info_json) != dict:
                    print("    ОШИБКА: Основная информация о газе должна быть представлена словарём.")
                    continue
                if ((not "based_on" in basic_info_json) or
                    (not "gas_name" in basic_info_json) or
                    (not "formula" in basic_info_json) or
                    (not "state_standard" in basic_info_json)):
                    print("    ОШИБКА: Словарь с основной информацией о газе должен содержать ключи \"based_on\", \"gas_name\", \"formula\" и \"state_standard\".")
                    continue
                if (type(basic_info_json["based_on"]) != str or
                    type(basic_info_json["gas_name"]) != str or
                    type(basic_info_json["formula"]) != str or
                    type(basic_info_json["state_standard"]) != str):
                    print("    ОШИБКА: Все значения ключей в словаре с основной информацией о газе должны быть строками.")
                    continue
            except:
                print("    ОШИБКА: Не удалось преобразовать основную информацию о газе в формат JSON.")
                continue

            try:
                mark_info_json = extracted_info[1][i]
                if type(mark_info_json) != dict:
                    print("    ОШИБКА: Информация о марке газа должна быть представлена словарём.")
                    continue
                if not "mark" in mark_info_json:
                    print("    ОШИБКА: Словарь с информацией о марке газа должен содержать ключ \"mark\".")
                    continue
                if type(mark_info_json["mark"]) != str:
                    print("    ОШИБКА: Значение ключа \"mark\" в словаре с информацией о марке газа должно быть строкой.")
                    continue
            except:
                print("    ОШИБКА: Не удалось преобразовать информацию о марке газа в формат JSON.")
                continue
        
            try:
                composition_json = extracted_info[2][i]
                if type(composition_json) != dict:
                    print("    ОШИБКА: Информация о составе газа должна быть представлена словарём.")
                    continue
                if not "components" in composition_json:
                    print("    ОШИБКА: Словарь с информацией о составе газа должен содержать ключ \"components\".")
                if type(composition_json["components"]) != list:
                    print("    ОШИБКА: Информация о компонентах газа должна быть представлена списком.")
                if len(composition_json["components"]) == 0:
                    print("    ОШИБКА: В составе газа должен быть как минимум один компонент.")
            except:
                print("    ОШИБКА: Не удалось преобразовать информацию о составе газа в формат JSON.")
                continue

            #Поиск вершины, содержащей название основного газа в составе моногаза.
            base_gas_node_index = None
            for j in range(0, len(root_node["successors"][0]["successors"])):
                if root_node["successors"][0]["successors"][j]["name"] == "Газы " + basic_info_json["based_on"]:
                    base_gas_node_index = j
                    break
            if base_gas_node_index == None:
                #Нужно создать новую вершину для хранения информации о моногазах.
                base_gas_node = deepcopy(non_terminal_node_template)
                base_gas_node["name"] = "Газы " + basic_info_json["based_on"]
                base_gas_node["meta"] = "Класс газов"
                root_node["successors"][0]["successors"].append(base_gas_node)
                base_gas_node_index = len(root_node["successors"][0]["successors"]) - 1

            #Создание вершины, которая будет корнем для остальных
            #вершин с информацией о моногазе.
            gas_node = deepcopy(non_terminal_node_template)
            gas_node["name"] = basic_info_json["gas_name"]
            gas_node["meta"] = "Газ"
            root_node["successors"][0]["successors"][base_gas_node_index]["successors"].append(gas_node)

            #Создание вершины, содержащей химическую формулу основного
            #компонента моногаза.
            gas_formula_node = deepcopy(terminal_node_template)
            gas_formula_node["value"] = basic_info_json["formula"]
            gas_formula_node["valtype"] = "STRING"
            gas_formula_node["meta"] = "Химическое обозначение"
            gas_formula_node["original"] = CHEMICAL_ELEMENT_PATH_TEMPLATE.format(basic_info_json["gas_name"], basic_info_json["formula"])
            gas_node["successors"].append(gas_formula_node)
        
            #Если у газа есть марка, то создаётся вершина для её хранения.
            if mark_info_json["mark"] != "Отсутствует":
                gas_mark_node = deepcopy(terminal_node_template)
                gas_mark_node["value"] = mark_info_json["mark"]
                gas_mark_node["valtype"] = "STRING"
                gas_mark_node["meta"] = "Марка"
                gas_node["successors"].append(gas_mark_node)

            #В примере базы эта вершина идёт после вершины с компонентами, но
            #из-за этого её легко забыть и вообще пропустить, поэтому она перемещена.
            state_standard_node = deepcopy(terminal_node_template)
            state_standard_node["value"] = basic_info_json["state_standard"]
            state_standard_node["valtype"] = "STRING"
            state_standard_node["meta"] = "Стандарт (норматив)"
            gas_node["successors"].append(state_standard_node)

            components_node = deepcopy(non_terminal_node_template)
            components_node["name"] = "Объемные доли компонентов"
            components_node["meta"] = "Объемные доли компонентов"
            gas_node["successors"].append(components_node)

            print("        Преобразование информации о компонентах газа...")
            for j in range(len(composition_json["components"])):
                if ((not "name" in composition_json["components"][j]) or
                    (not "formula" in composition_json["components"][j]) or
                    (not "value" in composition_json["components"][j]) or
                    (not "operation" in composition_json["components"][j])):
                    print("            ОШИБКА: Словарь с информацией о компоненте не содержит все необходимые ключи.")
                    continue
                if (type(composition_json["components"][j]["name"]) != str or
                    type(composition_json["components"][j]["formula"]) != str or
                    type(composition_json["components"][j]["value"]) != str or
                    type(composition_json["components"][j]["operation"])!= str):
                    print("    ОШИБКА: Все значения ключей в словаре с информацией о компонентах газа должны быть строками.")
                    continue

                component_node = deepcopy(non_terminal_node_template)
                component_node["name"] = str(j + 1)
                component_node["meta"] = "Компонент"

                chemical_formula_node = deepcopy(non_terminal_node_template)
                chemical_formula_node["name"] = composition_json["components"][j]["formula"]
                chemical_formula_node["meta"] = "Химическое обозначение"
                chemical_formula_node["original"] = CHEMICAL_ELEMENT_PATH_TEMPLATE.format(composition_json["components"][j]["name"],
                                                                                      composition_json["components"][j]["formula"])
                #Проверка информации о компоненте на наличие ошибок.
                if not composition_json["components"][j]["formula"] in CHEMICAL_ELEMENT_LIST:
                    print("            ПРЕДУПРЕЖДЕНИЕ: Компонент газа \"" + 
                          composition_json["components"][j]["formula"] + 
                          "\" не содержится в списке химических элементов. Это вызовет ошибку импорта.")
            
                float_component_value = None
                try:
                    float_component_value = float(composition_json["components"][j]["value"])
                except:
                    print("            ОШИБКА: Не удалось преобразовать содержание компонента газа в процентах в вещественное число (" + 
                          composition_json["components"][j]["value"] + ").")
                    continue

                if (float_component_value < 0 or float_component_value > 100):
                    print("            ПРЕДУПРЕЖДЕНИЕ: Содержание компонента газа в процентах должно находиться в пределах от 0 до 100, но получено " +
                        float_component_value + ".")

                percent_node = deepcopy(terminal_node_template)
                percent_node["value"] = "%"
                percent_node["valtype"] = "STRING"
                percent_node["meta"] = "%"

                operation_node = deepcopy(non_terminal_node_template)
                operation_sign_node = deepcopy(terminal_node_template)
                if composition_json["components"][j]["operation"] == "не менее":
                    operation_node["name"] = "Не менее"
                    operation_node["meta"] = "Не менее"

                    operation_sign_node["value"] = "≥"
                    operation_sign_node["valtype"] = "STRING"
                    operation_sign_node["meta"] = "≥"
                else:
                    operation_node["name"] = "Не более"
                    operation_node["meta"] = "Не более"

                    operation_sign_node["value"] = "≤"
                    operation_sign_node["valtype"] = "STRING"
                    operation_sign_node["meta"] = "≤"

                value_node = deepcopy(terminal_node_template)
                value_node["value"] = float(composition_json["components"][j]["value"])
                value_node["valtype"] = "REAL"
                value_node["meta"] = "Числовое значение"

                #Соединение вершин.
                operation_node["successors"].append(operation_sign_node)
                operation_node["successors"].append(value_node)
                chemical_formula_node["successors"].append(percent_node)
                chemical_formula_node["successors"].append(operation_node)
                component_node["successors"].append(chemical_formula_node)
                components_node["successors"].append(component_node)
            print("        Завершено.")
            print("    Завершено.")
        return root_node

#############################

import argparse
import sys

params = argparse.ArgumentParser(description=
"""Reads simplified JSON from the specified text file and converts simplified JSON into universal JSON.""",
formatter_class=argparse.RawDescriptionHelpFormatter, epilog=
"""EXAMPLE

python json_converter.py -i gemma_extracted_info.json -e example@example -n welding_gases

Read simplified JSON from \"gemma_extracted_info.json\", convert it into universal JSON and save it into \"welding_gases.universal.json\".""")

params.add_argument("-i", "--input", type=argparse.FileType('r',encoding="utf-8"), help="The name of the input text file with simplified JSON structure.")
params.add_argument("-e", "--user-email", type=str, help="The platform user's email. Required for the generation of the output file.")
params.add_argument("-n", "--infores-name", type=str, help="Information resource name. Required for the generation of the output file. If the parameter is missing, the name of the information resource will default to \"Новая база сварочных газов\".")

params = params.parse_args()

if not params.input:
    sys.exit("The input file is not specified. Exiting.")
if not params.user_email:
    sys.exit("User email is not specified. Exiting.")

infores_name = params.infores_name if params.infores_name else "Новая база сварочных газов"

extracted_info = None 
try:
    extracted_info = json.loads(params.input.read())
except:
    sys.exit("The specified file contains invalid JSON. Exiting.")

params.input.close()

converted_info = convert_to_universal_json(extracted_info, params.user_email, infores_name)

#print(extracted_info)

f = open(infores_name + ".universal.json", "w", encoding="utf-8")
f.write(json.dumps(converted_info, indent=4, ensure_ascii=False))
f.close()

print("Завершено.")