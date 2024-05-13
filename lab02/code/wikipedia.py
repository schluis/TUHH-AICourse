from collections import defaultdict
import csv
import math
from copy import deepcopy
import time


class Wikigraph:
    
    def __init__(self):
        links = open('data/enwiki-2013-small.txt').read().strip().split('\n')
        self.hyperlinks = defaultdict(list)
        for link in links:
            a, b = [int(x) for x in link.split()]
            self.hyperlinks[a].append(b)
        
        self.name_to_id = defaultdict()
        self.id_to_name = defaultdict()
        
        with open('data/enwiki-2013-small-names.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                self.name_to_id[row[1]] = int(row[0])
                self.id_to_name[int(row[0])] = row[1]
    
    def get_id(self, page: str):
        return self.name_to_id[page]
    
    def get_name(self, page_id: int):
        return self.id_to_name[page_id]
    
    def get_links(self, page_id: int):
        return self.hyperlinks[page_id]



def length_of_shortest_path(start_page: str, end_page: str, wikigraph: Wikigraph):
    start_id = wikigraph.get_id(start_page)
    end_id = wikigraph.get_id(end_page)
    

    visited = set()
    depth = 2
    length = math.inf
    while length == math.inf:
        depth += 1
        length = recursive_search(start_id, end_id, visited, wikigraph, depth)[0]

def recursive_search(start_id, end_id, visited, wikigraph, max_depth):
    if max_depth == 0:
        return (math.inf, [])

    links_on_page = wikigraph.get_links(start_id)
    for link in links_on_page:
        # print(link)
        if link == end_id:
            print("Found path")
            return (1, [end_id])

        if link not in visited:
            local_visited = deepcopy(visited)
            local_visited.add(link)
            previous = recursive_search(link, end_id, local_visited, wikigraph, max_depth - 1)

            if previous[0] < math.inf:
                return (previous[0] + 1, [link] + previous[1])
    
    return (math.inf, [])

if __name__ == '__main__':
    wg = Wikigraph()

    start_page = "Out of memory"
    end_page = "Solar power in Germany"

    start = time.time()

    print(f"\nLength of shortest path: {length_of_shortest_path(start_page, end_page, wg)[0]}")
    print(f"Needed time: {time.time() - start}\n")

