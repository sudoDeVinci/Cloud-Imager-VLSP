def get_QNH_hpa(location:str) -> int:
    """
    Get the sea level pressure for a given location in Kronobergs Lan.
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    browser = webdriver.Chrome(options=options) 
    browser.get("https://meteologix.com/se/observations/kronoberg/pressure-qnh/20240225-1100z.html") 
    
    results = browser.find_elements(By.CLASS_NAME, "o-4")
    
    result = tuple(result.get_property("title").lower() for result in results if location in result.get_property("title").lower())
    if len(result) == 0:
        return None

    out = result[0].split(" | ")
    print(out)
    
    try:
        out[0] = int(out[0].split(" ")[0])
    except Exception:
        return None
    
    print(out)
    browser.close()

    return out[0]

if __name__ == "__main__":
    # Example: Getting vaxjo weather.
    get_QNH_hpa("vaxjo")