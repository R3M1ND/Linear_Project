import SearchEngine as sng
import time
if __name__ == "__main__":
    se = sng.SearchEngine("zen_record.txt")

    while True:
        kw = input("Search : ")
        t0 = time.time()
        x = se.search_by_keyword(keyword=kw, return_value ='Quote',number_of_result = 20)
        t1 = time.time()

        for i,data in enumerate(x):
            print(i+1,data.replace(kw,"'"+kw+"'"))
        
        print("Searched in",t1-t0,"seconds")
