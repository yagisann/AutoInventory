# inventory_list_detail_{ダウンロード日時}.csv のデータ取り出し

from .ddn import DictDotNotation as ddn
from . import config
import csv, os, pickle
import datetime


def get_inventory_reagent_info(inventory_list_path):
    with open(inventory_list_path, "r") as f:
        reader = csv.reader(f)
        data = [i for i in reader if len(i)==136]
    all_reagent = ddn()
    for i in data[1:]:
        if i[0] == "":
            continue
        partial_reagent = ddn({
            "name": i[0],
            "maker": i[1],
            "grade": i[2],
            "cas": i[3],
            "quantity": i[4],
            "quantity_unit": i[5],
            "iaso": i[10],
            "alias": [name for name in i[16:18] if name!=""], # 別名
            "storage_condition": i[30],
            "is_weight_management": i[59]=="重量管理",
            "is_capacity_management": i[59]=="容量管理",
            "control_method_unit": i[61],
            "sds": i[74],
            "storage_location": "/".join([loc for loc in i[89:93] if loc!=""]),
            "is_sealed": i[101]=="●",
            "is_using": i[104]=="●",
            "expire_at": datetime.datetime.strptime(i[100], "%Y/%m/%d"),
            "is_inventory_registered": i[11]!="",
            "is_checked": False,
            "weight": ""
        })
        all_reagent[i[10]] = partial_reagent
        #exec(f"all_reagent.{i[10]} = partial_reagent")
    return all_reagent

def get_stock_reagent_info(stock_list_path):
    with open(stock_list_path, "r") as f:
        reader = csv.reader(f)
        data = [i for i in reader if len(i)==133]
    all_reagent = ddn()
    for i in data[1:]:
        if i[0] == "":
            continue
        partial_reagent = ddn({
            "name": i[0],
            "maker": i[1],
            "grade": i[2],
            "cas": i[3],
            "quantity": i[4],
            "quantity_unit": i[5],
            "iaso": i[6],
            "is_sealed": i[8]=="●",
            "storage_location": i[12].replace("／", "/"),
            "is_checked": False
        })
        all_reagent[i[6]] = partial_reagent
        #exec(f"all_reagent.{i[6]} = partial_reagent")
    return all_reagent

def compare_reagent_info(inventory_list, stock_list):
    """ returns reagent info not in inventory_list but in stock_list """
    if len(inventory_list)==len(stock_list):
        return ddn()
    
    inv_key = inventory_list.keys()
    not_subject_to_inventory = ddn()
    for code, reagent in stock_list.items():
        if not code in inv_key:
            not_subject_to_inventory[code] = reagent
            #exec(f"not_subject_to_inventory.{code} = reagent")
    return not_subject_to_inventory

def generate_reagent_info_from(inventory_list_path, stock_list_path, project_path):
    inventory_list = get_inventory_reagent_info(inventory_list_path)
    stock_list = get_stock_reagent_info(stock_list_path)
    
    not_subject_to_inventory = compare_reagent_info(inventory_list, stock_list)
    save_to("not_subject_to_inventory_list", not_subject_to_inventory, config.s_csv_header, project_path)
    save_to("inventory_list", inventory_list, config.i_csv_header, project_path)
    return inventory_list, not_subject_to_inventory

def restore_reagent_info(project_path):
    with open(project_path+"/result/inventory_list.reagent", "rb") as f:
        inventory_list = ddn(pickle.load(f))
    with open(project_path+"/result/not_subject_to_inventory_list.reagent", "rb") as f:
        not_subject_to_inventory = ddn(pickle.load(f))
    return inventory_list, not_subject_to_inventory

def save_to(name, obj, header, project_path):
    h = header
    os.makedirs(project_path+"/result", exist_ok=True)
    with open(f"{project_path}/result/{name}.reagent", "wb") as f:
        pickle.dump(obj.__dict__, f)
    c = [list(h.values())]
    for i in obj.values():
        command = f"[{', '.join(['i.'+j for j in h.keys()])}]"
        c.append(["〇" if i is True else "" if i is False else i for i in eval(command)])
    with open(f"{project_path}/result/{name}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(c)
    