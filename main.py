from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
from utils.Constantes import YEARS, MONTHS
import os

def collect_state_list(driver): 
    try:
        select_state = Select(driver.find_element(By.ID, 'uf'))
        states = [option.text for option in select_state.options[1:]]
        return states
    except Exception as e:
        print(f"Erro ao coletar Estados: {e}")

def collect_city_list(driver): 
    try:
        select_city = Select(driver.find_element(By.ID, 'mun'))
        cities = [option.text for option in select_city.options[1:]]
        return cities
    except Exception as e:
        print(f"Erro ao coletar Municípios: {e}")

def select_state(driver, state): 
    try:
        select_state = Select(driver.find_element(By.ID, 'uf'))
        select_state.select_by_visible_text(state)
        time.sleep(1)
        return state
    except Exception as e:
        print(f"Erro ao selecionar state: {e}")

def select_city(driver, city): 
    try:
        select_city = Select(driver.find_element(By.ID, 'mun'))
        select_city.select_by_visible_text(city)
        return city
    except Exception as e:
        print(f"Erro ao selecionar Município: {e}")

def select_radio(driver): 
    try:
        radio_element = driver.find_element(By.XPATH, '//input[@type="radio" and @value="ocupacional" and @name="YCnivel"]')
        if not radio_element.is_selected():
            radio_element.click()
    except Exception as e:
        print(f"Erro ao selecionar radio button: {e}")

def select_date(driver, year, month): 
    try:
        select_ano_inicio = Select(driver.find_element(By.ID, 'ano_inicio'))
        select_ano_inicio.select_by_visible_text(year)
        select_ano_fim = Select(driver.find_element(By.ID, 'ano_fim'))
        select_ano_fim.select_by_visible_text(year)

        select_mes_inicio = Select(driver.find_element(By.ID, 'mes_inicio_cons'))
        select_mes_fim = Select(driver.find_element(By.ID, 'mes_fim_cons'))
        select_mes_inicio.select_by_value(month)
        select_mes_fim.select_by_value(month)
    except Exception as e:
        print(f"Erro ao selecionar data: {e}")

def execute_query(driver): 
    try:
        xpath = '//a[@href="javascript:executa_consulta()"]'
        executa_link = driver.find_element(By.XPATH, xpath)
        executa_link.click()
    except TimeoutException:
        print("Timeout: Imagem de execução não foi encontrada a tempo.")
    except Exception as e:
        print(f"Erro ao clicar na imagem de execução: {e}")


def get_table_url(driver): 
    try:
        url_default = driver.current_url
        iframe = driver.find_element(By.NAME, 'iframe1')
        driver.switch_to.frame(iframe)
        time.sleep(1)
        try:
            tabela_frame = driver.find_element(By.NAME, 'tabela')
            tabela_url = tabela_frame.get_attribute('src')
        except NoSuchElementException:
            print("Não há dados para essa data.")
            tabela_url = None
        driver.switch_to.default_content()
        assert driver.current_url == url_default, "Não está no contexto padrão."
        if tabela_url:
            time.sleep(2)
            driver.get(tabela_url)
            html = driver.page_source
            pasta_temp = 'temp'
            os.makedirs(pasta_temp, exist_ok=True)     
            with open('temp/tabela.html', 'w', encoding='utf-8') as file:
                file.write(html)
            time.sleep(2)
            driver.get(url_default)
        return tabela_url  
    except Exception as e:
        print(f"Erro ao encontrar ou trocar para o iframe: {e}")



def add_month_data(table_url, state, city, year, month, city_df):
    cod_city = city.split(':')[0]
    name_city = city.split(':')[1]
    if table_url is None:
        print(f"Não há dados para este mês")
        print(f"Adicionando linha vazia")        
        print('-------------------------')
        city_df.loc[len(city_df)] = [state, cod_city, name_city, year, month, 0, 0, 0]
    else:
        with open('temp/tabela.html', 'r', encoding='utf-8') as file:
            html = file.read()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', id='dados')
        data = []
        for row in table.find_all('tr')[3:]:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            data.append(cols)
        columns = ['CBO 2002', 'Salário Médio Adm.', 'Admissão', 'Desligamento', 'Saldo']
        if len(data[0]) == len(columns):
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(f'temp/df_consulta.csv', index=False)
            df = pd.read_csv('temp/df_consulta.csv')
            df.fillna(0, inplace=True)
            df[['Admissão', 'Saldo', 'Desligamento']] = df[['Admissão', 'Saldo', 'Desligamento']].apply(lambda x: x.astype(int))
            sum_admissao = df['Admissão'].sum()
            sum_desligamento = df['Desligamento'].sum()
            sum_saldo = df['Saldo'].sum()
            city_df.loc[len(city_df)] = [state, cod_city, name_city, year, month, sum_admissao, sum_desligamento, sum_saldo]
            print('Dados mensais coletados com sucesso!')
            print('-------------------------')
        else:
            print(f"A tabela coletada não possui a quantidade correta de colunas.")
            print(f"Adicionando linha vazia")
            print('-------------------------')
            city_df.loc[len(city_df)] = [state, cod_city, name_city, year, month, 0, 0, 0]
        return city_df

def is_this_year_valid(driver, year): 
    select_ano_inicio = Select(driver.find_element(By.ID, 'ano_inicio'))
    select_ano_inicio.select_by_visible_text(year)
    select_ano_fim = Select(driver.find_element(By.ID, 'ano_fim'))
    select_ano_fim.select_by_visible_text(year)

    select_mes_inicio = Select(driver.find_element(By.ID, 'mes_inicio_cons'))
    select_mes_fim = Select(driver.find_element(By.ID, 'mes_fim_cons'))
    select_mes_inicio.select_by_value('01')
    select_mes_fim.select_by_value('12')

    execute_query(driver)
    time.sleep(1)
    tabela_url = get_table_url(driver)
    if tabela_url is None:
        return False
    return True

def add_empty_year(city_df, year, state, city):
    for month in MONTHS:
        cod_city = city.split(':')[0]
        name_city = city.split(':')[1]
        city_df.loc[len(city_df)] = [state, cod_city, name_city, year, month, 0, 0, 0]
    return city_df

def save_city_data(state, city, city_df):
    city = city.split(':')[1]
    extract_name = f"{city}.csv"
    folder_path = os.path.join('Dados Coletados', state, city) 
    os.makedirs(folder_path, exist_ok=True)
    city_df.to_csv(os.path.join(folder_path, extract_name), index=False)
    print(f"\n======================== \nArquivo {extract_name} salvo com sucesso.\n =================\n")

def main():
    try:
        state_list = collect_state_list(driver)
        for state in state_list:
            select_state(driver, state)
            city_list = collect_city_list(driver)
            for city in city_list:
                select_state(driver, state)
                columns = ['UF', 'Cod. Municipio','Nome Municipio', 'Ano', 'Mês', 'Admissao', 'Desligamento', 'Saldo']
                city_df = pd.DataFrame(columns=columns)
                select_city(driver, city)
                for year in YEARS:
                    select_state(driver, state)
                    select_city(driver, city)
                    select_radio(driver)
                    time.sleep(1)
                    if not is_this_year_valid(driver, year):
                        print(f"Não há dados para o ano {year} em {state} - {city}")
                        print(f"Adicionando dados vazios para o ano {year} em {state} - {city}")
                        add_empty_year(city_df, year, state, city)
                        continue
                    else:
                        print(f"\nHá dados para o ano {year} em {state} - {city}")
                        print('Iniciando captura de dados...')
                    for month in MONTHS:
                        select_state(driver, state)
                        select_city(driver, city)
                        time.sleep(1)
                        print('\n-------------------------')
                        print(f"Capturando dados de {state} - {city.split(':')[1]} no período de ({month}/{year})")
                        select_radio(driver)
                        time.sleep(1)
                        select_date(driver, year, month)
                        execute_query(driver)
                        time.sleep(1)
                        table_url = get_table_url(driver)
                        add_month_data(table_url, state, city, year, month, city_df)
                save_city_data(state, city, city_df)
    finally:
        driver.quit()

if __name__ == "__main__":
    url = 'https://bi.mte.gov.br/bgcaged/caged_perfil_municipio/index.php'

    #driver_path = '/media/lucas/HD 1TB/Dados_CAGED/utils/chromedriver_linux' #Para sistemas Linux
    driver_path = 'C:\\Users\\Predify\\Documents\\GitHub\\CAGED_Data_Collector\\utils\\chromedriver_windows.exe' #Para sistemas Windows
    
    chrome_service = Service(driver_path)
    driver = webdriver.Chrome(service=chrome_service)
    driver.get(url)
    main()
