import sys
print(f"Python sys.path: {sys.path}")

try:
    from fb2.fb2 import FB2Tree
    print("Successfully imported FB2Tree from fb2.fb2")
except ImportError as e:
    print(f"Failed to import FB2Tree from fb2.fb2: {e}")

# It's possible FB2Tree is part of lxml, as lxml is a dependency for FB2 processing
try:
    from lxml import etree
    # Attempt to parse a dummy FB2 string to see if lxml handles it
    # This is a common way to check if lxml can handle FB2-like structures
    # A real FB2 file would have a more complex structure.
    fb2_minimal_content = """
    <FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">
      <description>
        <title-info>
          <genre>antica</genre>
          <author><first-name>John</first-name><last-name>Doe</last-name></author>
          <book-title>Test Book</book-title>
          <lang>en</lang>
        </title-info>
        <document-info>
          <author><nickname>PyTest</nickname></author>
          <date>2024-05-07</date>
          <version>1.0</version>
        </document-info>
      </description>
    </FictionBook>
    """
    tree = etree.fromstring(fb2_minimal_content.encode('utf-8'))
    if tree.tag == '{http://www.gribuser.ru/xml/fictionbook/2.0}FictionBook':
        print("Successfully parsed dummy FB2 XML with lxml.etree and found FictionBook tag")
        # Further checks could involve looking for FB2Tree or similar classes if lxml wraps them
        # For now, confirming lxml can parse FB2 structure is a good step.
    else:
        print(f"lxml.etree parsed XML, but root tag is not FictionBook: {tree.tag}")

except ImportError as e:
    print(f"Failed to import etree from lxml: {e}")
except Exception as e:
    print(f"An error occurred while trying to parse FB2 with lxml: {e}")

try:
    import fb2
    print("Successfully imported fb2 directly")
except ImportError as e:
    print(f"Failed to import fb2 directly: {e}")
