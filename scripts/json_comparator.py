import re
from enum import Enum

#Universal JSON Comparator.
class UJSONC:
    #Вспомогательный метод. Экранирует символы, которые можно 
    #неоднозначно интерпретировать при разборе логов компаратора.
    @staticmethod
    def __escape_string(string):
        if type(string) != str:
            raise "ERROR: Input must be a string."

        string = str(string.encode("unicode_escape"))
        string = string[2:len(string) - 1]
        return string.replace(" ", "\\\\ ").replace("\'", "\\\\\'").replace("\"", "\\\\\"").replace(".", "\\\\.").replace("[", "\\\\[").replace("]", "\\\\]")
     
    #Вспомогательный метод. Соединяет два пути.
    #Если первый путь не пустой, то добавляет между путями точку.
    @staticmethod
    def __join_paths(path1, path2):
        if len(path1) == 0:
            return UJSONC.__escape_string(path2)
        return path1 + "." + UJSONC.__escape_string(path2)

    #Вспомогательный метод.
    #Проверка типа ключа словаря.
    @staticmethod
    def __is_supported_key_type(key_type):
        if (key_type == bool or key_type == int or key_type == float or 
            key_type == str or key_type == type(None)):
            return True
        return False

    #Вспомогательный метод.
    #Проверка типа значения элемента списка или ключа словаря.
    @staticmethod
    def __is_supported_value_type(value_type):
        if (value_type == bool or value_type == int or value_type == float or 
            value_type == str or value_type == list or value_type == dict or
            value_type == type(None)):
            return True
        return False

    @staticmethod
    def __compare_lists(list1, list2, path, result):
        len1 = len(list1)
        len2 = len(list2)

        if (len1 != len2):
            result += "size_mismatch " + path + " " + str(len1) + " " + str(len2) + "\n"
    
        min_len = min(len1, len2)

        for i in range(min_len):
            t1 = type(list1[i])
            if not UJSONC.__is_supported_value_type(t1):
                result += "value_type_error " + path + "[" + str(i) + "] l " + UJSONC.__escape_string(str(t1)) + "\n"
                continue

            t2 = type(list2[i])
            if not UJSONC.__is_supported_value_type(t2):
                result += "value_type_error " + path + "[" + str(i) + "] r " + UJSONC.__escape_string(str(t2)) + "\n"
                continue

            if t1 == t2:
                if (t1 == bool or t1 == float or t1 == int or 
                    t1 == str or t1 == type(None)):
                    if (list1[i] != list2[i]):
                        result += "value_mismatch " + path + "[" + str(i) + "] "  + UJSONC.__escape_string(str(list1[i])) + " " + UJSONC.__escape_string(str(list2[i])) + "\n"
                elif t1 == list:
                    result = UJSONC.__compare_lists(list1[i], list2[i], path + "[" + str(i) + "]", result)
                else:
                    result = UJSONC.__compare_dicts(list1[i], list2[i], path + "[" + str(i) + "]", result)
            else:
                result += "value_type_mismatch " + path + "[" + str(i) + "] " + UJSONC.__escape_string(str(t1)) + " " + UJSONC.__escape_string(str(t2)) + "\n"

        max_len = max(len1, len2)
        longest_list = list1 if min_len == len2 else list2
        struct_num = "l" if min_len == len2 else "r"

        for i in range(max_len - min_len):
            t = type(longest_list[i + min_len])
            if not UJSONC.__is_supported_value_type(t):
                result += "value_type_error " + path + "[" + str(i + min_len) + "] " + struct_num + " " + UJSONC.__escape_string(str(t)) + "\n"

        return result

    @staticmethod
    def __compare_dicts(dict1, dict2, path, result):
        common_keys = set(dict1.keys()).intersection(set(dict2.keys()))
        dict1_specific_keys = set(dict1.keys()).difference(common_keys)
        dict2_specific_keys = set(dict2.keys()).difference(common_keys)

        for i in dict1_specific_keys:
            if not UJSONC.__is_supported_key_type(type(i)):
                result += "key_type_error " + UJSONC.__join_paths(path, str(i)) + " l " + UJSONC.__escape_string(str(type(i))) + "\n"
            if not UJSONC.__is_supported_value_type(type(dict1[i])):
                result += "value_type_error " + UJSONC.__join_paths(path, str(i)) + " l " + UJSONC.__escape_string(str(type(dict1[i]))) + "\n"
            result += "key_missing_in " + UJSONC.__join_paths(path, str(i)) + " r\n"

        for i in dict2_specific_keys:
            if not UJSONC.__is_supported_key_type(type(i)):
                result += "key_type_error " + UJSONC.__join_paths(path, str(i)) + " r " + UJSONC.__escape_string(str(type(i))) + "\n"
            if not UJSONC.__is_supported_value_type(type(dict2[i])):
                result += "value_type_error " + UJSONC.__join_paths(path, str(i)) + " r " + UJSONC.__escape_string(str(type(dict2[i]))) + "\n"
            result += "key_missing_in " + UJSONC.__join_paths(path, str(i)) + " l\n"

        for i in common_keys:
            if not UJSONC.__is_supported_key_type(type(i)):
                result += "key_type_error " + UJSONC.__join_paths(path, str(i)) + " b " + UJSONC.__escape_string(str(type(i))) + "\n"

            t1 = type(dict1[i])
            if not UJSONC.__is_supported_value_type(t1):
                result += "value_type_error " + UJSONC.__join_paths(path, i) + " l " + UJSONC.__escape_string(str(t1)) + "\n"
                continue

            t2 = type(dict2[i])
            if not UJSONC.__is_supported_value_type(t2):
                result += "value_type_error " + UJSONC.__join_paths(path, i) + " r " + UJSONC.__escape_string(str(t2)) + "\n"
                continue

            if t1 == t2:
                if (t1 == bool or t1 == float or t1 == int or 
                    t1 == str or dict1[i] == None):
                    if (dict1[i] != dict2[i]):
                        result += "value_mismatch " + UJSONC.__join_paths(path, str(i)) + " " + UJSONC.__escape_string(str(dict1[i])) + " " + UJSONC.__escape_string(str(dict2[i])) + "\n"
                elif t1 == list:
                    result = UJSONC.__compare_lists(dict1[i], dict2[i], UJSONC.__join_paths(path, str(i)), result)
                else:
                    result = UJSONC.__compare_dicts(dict1[i], dict2[i], UJSONC.__join_paths(path, str(i)), result)
            else:
                result += "value_type_mismatch " + UJSONC.__join_paths(path, i) + " " + UJSONC.__escape_string(str(t1)) + " " + UJSONC.__escape_string(str(t2)) + "\n"

        return result

    #Данный метод выполняет сравнение произвольной структуры json1 с произвольной структурой json2 в формате JSON.
    #Присутствует поддержка "None" в качестве ключа словаря или значения. При встрече синтаксической ошибки  
    #элемент пропускается, после чего к выводу добавляется соответствующее сообщение.
    #Возвращаемое значение: (<Наличие разницы (логическое значение)>, <Разница (строка)>)
    @staticmethod
    def compare_json(json1, json2):
        result = ""
        
        if (type(json1) != list and type(json1) != dict):
            result += "input_type_error l " + UJSONC.__escape_string(str(type(json1))) + "\n"
        if (type(json2) != list and type(json2) != dict): 
            result += "input_type_error r " + UJSONC.__escape_string(str(type(json2))) + "\n"
    
        if len(result) > 0:
            return (False, result)

        if type(json1) != type(json2):
            return (False, "full_json_mismatch " + UJSONC.__escape_string(str(type(json1))) + " " + UJSONC.__escape_string(str(type(json2))))
    
        if type(json1) == list:
            result = UJSONC.__compare_lists(json1, json2, "", result)
        else:
            result = UJSONC.__compare_dicts(json1, json2, "", result)
    
        return (len(result) == 0, result)
    
#Пояснитель.
class Explainer:
    #Формат словаря:
    #    Идентификатор сообщения: [Первый параметр - JSON-ключ / Количество параметров сообщения / Шаблон пояснения / Тип параметров в пояснении].
    #
    #Тип параметров в пояснении - строка, содержащая информацию о том, какие параметры нужно 
    #подставить в шаблон для генерации корректного пояснения. Во время генерации пояснения 
    #выполняется посимвольное чтение строки типов параметров пояснения.
    #Каждый символ представляет собой команду для Пояснителя:
    # j - взять название JSON-структуры из параметров сообщения, преобразовать в строку,
    #     поместить результат в буфер параметров пояснения и перейти к следующему параметру.
    #     Допустимые значения названия JSON-структуры и результат преобразования в строку: 
    #     * "l" - " первой";
    #     * "r" - "о второй";
    #     * "b" - " обеих".
    #     Недопустимые значения вызовут ошибку.
    # k - взять параметр сообщения как JSON-ключ, сгенерировать словесное пояснение (в родительном падеже) 
    #     к JSON-ключу и поместить в буфер параметров пояснения.
    # K - взять параметр сообщения как JSON-ключ, сгенерировать словесное пояснение (в именительном падеже) 
    #     к JSON-ключу и поместить в буфер параметров пояснения.
    # i - перейти к следующему параметру входного сообщения.
    # d - перейти к предыдущему параметру входного сообщения.
    # p - взять параметр сообщения, преобразовать его в строку, поместить в буфер параметров 
    #     пояснения и перейти к следующему.
    #Другие символы вызовут ошибку.
    __KNOWLEDGEBASE = {
        "input_type_error":    [False, 2, "Некорректный тип {:s} JSON-структуры: {:s}.", "jip"],
        "full_json_mismatch":  [False, 2, "JSON-структуры имеют разные типы на первом уровне: {:s} и {:s}.", "pip"],
        "size_mismatch":       [True,  3, "Не совпадает количество {:s} в JSON-структурах: {:s} и {:s}.", "kipip"],
        "value_type_error":    [True,  3, "В {:s} JSON-структуре {:s} имеет некорректный для JSON тип {:s}.", "ijdKiip"],
        "value_mismatch":      [True,  3, "Не совпадают {:s} в JSON-структурах: {:s} и {:s}.", "kipip"],
        "value_type_mismatch": [True,  3, "Не совпадают типы {:s} в JSON-структурах: {:s} и {:s}.", "kipip"],
        "key_type_error":      [False, 3, "В {:s} JSON-структуре {:s} имеет некорректный для JSON тип {:s}.", "ijdKiip"],
        "key_missing_in":      [False, 2, "В {:s} JSON-структуре отсутству(-ет/-ют) {:s}.", "ijdK"]
    }
    
    class LangCase(Enum):
        NOMINATIVE = 0
        GENITIVE   = 1
        DATIVE     = 2

    @staticmethod
    def __unescape_string(string: str):
        string = re.sub("\\\\\\\\u([0-9a-fA-F]{4})", lambda l: chr(int(l.group()[3:7], 16)), string)
        string = (string.replace("\\\\ ", " ").replace("\\\\\'", "\'")
                        .replace("\\\\\"", "\"").replace("\\\\.", ".")
                        .replace("\\\\[", "[").replace("\\\\]", "]")
                        .replace("\\\\\\\\","\\").replace("\\\\n", "\n"))
        return string

    #Проверка корректности строки из входных данных.
    @staticmethod
    def __validate_string(string: str):
        regex = "(?<!\\\\)\\\\(?!\\\\)"
        if not re.search(regex, string) == None:
            return "ОШИБКА: Некорректный формат входных данных: обнаружен одинарный \"\\\"."
        if not re.search("\\\\$", string) == None:
            return "ОШИБКА: Некорректный формат входных данных: отсутствует экранируемый символ."
        if len(re.findall("\\\\", string)) % 2 == 1:
            return "ОШИБКА: Некорректный формат входных данных: обнаружен одинарный \"\\\"."
        return ""
    
    #Изначально при генерации сообщений газ назывался своим 
    #порядковым номером.
    #
    #Компаратор универсальный (т.е. он может сравнить любые JSON-структуры),
    #и он не знает онтологию базы сварочных газов, и поэтому он выдаёт 
    #формализованные логи, которые потом объясняет пояснитель. Так как в логах 
    #содержатся только JSON-ключи, пояснитель знает только порядковый номер газа.
    #По порядковому номеру газа можно извлечь его назание из исходных 
    #JSON-структур, но для этого их надо загрузить в пояснителя.
    #Извлечение названия из JSON-структур также создаёт следующие проблемы:
    # 1) ключа с названием газа может не быть в JSON-структурах;
    # 2) название одного и того же газа может не совпадать.
    #Поэтому сначала проверяется наличие ключа. Если ключ отсутствует в
    #одной из структур, название берётся из оставшейся. Если ключа нет вообще,
    #то вместо названия используется порядковый номер газа. Если названия не
    #совпадают, то берутся оба названия и выводятся через символ "/". Если
    #названия совпадают, то выводится один экземпляр названия.
    def __generate_gas_name(gas_id: int, source_json: tuple, lang_case: LangCase):
        name_l = None
        try:
            name_l = str(source_json[0][0][gas_id]["gas_name"])
        except:
            pass
        
        name_r = None
        try:
            name_r = str(source_json[1][0][gas_id]["gas_name"])
        except:
            pass
        
        if name_l == None:
            if name_r == None:
                if lang_case == Explainer.LangCase.GENITIVE:
                    return str(gas_id) + "-го газа"
                return str(gas_id) + "-му газу"
            
            if lang_case == Explainer.LangCase.GENITIVE:
                return "газа \"" + name_r + "\""
            return "газу \"" + name_r + "\""
        
        if name_r == None:
            if lang_case == Explainer.LangCase.GENITIVE:
                return "газа \"" + name_l + "\""
            return "газу \"" + name_l + "\""
            
        if name_l == name_r:
            if lang_case == Explainer.LangCase.GENITIVE:
                return "газа \"" + name_l + "\""
            return "газу \"" + name_l + "\""
                
        if lang_case == Explainer.LangCase.GENITIVE:
            return "газа \"" + name_l + "\"/\"" + name_r + "\""
        return "газу \"" + name_l + "\"/\"" + name_r + "\""

    #Генерация пояснения для ключа в терминах онтологии.
    #Этот метод ожидает, что на входе подаётся корректный ключ.
    @staticmethod
    def __generate_key_explanation(key: str, source_json: tuple, lang_case: LangCase):
        #Генерация описания в именительном падеже.
        if lang_case == Explainer.LangCase.NOMINATIVE:
            if key == "[0]":
                return "названия, главные компоненты и формулы газов и нормативные документы"
            elif key == "[1]":
                return "марки газов"
            elif key == "[2]":
                return "составы газов"
            elif re.match("^\\[0\\]\\[\\d+\\]$", key):
                return ("запись с информацией о названии, главном компоненте и формуле " + 
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE) + 
                        " и о нормативном документе")
            elif re.match("^\\[1\\]\\[\\d+\\]$", key):
                return "запись с информацией о марке " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[2\\]\\[\\d+\\]$", key):
                return "запись с информацией о составе " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.based_on$", key):
                return "название главного компонента " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.gas_name$", key):
                return "название " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.formula$", key):
                return "химическая формула " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.state_standard$", key):
                return "название нормативного документа, задающего требования к " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.DATIVE)
            elif re.match("^\\[1\\]\\[\\d+\\]\\.mark$", key):
                return "марка " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components$", key):
                return "компоненты " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.name$", key):
                return ("название " + re.search("\\d+(?=\\]\\.name$)", key)[0] + "-го компонента " +
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.formula$", key):
                return ("формула " + re.search("\\d+(?=\\]\\.formula$)", key)[0] + "-го компонента " +
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.value$", key):
                return ("объёмная долая/концентрация " + re.search("\\d+(?=\\]\\.value$)", key)[0] + "-го компонента " +
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.operation$", key):
                return ("операция сравнения для объёмных долей/концентрации " + re.search("\\d+(?=\\]\\.operation$)", key)[0] + 
                        "-го компонента " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            return "неизвестное (не описанное в онтологии) свойство " + key
        #Генерация описания в родительном падеже.
        else:
            if key == "[0]":
                return "названий, главных компонентов и формул газов и нормативных документов"
            elif key == "[1]":
                return "марок газов"
            elif key == "[2]":
                return "составов газов"
            elif re.match("^\\[0\\]\\[\\d+\\]$", key):
                return ("записей с информацией о названии, главном компоненте и формуле " + 
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE) + 
                        " и о нормативном документе")
            elif re.match("^\\[1\\]\\[\\d+\\]$", key):
                return "записей с информацией о марке " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[2\\]\\[\\d+\\]$", key):
                return "записей с информацией о составе " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.based_on$", key):
                return "названия главного компонента " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.gas_name$", key):
                return "названия " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.formula$", key):
                return "химические формулы " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[0\\]\\[\\d+\\]\\.state_standard$", key):
                return "названия нормативного документа, задающего требования к " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.DATIVE)
            elif re.match("^\\[1\\]\\[\\d+\\]\\.mark$", key):
                return "марки " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components$", key):
                return "компонентов " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE)
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.name$", key):
                return ("названия " + re.search("\\d+(?=\\]\\.name$)", key)[0] + "-го компонента " +
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.formula$", key):
                return ("формулы " + re.search("\\d+(?=\\]\\.formula$)", key)[0] + "-го компонента " +
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.value$", key):
                return ("объёмных долей/концентрации " + re.search("\\d+(?=\\]\\.value$)", key)[0] + "-го компонента " +
                        Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            elif re.match("^\\[2\\]\\[\\d+\\]\\.components\\[\\d+\\]\\.operation$", key):
                return ("операции сравнения для объёмных долей/концентрации " + re.search("\\d+(?=\\]\\.operation$)", key)[0] + 
                        "-го компонента " + Explainer.__generate_gas_name(int(re.search("(?<!^\\[)\\d+", key)[0]), source_json, Explainer.LangCase.GENITIVE))
            return "неизвестного (не описанного в онтологии) свойства " + key

    #Генерация пояснения к сообщению от компаратора с помощью данных из
    #словаря __KNOWLEDGEBASE (data driven generation).
    @staticmethod
    def __generate_message_explanation(message_id: str, params: list, source_json: tuple):
        #Выполнение команд, необходимых для генерации корректного пояснения.
        explanation_params = []
        param_index = 0

        for symbol in Explainer.__KNOWLEDGEBASE[message_id][3]:
            if symbol == 'j':
                if params[param_index] == 'l':
                    explanation_params.append("левой")
                elif params[param_index] == 'r':
                    explanation_params.append("правой")
                elif params[param_index] == 'b':
                    explanation_params.append("обеих")
                else:
                    return "ОШИБКА: Некорректное значение названия JSON-структуры: \"" + params[param_index] + "\"."
            elif symbol == 'k':
                explanation_params.append(Explainer.__generate_key_explanation(Explainer.__unescape_string(params[param_index]),
                                                                               source_json,
                                                                               Explainer.LangCase.GENITIVE))
            elif symbol == 'K':
                explanation_params.append(Explainer.__generate_key_explanation(Explainer.__unescape_string(params[param_index]), 
                                                                               source_json,
                                                                               Explainer.LangCase.NOMINATIVE))
            elif symbol == 'i':
                if param_index == len(params) - 1:
                    return "ОШИБКА: Внутренная ошибка при генерации пояснения: индекс входного параметра вышел за пределы списка."
                param_index += 1
            elif symbol == 'd':
                if param_index == 0:
                    return "ОШИБКА: Внутренная ошибка при генерации пояснения: индекс входного параметра вышел за пределы списка."
                param_index -= 1
            elif symbol == 'p':
                explanation_params.append(Explainer.__unescape_string(str(params[param_index])))
            else:
                return "ОШИБКА: Внутренняя ошибка при генерации пояснения: обнаружен неизвестный управляющий символ \"" + symbol + "\"."
        return Explainer.__KNOWLEDGEBASE[message_id][2].format(*explanation_params)

    #Данный метод генерирует пояснение к логам компаратора в терминах онтологии.
    #Метод ожидает, что сравнивались данные в упрощённом представлении (см. "gemma_json_generator.ipynb").
    @staticmethod
    def explain_log(log: str, source_json: tuple):
        if type(log) != str:
            return "ОШИБКА: Входные данные не являются строкой.\n"
    
        explanation = ""

        lines = log.split("\n")
        for i in lines:
            i = i.strip()
            if len(i) == 0 :
                continue

            validation_result = Explainer.__validate_string(i)
            if len(validation_result) > 0:
                explanation += validation_result + "\n"
                continue
            
            substrings = re.split("(?<!\\\\\\\\) ", i)

            message_id = substrings[0]
            params = substrings[1:len(substrings)] 
            param_count = len(params) 

            if message_id in Explainer.__KNOWLEDGEBASE.keys():
                if param_count == Explainer.__KNOWLEDGEBASE[message_id][1]:
                    if Explainer.__KNOWLEDGEBASE[message_id][0]:
                        if (#             Элемент     
                            #             массива                      Ключ словаря
                            #          <-----------> <---------------------------------------------->
                            #                           ^<буква>        
                            #                              или       Буква, цифра или экранированный
                            #                        <буква>.<буква>             символ
                            #                        <------------><-------------------------------->
                            re.match("^((\\[\\d+\\])|((^|(?<!^)\\.)([0-9a-zA-Zа-яА-Я]|\\\\\\\\.{1}|_)+))+$", params[0])):
                            explanation += Explainer.__generate_message_explanation(message_id, params, source_json) + "\n"
                        else:
                            explanation += "ОШИБКА: Синтаксическая ошибка в ключе сообщения \"" + message_id + "\".\n"
                    else:
                        explanation += Explainer.__generate_message_explanation(message_id, params, source_json) + "\n"
                else:
                    explanation += ("ОШИБКА: Некорректное количество параметров сообщения \"" + 
                                    message_id + "\": " + str(param_count) + " вместо " + 
                                    str(Explainer.__KNOWLEDGEBASE[message_id][1]) + ".\n")
            else:
                explanation += "ОШИБКА: Неизвестное сообщение \"" + i + "\".\n"

        return explanation

#############################
    
import pickle
import argparse
import sys

params = argparse.ArgumentParser(description=
"""Compares two JSON structures from the provided binary files generated by "pickle" module.""",
formatter_class=argparse.RawDescriptionHelpFormatter, epilog=
"""EXAMPLE

python json_comparator.py -l gemma_extracted_info.bin -r deepseek_extracted_info.bin -o explanation.txt

Compare JSON structures stored in "gemma_extracted_info.bin" and "deepseek_extracted_info.bin" and save the explanation of the comparison into the "explanation.txt".""")

params.add_argument("-l", "--left-json", type=argparse.FileType('rb'), help="The first input binary file generated by \"pickle\" module with JSON structure.");
params.add_argument("-r", "--right-json", type=argparse.FileType('rb'), help="The second input binary file generated by \"pickle\" module with JSON structure.");
params.add_argument("-o", "--output", type=argparse.FileType('w',encoding="utf-8"), help="An output text file name. If the parameter is missing, the name will default to \"output.txt\".");

params = params.parse_args()

if not params.left_json:
    sys.exit("The first input file is not specified. Exiting.")
if not params.right_json:
    sys.exit("The second input file is not specified. Exiting.")

json_l = pickle.loads(params.left_json.read())
json_r = pickle.loads(params.right_json.read())

output_file = params.output if params.output else open("output.txt", "w", encoding="utf-8")

log = UJSONC.compare_json(json_l, json_r)
if log[0]:
    output_file.write("Сравниваемые JSON-структуры совпадают.")
else:
    output_file.write("Сравниваемые JSON-структуры не совпадают.\n")
    output_file.write("Логи компаратора:\n")
    output_file.write(log[1])
    output_file.write("Пояснение:\n")
    output_file.write(Explainer.explain_log(log[1], (json_l, json_r)))
output_file.close