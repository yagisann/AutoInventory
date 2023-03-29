from pathlib import Path
from tabulate import tabulate
import reagents, config, iaso_wrapper
import pickle, os, traceback

class AutoInventory:
    
    def __init__(self, iaso_id, iaso_pw):
        self.doc = "https://www.notion.so/yagi-t/789dd52e94614a9896e20507f329d22c#96d2e99d968e4b0aa92b276f329592f7"
        self.iaso_id = iaso_id
        self.iaso_pw = iaso_pw
        self.driver = None
    
    def start(self, name):
        # validation check
        if not os.path.exists(name):
            raise RuntimeError(f"フォルダ '{name}' が存在しません。")
        if os.path.exists(name+"/result/inventory_list.reagent"):
            raise RuntimeError(f"'{name}' にはすでに棚卸情報があります。棚卸を再開するには、AutoInventory().load_from(directory_name) を使用してください。")
        inv_list_list = list(Path(name).glob(r"inventory_list_detail_*.csv"))
        stk_list_list = list(Path(name).glob(r"stock_list_detail_*.csv"))
        if len(inv_list_list) != 1:
            raise RuntimeError(f"フォルダ '{name}' に、'inventory_list_detail_*.csv' が存在しないか、複数存在します。最新のもののみを使用してください。")
        if len(stk_list_list) != 1:
            raise RuntimeError(f"フォルダ '{name}' に、'stock_list_detail_*.csv' が存在しないか、複数存在します。最新のもののみを使用してください。")
        
        self.project_name = name
        self.inv_reagents, self.not_inv_reagents = reagents.generate_reagent_info_from(inv_list_list[0], stk_list_list[0], self.project_name)
        return self
        
    def load_from(self, name):
        # validation check
        if not os.path.exists(name+"/result"):
            raise RuntimeError(f"フォルダ '{name}' には棚卸情報がありません。棚卸を開始するには、AutoInventory().start(directory_name) を使用してください。")
        self.project_name = name
        self.inv_reagents, self.not_inv_reagents = reagents.restore_reagent_info(name)
        return self
    
    def search(self, IASOcode, check=False, print_code=True):
        if print_code:
            print("IASOバーコードナンバー: "+IASOcode)
        if IASOcode in self.inv_reagents.__dict__:
            hit = self.inv_reagents[IASOcode]
            tmpdict = [{
                "試薬名": hit.name,
                "メーカー": hit.maker,
                "グレード": hit.grade,
                "量": hit.quantity+hit.quantity_unit,
                "IASOナンバー": hit.iaso,
                "保管場所": hit.storage_location,
                "棚卸処理": "✓" if hit.is_inventory_registered else "-",
                "実在確認": "✓" if hit.is_checked else "-",
                "管理方法": "重量" if hit.is_weight_management else "容量" if hit.is_capacity_management else "-",
                "実測値": hit.weight,
                "管理単位": hit.control_method_unit
            }]
            print(tabulate(tmpdict, headers="keys"))
            if check:
                hit.is_checked = True
                if hit.is_weight_management or hit.is_capacity_management:
                    print("重量or容量管理試薬です。管理単位: "+hit.control_method_unit)
                    hit.weight = input("重量or容量を、単位を除いて書いてください: ")
        elif IASOcode in self.not_inv_reagents.__dict__:
            hit = self.not_inv_reagents[IASOcode]
            print("棚卸対象外試薬です。")
            tmpdict = [{
                "試薬名": hit.name,
                "メーカー": hit.maker,
                "グレード": hit.grade,
                "量": hit.quantity+hit.quantity_unit,
                "IASOナンバー": hit.iaso,
                "保管場所": hit.storage_location,
                "実在確認": "✓" if hit.is_checked else "-"
            }]
            print(tabulate(tmpdict, headers="keys"))
            if check:
                hit.is_checked = True
        else:
            print("試薬情報が見つかりませんでした")
        print("")
    
    # 実在性チェック
    def check(self, IASOcode):
        self.search(IASOcode, check=True, print_code=False)
    
    # 現在の状況を保存
    def save(self):
        reagents.save_to("not_subject_to_inventory_list", self.not_inv_reagents, config.s_csv_header, self.project_name)
        reagents.save_to("inventory_list", self.inv_reagents, config.i_csv_header, self.project_name)
        return self
    
    # webdriver起動
    def IASO_login(self):
        self.driver = iaso_wrapper.IASO_login(self.iaso_id, self.iaso_pw)
    
    # webdriver終了
    def IASO_logout(self):
        if self.driver is None:
            return
        iaso_wrapper.IASO_logout(self.driver)
    
    # 存在確認ができている、すべての試薬を棚卸登録する
    def regist_inventory(self):
        if self.driver is None:
            raise RuntimeError("Webブラウザが起動していません。先に AutoInventory().IASO_login() を実行してください。")
        try:
            registered = 0
            for code, reagent in self.inv_reagents.items():
                # 実物確認済みで棚卸未処理で持ち出し中でないものは、通常通り棚卸が可能
                if all([reagent.is_checked, not reagent.is_inventory_registered, not reagent.is_using]):
                    iaso_wrapper.IASO_register(self.driver, reagent)
                    reagent.is_inventory_registered = True
                    print(f"{code} は正常に棚卸登録されました。")
                    registered += 1
        except Exception as e:
            print("棚卸登録中にエラーが発生しました。今までの情報を保存します。")
            print(traceback.format_exc())
        finally:
            print(f"{registered} 本の試薬が正常に棚卸登録されました。")
            self.save()
    
    # IASO上でも処理を一括で行う
    def iaso_patch(self):
        self.IASO_login()
        self.regist_inventory()
        self.IASO_logout()
                    
        