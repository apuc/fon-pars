import argparse
import datetime
import sys
from collections import namedtuple
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_match(search_title: str, search_coeffs: list, filename="results.txt"):
    Result = namedtuple('Result', 'title coeffs')
    result = Result(None, None)

    url = "https://www.fonbet.ru/#!/live"

    options = webdriver.FirefoxOptions()
    options.headless = True

    driver = None

    try:
        driver = webdriver.Firefox(options=options)

        driver.get(url)

        table_rows = WebDriverWait(driver, 120).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "table__row")))
        for row in table_rows:
            try:
                title = str(row.find_element_by_class_name("table__match-title-text").text)
                if search_title == title:
                    elem_coeffs = row.find_elements_by_class_name("_type_btn")
                    coeffs = OrderedDict()
                    for coeff in search_coeffs:
                        coeffs[coeff] = elem_coeffs[coeff - 1].text
                        if not coeffs[coeff]:
                            coeffs[coeff] = "Пусто"
                    result = Result(title, coeffs)
                    break
            except NoSuchElementException:
                continue
    except Exception as e:
        pass
    finally:
        if driver is not None:
            driver.quit()

    f = open(filename, "a+", newline=None)
    if result.title:
        print(str(datetime.datetime.now()) + ' - ' + result.title + " : " +
              ', '.join(['{} - {}'.format(k, v) for k, v in result.coeffs.items()]), file=f)
    else:
        print(str(datetime.datetime.now()) + ' - Not found', file=f)
    f.flush()
    f.close()


if __name__ == "__main__":
    args = sys.argv[1:]

    parser = argparse.ArgumentParser(prog='parser.py',
                                     description='Find 1st player coef by title on https://www.fonbet.ru/#!/live.')
    parser.add_argument('--title', dest='title', type=str, default='', help='string with match title. is required')
    parser.add_argument('--coeffs', dest='coeffs', type=int, nargs='+', default=[1],
                        help='integers corresponding to columns of coeffs. '
                             'Fora and Dop are ignored when calculating index. by default = 1')
    parsed = parser.parse_intermixed_args(args)

    if not parsed.title:
        print("Title wasn't supplied")
        exit(-1)
    search_match(parsed.title, parsed.coeffs)
    exit(1)
