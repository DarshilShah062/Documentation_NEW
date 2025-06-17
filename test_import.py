try:
    import langchain_pinecone
    print("Successfully imported 'langchain_pinecone'")
    try:
        from langchain_pinecone import PineconeVectorStore
    except ImportError:
        from langchain_pinecone import Pinecone as PineconeVectorStore
    print("Successfully imported 'PineconeVectorStore' (alias) from 'langchain_pinecone'")
    print("Test Succeeded")
except ImportError as e:
    print(f"ImportError: {e}")
    print("Test Failed")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("Test Failed")
