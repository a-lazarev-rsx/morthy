try:
    from fb2.fb2 import FB2Tree
    print("Successfully imported FB2Tree from fb2.fb2")
except ImportError as e:
    print(f"Failed to import FB2Tree from fb2.fb2: {e}")
    try:
        import fb2
        print("Successfully imported fb2 directly")
        # If fb2 imports, check if FB2Tree is an attribute or how to access it
        if hasattr(fb2, 'FB2Tree'):
            print("FB2Tree is available under fb2.FB2Tree")
        elif hasattr(fb2, 'fb2') and hasattr(fb2.fb2, 'FB2Tree'):
            print("FB2Tree is available under fb2.fb2.FB2Tree")
        else:
            print("fb2 module imported, but FB2Tree not found directly. Further inspection needed.")
            # Attempt to list attributes of the fb2 module
            print(f"Attributes of fb2 module: {dir(fb2)}")
            if hasattr(fb2, 'fb2'):
                print(f"Attributes of fb2.fb2 module: {dir(fb2.fb2)}")

    except ImportError as ie:
        print(f"Failed to import fb2 directly: {ie}")
