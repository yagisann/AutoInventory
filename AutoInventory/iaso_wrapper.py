# webdriver.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import datetime

# ロードが終わるまで待つ設定
def ExCond(driver, xpath, kind, sec=10):
    wait = WebDriverWait(driver, sec)
    if kind == "vis":
        wait.until(expected_conditions.visibility_of_element_located((By.XPATH, xpath)))
    elif kind == "clk":
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
        driver.find_element(By.XPATH, xpath).click()
    else:
        return
    
# loginを行う関数
def IASO_login(ID, PW):
    # Chromeを自動制御モードで開き、iasoに接続する
    options = Options()
    new_driver = ChromeDriverManager().install()
    service = ChromeService(executable_path=new_driver)
    driver = webdriver.Chrome(service=service, options=options)
    driver.minimize_window()
    driver.maximize_window()
    driver.get("http://133.86.49.11/iasor7/fw/FW0000/")
    
    # ロードが終わるまで待つ
    ExCond(driver, '/html/body/div/section/form/div[1]/input', "vis")
    
    # IDとPWを入力して、ログインボタンを押す
    loginID = driver.find_element(By.XPATH, '/html/body/div/section/form/div[1]/input')
    loginID.send_keys(ID)
    loginPW = driver.find_element(By.XPATH, '/html/body/div/section/form/div[2]/input')
    loginPW.send_keys(PW)
    driver.find_element(By.XPATH, '/html/body/div/section/form/button/span').click()
    
    # 棚卸画面まで遷移する
    ExCond(driver, '//*[text()="棚卸"]', "clk")
    ExCond(driver, '//*[text()="棚卸入力"]', "clk")
    
    # ドライバーを返す
    return driver

# logoutを行う関数
def IASO_logout(driver):
    ExCond(driver, '/html/body/header/div[2]/nav/a/span', "clk")
    driver.close()
    return


# 一回分の棚卸
def IASO_register(driver, reagent_info):
    r = reagent_info
    
    IASO_No_input = driver.find_element(By.XPATH, '/html/body/div[2]/form/section[1]/ul/li[2]/input')
    IASO_No_input.send_keys(r.iaso)
    IASO_No_input.send_keys(Keys.ENTER)
    
    # 重量or容量管理の場合
    if r.is_weight_management or r.is_capacity_management:
        wt_input = driver.find_element(By.XPATH, '/html/body/div[2]/form/section[2]/table/tbody/tr[1]/td[2]/ul/li[1]/input')
        wt_input.send_keys(r.weight)
    
    # Enterボタン
    ExCond(driver, "/html/body/div[1]/ul/li/button", "clk")
    # 重量or容量管理の場合、Enterで、「異常増減を検出しました」と出てくることがあるのでそれを消す
    if r.is_weight_management or r.is_capacity_management:
        ExCond(driver, "/html/body/div[5]/div[2]/div/div/div/p", "vis")
        if driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div/div/div/p").text == "異常増減を検出しました。":
            ExCond(driver, "/html/body/div[5]/div[3]/div/button", "clk")
    # 使用期限切れの表示を閉じる
    if r.expire_at < datetime.datetime.now():
        ExCond(driver, "/html/body/div[5]/div[3]/div/button", "clk")
    # 棚卸登録確認画面で「はい」を押す
    ExCond(driver, "/html/body/div[5]/div[3]/div/button[1]", "clk")
    # 棚卸登録完了画面を閉じる
    ExCond(driver, "/html/body/div[5]/div[3]/div/button", "clk")
    return
