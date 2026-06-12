from mcp_server import search_outings

def test():
    print("Calling search_outings directly...")
    result = search_outings("romantic event")
    print(result)

if __name__ == "__main__":
    test()
