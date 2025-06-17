try:
    import langchain_pinecone
    print("Successfully imported 'langchain_pinecone'")
    from langchain_pinecone import PineconeVectorStore
    print("Successfully imported 'PineconeVectorStore' from 'langchain_pinecone'")
    print("Test Succeeded")
except ImportError as e:
    print(f"ImportError: {e}")
    print("Test Failed")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("Test Failed")
