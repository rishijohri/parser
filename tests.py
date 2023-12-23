# Python
import re

# Define the SQL query
query = """
SELECT * FROM table; -- This is a comment
WHERE column = 'value'; /* This is another comment */
"""

# Remove comments
query_without_comments = re.sub(r'--.*?$|/\*.*?\*/', '', query, flags=re.MULTILINE|re.DOTALL)

print(query_without_comments)