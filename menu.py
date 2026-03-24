"""
╔══════════════════════════════════════════════════════════════╗
║         Restaurant Menu Management System                    ║
║         ระบบจัดการเมนูอาหาร                                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import os
import unicodedata
from datetime import datetime


# ─────────────────────────────────────────────
#  DATA LAYER  (เก็บข้อมูลใน JSON file)
# ─────────────────────────────────────────────

DATA_FILE = "menu_data.json"

CATEGORIES = {
    "1": "อาหารจานหลัก",
    "2": "อาหารเรียกน้ำย่อย",
    "3": "เครื่องดื่ม",
    "4": "ของหวาน",
    "5": "อาหารจานเดียว",
}


def load_data() -> list[dict]:
    """โหลดข้อมูลจากไฟล์ JSON"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(menu_list: list[dict]) -> None:
    """บันทึกข้อมูลลงไฟล์ JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(menu_list, f, ensure_ascii=False, indent=2)


def next_id(menu_list: list[dict]) -> int:
    """สร้าง ID อัตโนมัติ"""
    return max((item["id"] for item in menu_list), default=0) + 1


# ─────────────────────────────────────────────
#  THAI TEXT PADDING HELPER
# ─────────────────────────────────────────────

def visual_width(text: str) -> int:
    """คำนวณความกว้างจริงของข้อความ (รองรับภาษาไทย/จีน/ญี่ปุ่น)"""
    width = 0
    for ch in text:
        cp = ord(ch)
        # ตรวจสอบว่าเป็นภาษาไทยหรือไม่ (U+0E00 ถึง U+0E7F)
        if 0x0E00 <= cp <= 0x0E7F:
            # กลุ่มสระจม/ลอย และวรรณยุกต์ ที่ไม่มีความกว้าง (Zero-width characters)
            if cp in (0x0E31, 0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E38, 0x0E39, 0x0E3A, 
                      0x0E47, 0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C, 0x0E4D, 0x0E4E):
                width += 0
            else:
                width += 1  # พยัญชนะและสระปกติกว้าง 1 คอลัมน์
        else:
            eaw = unicodedata.east_asian_width(ch)
            width += 2 if eaw in ("W", "F") else 1
    return width


def thai_ljust(text: str, width: int) -> str:
    """จัด left-align โดยใช้ visual width แทน len()"""
    pad = width - visual_width(text)
    return text + " " * max(pad, 0)


def thai_rjust(text: str, width: int) -> str:
    """จัด right-align โดยใช้ visual width แทน len()"""
    pad = width - visual_width(text)
    return " " * max(pad, 0) + text


# ─────────────────────────────────────────────
#  CORE OPERATIONS  (CRUD)
# ─────────────────────────────────────────────

def add_menu(menu_list: list[dict]) -> None:
    """เพิ่มเมนูอาหารใหม่"""
    print("\n" + "─" * 50)
    print("  เพิ่มเมนูอาหารใหม่")
    print("─" * 50)

    name = input("ชื่อเมนู            : ").strip()
    if not name:
        print("  [!] ชื่อเมนูต้องไม่ว่างเปล่า")
        return

    if any(item["name"].lower() == name.lower() for item in menu_list):
        print(f"  [!] เมนู '{name}' มีอยู่ในระบบแล้ว")
        return

    description = input("รายละเอียด          : ").strip()

    while True:
        try:
            price = float(input("ราคา (บาท)          : "))
            if price < 0:
                raise ValueError
            break
        except ValueError:
            print("  [!] กรุณาระบุราคาที่ถูกต้อง (ตัวเลขมากกว่า 0)")

    print("\n  หมวดหมู่ที่มี:")
    for key, val in CATEGORIES.items():
        print(f"    [{key}] {val}")
    cat_key = input("เลือกหมวดหมู่ (1-5)  : ").strip()
    category = CATEGORIES.get(cat_key, "อื่น ๆ")

    available_input = input("พร้อมขาย? (y/n)     : ").strip().lower()
    available = available_input != "n"

    new_item = {
        "id": next_id(menu_list),
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "available": available,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    menu_list.append(new_item)
    bubble_sort_by_name(menu_list)
    save_data(menu_list)
    print(f"\n  [OK] เพิ่มเมนู '{name}' เรียบร้อยแล้ว (ID: {new_item['id']})")


def delete_menu(menu_list: list[dict]) -> None:
    """ลบเมนูอาหาร"""
    print("\n" + "─" * 50)
    print("  ลบเมนูอาหาร")
    print("─" * 50)

    if not menu_list:
        print("  [!] ไม่มีเมนูในระบบ")
        return

    display_all(menu_list)

    try:
        menu_id = int(input("\nระบุ ID ที่ต้องการลบ : "))
    except ValueError:
        print("  [!] ID ไม่ถูกต้อง")
        return

    item = next((m for m in menu_list if m["id"] == menu_id), None)
    if not item:
        print(f"  [!] ไม่พบเมนู ID {menu_id}")
        return

    confirm = input(f"ยืนยันลบ '{item['name']}'? (y/n) : ").strip().lower()
    if confirm == "y":
        menu_list.remove(item)
        save_data(menu_list)
        print(f"  [OK] ลบเมนู '{item['name']}' เรียบร้อยแล้ว")
    else:
        print("  ยกเลิกการลบ")


def edit_menu(menu_list: list[dict]) -> None:
    """แก้ไขเมนูอาหาร"""
    print("\n" + "─" * 50)
    print("  แก้ไขเมนูอาหาร")
    print("─" * 50)

    if not menu_list:
        print("  [!] ไม่มีเมนูในระบบ")
        return

    display_all(menu_list)

    try:
        menu_id = int(input("\nระบุ ID ที่ต้องการแก้ไข : "))
    except ValueError:
        print("  [!] ID ไม่ถูกต้อง")
        return

    item = next((m for m in menu_list if m["id"] == menu_id), None)
    if not item:
        print(f"  [!] ไม่พบเมนู ID {menu_id}")
        return

    print(f"\n  แก้ไขเมนู: {item['name']}  (กด Enter เพื่อคงค่าเดิม)")

    new_name = input(f"  ชื่อเมนู [{item['name']}]          : ").strip()
    if new_name:
        item["name"] = new_name

    new_desc = input(f"  รายละเอียด [{item['description']}] : ").strip()
    if new_desc:
        item["description"] = new_desc

    new_price = input(f"  ราคา [{item['price']} บาท]            : ").strip()
    if new_price:
        try:
            item["price"] = float(new_price)
        except ValueError:
            print("  [!] ราคาไม่ถูกต้อง คงค่าเดิม")

    print("\n  หมวดหมู่ที่มี:")
    for key, val in CATEGORIES.items():
        print(f"    [{key}] {val}")
    new_cat_key = input(f"  หมวดหมู่ [{item['category']}] (1-5) : ").strip()
    if new_cat_key in CATEGORIES:
        item["category"] = CATEGORIES[new_cat_key]

    avail_str = "y" if item["available"] else "n"
    new_avail = input(f"  พร้อมขาย? [{avail_str}] (y/n)        : ").strip().lower()
    if new_avail in ("y", "n"):
        item["available"] = new_avail == "y"

    item["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_data(menu_list)
    print(f"\n  [OK] แก้ไขเมนู '{item['name']}' เรียบร้อยแล้ว")


def search_menu(menu_list: list[dict]) -> None:
    """ค้นหาเมนูอาหาร"""
    print("\n" + "─" * 50)
    print("  ค้นหาเมนูอาหาร")
    print("─" * 50)
    print("  ค้นหาโดย:")
    print("    [1] ชื่อเมนู")
    print("    [2] หมวดหมู่")
    print("    [3] ช่วงราคา")
    print("    [4] สถานะพร้อมขาย")

    choice = input("\n  เลือกวิธีค้นหา : ").strip()

    results = []

    if choice == "1":
        keyword = input("  คีย์เวิร์ด : ").strip().lower()
        results = [m for m in menu_list if keyword in m["name"].lower()
                   or keyword in m["description"].lower()]

    elif choice == "2":
        print("\n  หมวดหมู่:")
        for key, val in CATEGORIES.items():
            print(f"    [{key}] {val}")
        cat_key = input("  เลือกหมวดหมู่ : ").strip()
        cat = CATEGORIES.get(cat_key)
        if cat:
            results = [m for m in menu_list if m["category"] == cat]
        else:
            print("  [!] หมวดหมู่ไม่ถูกต้อง")
            return

    elif choice == "3":
        try:
            min_p = float(input("  ราคาต่ำสุด (บาท) : "))
            max_p = float(input("  ราคาสูงสุด (บาท) : "))
            results = [m for m in menu_list if min_p <= m["price"] <= max_p]
        except ValueError:
            print("  [!] ราคาไม่ถูกต้อง")
            return

    elif choice == "4":
        avail_input = input("  พร้อมขาย? (y/n) : ").strip().lower()
        avail = avail_input != "n"
        results = [m for m in menu_list if m["available"] == avail]

    else:
        print("  [!] ตัวเลือกไม่ถูกต้อง")
        return

    print(f"\n  พบ {len(results)} รายการ")
    if results:
        display_all(results)
    else:
        print("  ─ ไม่พบเมนูที่ตรงกับเงื่อนไข ─")


# ─────────────────────────────────────────────
#  DISPLAY HELPERS
# ─────────────────────────────────────────────

def display_all(menu_list: list[dict]) -> None:
    """แสดงรายการเมนูทั้งหมดในรูปแบบตาราง"""
    if not menu_list:
        print("\n  ─ ไม่มีเมนูในระบบ ─")
        return

    # คำนวณความกว้าง column จาก data จริง (dynamic)
    COL_ID    = max(2, max(len(str(m["id"])) for m in menu_list))
    COL_NAME  = max(visual_width("ชื่อเมนู"),  max(visual_width(m["name"])     for m in menu_list))
    COL_CAT   = max(visual_width("หมวดหมู่"), max(visual_width(m["category"]) for m in menu_list))
    COL_PRICE = 9
    COL_STAT  = 10

    # header
    h_id    = thai_rjust("ID",       COL_ID)
    h_name  = thai_ljust("ชื่อเมนู",  COL_NAME)
    h_cat   = thai_ljust("หมวดหมู่", COL_CAT)
    h_price = thai_rjust("ราคา",     COL_PRICE)
    h_stat  = thai_ljust("สถานะ",    COL_STAT)
    header  = f"{h_id}  {h_name}  {h_cat}  {h_price}  {h_stat}  รายละเอียด"

    sep_width = COL_ID + 2 + COL_NAME + 2 + COL_CAT + 2 + COL_PRICE + 2 + COL_STAT + 2 + 20

    print()
    print("  " + header)
    print("  " + "─" * sep_width)

    for item in menu_list:
        status   = "พร้อมขาย" if item["available"] else "หยุดขาย "
        desc_short = (item["description"][:16] + "...") if visual_width(item["description"]) > 18 else item["description"]

        col_id    = thai_rjust(str(item["id"]),    COL_ID)
        col_name  = thai_ljust(item["name"],        COL_NAME)
        col_cat   = thai_ljust(item["category"],    COL_CAT)
        col_price = thai_rjust(f"{item['price']:.2f}B", COL_PRICE)
        col_stat  = thai_ljust(status,              COL_STAT)

        print(f"  {col_id}  {col_name}  {col_cat}  {col_price}  {col_stat}  {desc_short}")
    print()


def show_menu_detail(menu_list: list[dict]) -> None:
    """แสดงรายละเอียดเมนูแบบเต็ม"""
    print("\n" + "─" * 50)
    print("  แสดงรายละเอียดเมนู")
    print("─" * 50)

    display_all(menu_list)

    try:
        menu_id = int(input("ระบุ ID ที่ต้องการดู : "))
    except ValueError:
        print("  [!] ID ไม่ถูกต้อง")
        return

    item = next((m for m in menu_list if m["id"] == menu_id), None)
    if not item:
        print(f"  [!] ไม่พบเมนู ID {menu_id}")
        return

    print("\n" + "=" * 40)
    print(f"  รหัสเมนู   : {item['id']}")
    print(f"  ชื่อ        : {item['name']}")
    print(f"  รายละเอียด : {item['description']}")
    print(f"  ราคา       : {item['price']:.2f} บาท")
    print(f"  หมวดหมู่   : {item['category']}")
    print(f"  สถานะ      : {'พร้อมขาย' if item['available'] else 'หยุดขาย'}")
    print(f"  สร้างเมื่อ  : {item['created_at']}")
    print(f"  แก้ไขล่าสุด : {item['updated_at']}")
    print("=" * 40)


def show_summary(menu_list: list[dict]) -> None:
    """แสดงสรุปสถิติเมนู"""
    total     = len(menu_list)
    available = sum(1 for m in menu_list if m["available"])
    avg_price = sum(m["price"] for m in menu_list) / total if total else 0

    print("\n" + "=" * 40)
    print("  สรุปข้อมูลเมนู")
    print("=" * 40)
    print(f"  เมนูทั้งหมด    : {total} รายการ")
    print(f"  พร้อมขาย      : {available} รายการ")
    print(f"  หยุดขาย       : {total - available} รายการ")
    print(f"  ราคาเฉลี่ย    : {avg_price:.2f} บาท")

    if menu_list:
        cheapest = min(menu_list, key=lambda m: m["price"])
        priciest = max(menu_list, key=lambda m: m["price"])
        print(f"  ราคาต่ำสุด    : {cheapest['price']:.2f} บาท ({cheapest['name']})")
        print(f"  ราคาสูงสุด    : {priciest['price']:.2f} บาท ({priciest['name']})")

    print("\n  จำนวนตามหมวดหมู่:")
    cat_counts: dict[str, int] = {}
    for m in menu_list:
        cat_counts[m["category"]] = cat_counts.get(m["category"], 0) + 1
    for cat, count in sorted(cat_counts.items()):
        print(f"    - {thai_ljust(cat, 24)}: {count} รายการ")
    print("=" * 40)

# ─────────────────────────────────────────────
#  SORTING  (เรียงลำดับ)
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  SORTING  (เรียงลำดับ)
# ─────────────────────────────────────────────

def bubble_sort_by_name(menu_list: list[dict]) -> None:
    """เรียงลำดับเมนูตามชื่อ ก-ฮ / A-Z ด้วย Bubble Sort (ใช้ภายในอัตโนมัติ)"""
    n = len(menu_list)
    for i in range(n):
        for j in range(0, n - i - 1):
            if menu_list[j]["name"] > menu_list[j + 1]["name"]:
                menu_list[j], menu_list[j + 1] = menu_list[j + 1], menu_list[j]


# ─────────────────────────────────────────────
#  MAIN MENU  (เมนูหลัก)
# ─────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║        Restaurant Menu Management System                     ║
║        ระบบจัดการเมนูอาหาร v1.0                             ║
╚══════════════════════════════════════════════════════════════╝"""

MAIN_MENU = """
  +-------------------------------------+
     [1]  เพิ่มเมนูอาหาร                   
     [2]  ลบเมนูอาหาร                    
     [3]  แก้ไขเมนูอาหาร                  
     [4]  ค้นหาเมนูอาหาร                  
     [5]  แสดงเมนูทั้งหมด                 
     [6]  ดูรายละเอียดเมนู                 
     [0]  ออกจากโปรแกรม                 
  +-------------------------------------+
  เลือกเมนู : """


def main() -> None:
    print(BANNER)
    menu_list = load_data()
    print(f"\n  โหลดข้อมูล {len(menu_list)} รายการจากระบบ")

    while True:
        choice = input(MAIN_MENU).strip()

        if choice == "1":
            add_menu(menu_list)
        elif choice == "2":
            delete_menu(menu_list)
        elif choice == "3":
            edit_menu(menu_list)
        elif choice == "4":
            search_menu(menu_list)
        elif choice == "5":
            print("\n" + "─" * 50)
            print("  เมนูอาหารทั้งหมด")
            print("─" * 50)
            display_all(menu_list)
        elif choice == "6":
            show_menu_detail(menu_list)
        elif choice == "0":
            print("\n  ขอบคุณที่ใช้งานระบบ ลาก่อน!\n")
            break
        else:
            print("  [!] กรุณาเลือกเมนู 0-6")


if __name__ == "__main__":
    main()