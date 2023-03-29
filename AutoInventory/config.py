from .ddn import DictDotNotation as ddn

i_csv_header = ddn({
    "name": "試薬名",
    "maker": "メーカー",
    "grade": "グレード",
    "cas": "CAS No.",
    "quantity": "量",
    "quantity_unit": "量単位",
    "iaso": "IASOバーコードナンバー",
    "is_weight_management": "重量管理",
    "is_capacity_management": "容量管理",
    "control_method_unit": "管理単位",
    "storage_location": "保管場所",
    "expire_at": "使用期限",
    "is_sealed": "未開封",
    "is_using": "持ち出し中",
    "is_inventory_registered": "棚卸処理済み",
    "is_checked": "実物確認済み",
    "weight": "実測重量or容量"
})

s_csv_header = ddn({
    "name": "試薬名",
    "maker": "メーカー",
    "grade": "グレード",
    "cas": "CAS No.",
    "quantity": "量",
    "quantity_unit": "量単位",
    "iaso": "IASOバーコードナンバー",
    "storage_location": "保管場所",
    "is_sealed": "未開封",
})

print_header = ddn({
    "name": "試薬名",
    "maker": "メーカー",
    "grade": "グレード",
    "quantity_unit": "量単位",
    "iaso": "IASOナンバー",
    "storage_location": "保管場所",
    "is_weight_management": "重量管理",
    "is_capacity_management": "容量管理",
    "control_method_unit": "管理単位",
    "storage_location": "保管場所",
    "is_inventory_registered": "棚卸処理済み",
    "is_checked": "実物確認済み",
    "weight": "実測値"
})
