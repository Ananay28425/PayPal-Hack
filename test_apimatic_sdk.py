from assembly_proof import AssemblyProofClient

client = AssemblyProofClient(
    base_url="http://127.0.0.1:8000"
)

try:
    response = client.search_products_api_products_search_get(
        q="Focusrite Scarlett 2i2",
        limit=5
    )
    print("APIMATIC SDK CALL SUCCESSFUL")
    print(response)
finally:
    client.close()
