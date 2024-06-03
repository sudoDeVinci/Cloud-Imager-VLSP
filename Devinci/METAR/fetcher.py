from selenium import webdriver
from selenium.webdriver.common.by import By


def get_QNH_hpa(location:str) -> int:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")

    browser = webdriver.Chrome(options=options) 
    browser.get("https://meteologix.com/se/observations/kronoberg/pressure-qnh/20240225-1100z.html") 

    results = browser.find_elements(By.CLASS_NAME, "o-4")

    result = tuple(result.get_property("title") for result in results if location.lower() in result.get_property("title").lower())
    if len(result) == 0:
        return None

    out = result[0].split(" | ")
    # print(out)

    try:
        out[0] = int(out[0].split(" ")[0])
    except Exception:
        return None

    print(out)
    browser.close()

    return out[0]

if __name__ == "__main__":
    get_QNH_hpa("Vaxjo")