# Take the data from the API and csv and add distance from train stop
import fetch_mbtaAPI
import fetch_foodanddrink
# For each business, compare their gps location to gps location of train stops




def main():
    fetch_mbtaAPI.main()
    fetch_foodanddrink.main()
    pass

if __name__ == '__main__':
    main()